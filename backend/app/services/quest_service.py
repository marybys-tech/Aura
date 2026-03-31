import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import QuestStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.models.category_score import CategoryScore
from app.models.quest import Quest
from app.services import stats_engine
from app.services.stats_engine import apply_xp, vitality_on_completion, xp_for_level


async def get_quests(db: AsyncSession, user_id: uuid.UUID) -> list[Quest]:
    """Return active + recently completed/expired quests."""
    result = await db.execute(
        select(Quest)
        .where(Quest.user_id == user_id)
        .order_by(Quest.created_at.desc())
        .limit(10)
    )
    return list(result.scalars().all())


async def create_quest(db: AsyncSession, user_id: uuid.UUID, quest_data: dict) -> Quest:
    """Create a quest from AI-generated data."""
    quest = Quest(
        user_id=user_id,
        quest_type=quest_data["quest_type"],
        title=quest_data["title"],
        description=quest_data["description"],
        target_category=quest_data["target_category"],
        criteria_json=quest_data["criteria"],
        bonus_points=quest_data["bonus_points"],
        issued_date=date.today(),
        expires_at=_quest_expiry(quest_data["quest_type"]),
    )
    db.add(quest)
    await db.commit()
    await db.refresh(quest)
    return quest


async def claim_quest(db: AsyncSession, quest_id: uuid.UUID, user_id: uuid.UUID) -> Quest:
    """Claim a completed quest and award bonus points."""
    result = await db.execute(select(Quest).where(Quest.id == quest_id))
    quest = result.scalar_one_or_none()
    if not quest or quest.user_id != user_id:
        raise NotFoundError("Quest not found")
    if quest.status != QuestStatus.ACTIVE:
        raise ConflictError(f"Quest is {quest.status}, not active")

    quest.status = QuestStatus.COMPLETED
    quest.completed_at = datetime.now(UTC)

    score_result = await db.execute(
        select(CategoryScore).where(
            and_(CategoryScore.user_id == user_id, CategoryScore.category == quest.target_category)
        )
    )
    score = score_result.scalar_one()
    # Quest reward: XP + vitality boost
    new_xp, new_level, _ = stats_engine.apply_xp(score.xp, score.level, quest.bonus_points)
    score.xp = new_xp
    score.level = new_level
    score.xp_to_next = round(stats_engine.xp_for_level(new_level), 2)
    score.vitality = stats_engine.vitality_on_completion(score.vitality)

    await db.commit()
    await db.refresh(quest)
    return quest


async def expire_old_quests(db: AsyncSession) -> int:
    """Mark expired active quests. Returns count of expired."""
    now = datetime.now(UTC)
    result = await db.execute(
        select(Quest).where(Quest.status == QuestStatus.ACTIVE, Quest.expires_at < now)
    )
    quests = list(result.scalars().all())
    for q in quests:
        q.status = QuestStatus.EXPIRED
    await db.commit()
    return len(quests)


def _quest_expiry(quest_type: str) -> datetime:
    if quest_type == "weekly":
        return datetime.now(UTC) + timedelta(days=7)
    return datetime.now(UTC) + timedelta(days=1)
