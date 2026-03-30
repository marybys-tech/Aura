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

FALLBACK_QUOTES = [
    "The bamboo that bends is stronger than the oak that resists.",
    "A journey of a thousand miles begins with a single step.",
    "The river does not drink its own water. Growth comes from what you give.",
    "Yesterday is history, tomorrow is a mystery. Today is a gift.",
    "Even the tallest mountain began as a grain of sand with ambition.",
    "Patience is not the ability to wait, but how you act while waiting.",
    "The seed does not see the sun, yet it grows toward the light.",
]


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
) -> Narration:
    """Generate an AI narration for a completion or skip event."""
    if trigger_type == "completion":
        prompt = (
            f'Event: habit_completed\nHabit: "{habit_title}" (category: {category})\n'
            f"Streak: {streak} days\nCategory score: {score}/100\n"
            "Respond with ONLY the narration text."
        )
    else:
        prompt = (
            f'Event: habit_skipped\nHabit: "{habit_title}" (category: {category})\n'
            f"Consecutive skips: {consecutive_skips}\nCategory score: {score}/100\n"
            "Respond with ONLY the narration text. Be gentle and motivating."
        )

    content = await bedrock_client.invoke_model(prompt, system=SYSTEM_PROMPT, max_tokens=150)
    if not content:
        content = random.choice(FALLBACK_QUOTES)

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


async def generate_quest_data(scores: dict[str, float], habits: list[str], quest_type: str) -> dict | None:
    """Generate quest via AI. Returns parsed dict or None on failure."""
    sorted_scores = sorted(scores.items(), key=lambda x: x[1])
    weakest = sorted_scores[0] if sorted_scores else ("intelligence", 0)
    strongest = sorted_scores[-1] if sorted_scores else ("intelligence", 0)

    points_range = "3.0-8.0" if quest_type == "daily" else "10.0-20.0"

    prompt = (
        f"Generate a {quest_type} quest for this student.\n\n"
        f"Student profile:\n- Scores: {json.dumps(scores)}\n"
        f"- Weakest category: {weakest[0]} ({weakest[1]})\n"
        f"- Strongest category: {strongest[0]} ({strongest[1]})\n"
        f"- Active habits: {', '.join(habits)}\n\n"
        f"Rules:\n- Target the student's weakest or second-weakest category\n"
        f"- Bonus points between {points_range}\n\n"
        "Return JSON only:\n"
        '{"title": "string", "description": "string", "target_category": "string", '
        '"bonus_points": number, "criteria": {"type": "complete_n_habits", "category": "string", "count": number, "within": "day|week"}}'
    )

    system = (
        "You are Master Aura, designing training challenges. "
        "Return valid JSON only, nothing else."
    )

    result = await bedrock_client.invoke_model(
        prompt,
        system=system,
        model_id=settings.BEDROCK_QUEST_MODEL,
        max_tokens=300,
        temperature=0.5,
    )
    if not result:
        return None

    try:
        data = json.loads(result)
        data["quest_type"] = quest_type
        return data
    except (json.JSONDecodeError, KeyError):
        logger.warning("Failed to parse quest JSON: %s", result)
        return None
