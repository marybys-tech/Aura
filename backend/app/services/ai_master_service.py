"""AI Master — narration and quest generation via Bedrock."""

import json
import logging
import random
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.integrations import bedrock_client
from app.models.narration import Narration

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are Master Aura, a wise and gently humorous mentor in the spirit of "
    "Master Oogway from Kung Fu Panda. You speak in short, memorable aphorisms. "
    "You reference the user's journey of self-improvement through nature metaphors "
    "and occasional playful humor. Max 2 sentences. Never reference the app directly."
)


async def generate_narration(
    db: AsyncSession,
    user_id: uuid.UUID,
    trigger_type: str,
    habit_title: str,
    category: str,
    streak: int,
    score: float,
    consecutive_skips: int = 0,
    trigger_ref_id: uuid.UUID | None = None,
) -> Narration | None:
    """Generate an AI narration. Returns None if Bedrock fails."""
    if trigger_type == "completion":
        prompt = (
            f'Event: habit_completed\nHabit: "{habit_title}" (category: {category})\n'
            f"Streak: {streak} days\nCategory vitality: {score}/100\n"
            "Respond with ONLY the narration text."
        )
    else:
        prompt = (
            f'Event: habit_skipped\nHabit: "{habit_title}" (category: {category})\n'
            f"Consecutive skips: {consecutive_skips}\nCategory vitality: {score}/100\n"
            "Respond with ONLY the narration text. Be gentle and motivating."
        )

    content = await bedrock_client.invoke_model(prompt, system=SYSTEM_PROMPT, max_tokens=150)
    if not content:
        logger.error("Bedrock narration failed for user %s, habit '%s'", user_id, habit_title)
        return None

    narration = Narration(
        user_id=user_id,
        trigger_type=trigger_type,
        trigger_ref_id=trigger_ref_id,
        content=content.strip(),
    )
    db.add(narration)
    await db.commit()
    await db.refresh(narration)
    return narration


# --- Quest Generation ---

# Quest templates — each defines criteria + a prompt hint for the AI
QUEST_TEMPLATES = [
    {
        "id": "complete_one",
        "criteria_fn": lambda cat, _qt: {"type": "any_completion", "category": cat},
        "target": 1,
        "points": (4.0, 6.0),
        "hint": "Complete at least one {category} habit today",
    },
    {
        "id": "complete_two",
        "criteria_fn": lambda cat, _qt: {"type": "complete_n_habits", "category": cat, "count": 2, "within": "day"},
        "target": 2,
        "points": (5.0, 8.0),
        "hint": "Complete 2 {category} habits in one day",
    },
    {
        "id": "complete_three",
        "criteria_fn": lambda cat, _qt: {"type": "complete_n_habits", "category": cat, "count": 3, "within": "day"},
        "target": 3,
        "points": (6.0, 8.0),
        "hint": "Complete 3 {category} habits in one day",
    },
    {
        "id": "streak_three",
        "criteria_fn": lambda cat, _qt: {"type": "maintain_streak", "category": cat, "days": 3},
        "target": 3,
        "points": (8.0, 12.0),
        "hint": "Build a 3-day streak in {category}",
    },
    {
        "id": "streak_five",
        "criteria_fn": lambda cat, _qt: {"type": "maintain_streak", "category": cat, "days": 5},
        "target": 5,
        "points": (12.0, 18.0),
        "hint": "Maintain a 5-day streak in {category}",
    },
    {
        "id": "total_five",
        "criteria_fn": lambda _cat, _qt: {"type": "total_completions", "count": 5, "within": "day"},
        "target": 5,
        "points": (5.0, 8.0),
        "hint": "Complete any 5 habits today across all categories",
    },
]


async def generate_quest_data(
    target_category: str,
    habits: list[str],
    quest_type: str,
    vitality: float,
) -> dict | None:
    """Generate a quest: pick template, then ask AI for creative title + description."""

    # Pick a template appropriate for vitality level
    if vitality < 20:
        # Low vitality — easy quest to get them back
        templates = [t for t in QUEST_TEMPLATES if t["id"] in ("complete_one", "total_five")]
    elif vitality < 50:
        templates = [t for t in QUEST_TEMPLATES if t["id"] in ("complete_one", "complete_two", "streak_three")]
    else:
        # High vitality — challenge them
        templates = [t for t in QUEST_TEMPLATES if t["id"] in ("complete_two", "complete_three", "streak_three", "streak_five")]

    template = random.choice(templates)
    criteria = template["criteria_fn"](target_category, quest_type)
    points = round(random.uniform(*template["points"]), 1)
    challenge = template["hint"].format(category=target_category)

    # Ask AI only for the creative wrapper
    prompt = (
        f"Create a quest title and description for this challenge:\n"
        f"Category: {target_category}\n"
        f"Challenge: {challenge}\n"
        f"The student's {target_category} vitality is {vitality}/100.\n"
        f"Their habits include: {', '.join(habits[:5])}\n\n"
        f"Requirements:\n"
        f"- Title: creative, thematic, 3-5 words (like 'The Scholar's Trial', 'Rise of the Phoenix', 'Iron Will Awakens')\n"
        f"- Description: 1-2 sentences, wise mentor voice, must reference the actual challenge ({challenge})\n\n"
        "Return JSON only:\n"
        '{"title": "string", "description": "string"}'
    )

    system = "You are Master Aura, a wise mentor designing training challenges. Return valid JSON only."

    result = await bedrock_client.invoke_model(
        prompt, system=system, model_id=settings.BEDROCK_QUEST_MODEL,
        max_tokens=200, temperature=0.8,
    )
    if not result:
        logger.error("Bedrock quest generation failed for category=%s", target_category)
        return None

    try:
        ai_data = json.loads(result)
    except (json.JSONDecodeError, KeyError):
        logger.error("Failed to parse quest JSON: %s", result)
        return None

    return {
        "quest_type": quest_type,
        "title": ai_data.get("title", f"The {target_category.title()} Path"),
        "description": ai_data.get("description", challenge),
        "target_category": target_category,
        "bonus_points": points,
        "criteria": criteria,
    }
