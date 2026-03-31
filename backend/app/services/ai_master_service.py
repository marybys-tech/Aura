"""AI Master — narration and quest generation via Bedrock."""

import json
import logging
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


async def generate_quest_data(
    target_category: str,
    habits: list[str],
    quest_type: str,
    vitality: float,
) -> dict | None:
    """Generate quest creative content via AI for a specific category."""
    import random

    points = round(random.uniform(3.0, 8.0) if quest_type == "daily" else random.uniform(10.0, 20.0), 1)
    criteria_types = ["complete_n_habits", "any_completion", "maintain_streak", "total_completions"]
    criteria_type = random.choice(criteria_types)

    prompt = (
        f"Create a {quest_type} quest for the category '{target_category}'.\n"
        f"The student's {target_category} vitality is {vitality}/100.\n"
        f"Their habits include: {', '.join(habits[:5])}\n\n"
        f"Give it a creative, evocative title (like 'The Scholar's Trial' or 'Path of Iron Will').\n"
        f"Write a 1-2 sentence description in wise mentor voice (Master Oogway style).\n\n"
        "Return JSON only:\n"
        '{"title": "string", "description": "string"}'
    )

    system = "You are Master Aura, a wise mentor. Return valid JSON only, nothing else."

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

    # Build criteria in code (reliable, not AI)
    if criteria_type == "complete_n_habits":
        count = random.choice([1, 2, 3])
        criteria = {"type": "complete_n_habits", "category": target_category, "count": count, "within": "day" if quest_type == "daily" else "week"}
    elif criteria_type == "maintain_streak":
        days = random.choice([3, 5, 7]) if quest_type == "weekly" else 2
        criteria = {"type": "maintain_streak", "category": target_category, "days": days}
    elif criteria_type == "any_completion":
        criteria = {"type": "any_completion", "category": target_category}
    else:
        count = random.choice([3, 5, 7])
        criteria = {"type": "total_completions", "count": count, "within": "day" if quest_type == "daily" else "week"}

    return {
        "quest_type": quest_type,
        "title": ai_data.get("title", f"The {target_category.title()} Path"),
        "description": ai_data.get("description", f"Strengthen your {target_category} today."),
        "target_category": target_category,
        "bonus_points": points,
        "criteria": criteria,
    }
