"""Quest service — auto-generation, progress tracking, claiming."""

import uuid
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import QuestStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.models.category_score import CategoryScore
from app.models.completion import HabitCompletion
from app.models.habit import Habit
from app.models.quest import Quest
from app.schemas.dashboard import QuestSummary
from app.services import ai_master_service
from app.services.stats_engine import apply_xp, vitality_on_completion, xp_for_level


# --- Public API ---

async def get_quests(db: AsyncSession, user_id: uuid.UUID) -> list[Quest]:
    result = await db.execute(
        select(Quest).where(Quest.user_id == user_id).order_by(Quest.created_at.desc()).limit(10)
    )
    return list(result.scalars().all())


async def create_quest(db: AsyncSession, user_id: uuid.UUID, quest_data: dict) -> Quest:
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
    result = await db.execute(select(Quest).where(Quest.id == quest_id))
    quest = result.scalar_one_or_none()
    if not quest or quest.user_id != user_id:
        raise NotFoundError("Quest not found")
    if quest.status not in (QuestStatus.ACTIVE, "ready_to_claim"):
        raise ConflictError(f"Quest is {quest.status}, cannot claim")

    quest.status = QuestStatus.COMPLETED
    quest.completed_at = datetime.now(UTC)

    score_result = await db.execute(
        select(CategoryScore).where(
            and_(CategoryScore.user_id == user_id, CategoryScore.category == quest.target_category)
        )
    )
    score = score_result.scalar_one()
    new_xp, new_level, _ = apply_xp(score.xp, score.level, quest.bonus_points)
    score.xp = new_xp
    score.level = new_level
    score.xp_to_next = round(xp_for_level(new_level), 2)
    score.vitality = vitality_on_completion(score.vitality)

    await db.commit()
    await db.refresh(quest)
    return quest


# --- Auto-generation (called on dashboard load) ---

MAX_ACTIVE_QUESTS = 3

async def auto_generate_quests(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Check if user needs new quests, generate if so. Max 3 active."""
    # Expire old quests first
    await _expire_old(db, user_id)

    active = await _count_active(db, user_id)
    if active >= MAX_ACTIVE_QUESTS:
        return

    # Get user context
    scores = await _get_user_scores(db, user_id)
    habits = await _get_habit_titles(db, user_id)
    if not habits:
        return  # no habits = no quests

    active_types = await _get_active_quest_types(db, user_id)
    today = date.today()

    # 1. Daily challenge
    if "daily" not in active_types and active < MAX_ACTIVE_QUESTS:
        quest = _build_daily_quest(scores, habits)
        if quest:
            await create_quest(db, user_id, quest)
            active += 1

    # 2. Weekly mission (Monday)
    if today.weekday() == 0 and "weekly" not in active_types and active < MAX_ACTIVE_QUESTS:
        quest = _build_weekly_quest(scores, habits)
        if quest:
            await create_quest(db, user_id, quest)
            active += 1

    # 3. Comeback quest (any vitality < 15)
    if active < MAX_ACTIVE_QUESTS:
        low_cat = next((cat for cat, s in scores.items() if s["vitality"] < 15 and s["vitality"] > 0), None)
        if low_cat and not await _has_quest_for_category(db, user_id, low_cat):
            quest = _build_comeback_quest(low_cat, scores)
            if quest:
                await create_quest(db, user_id, quest)


# --- Progress checking (called after each completion) ---

async def check_quest_progress(db: AsyncSession, user_id: uuid.UUID, category: str) -> None:
    """Check all active quests and update status if criteria met."""
    result = await db.execute(
        select(Quest).where(Quest.user_id == user_id, Quest.status.in_(["active", QuestStatus.ACTIVE]))
    )
    quests = list(result.scalars().all())

    for quest in quests:
        met = await _evaluate_criteria(db, user_id, quest)
        if met and quest.status != "ready_to_claim":
            quest.status = "ready_to_claim"

    await db.commit()


async def build_quest_summaries(db: AsyncSession, user_id: uuid.UUID, quests: list[Quest]) -> list[QuestSummary]:
    """Build rich QuestSummary with progress info. Auto-marks claimable if criteria met."""
    summaries = []
    now = datetime.now(UTC)
    dirty = False

    for q in quests:
        if q.status in ("completed", "expired"):
            continue

        progress_current, progress_target = await _get_progress(db, user_id, q)

        # Auto-mark as claimable if progress is complete
        if progress_current >= progress_target and q.status == "active":
            q.status = "ready_to_claim"
            dirty = True

        is_claimable = q.status == "ready_to_claim"
        expires_in = max(0, int((q.expires_at - now).total_seconds() / 3600)) if q.expires_at else None

        summaries.append(QuestSummary(
            id=q.id,
            title=q.title,
            description=q.description,
            target_category=q.target_category,
            bonus_points=q.bonus_points,
            quest_type=q.quest_type,
            status=q.status,
            progress_current=progress_current,
            progress_target=progress_target,
            is_claimable=is_claimable,
            expires_in_hours=expires_in,
        ))

    if dirty:
        await db.commit()

    return summaries


# --- Criteria evaluation ---

async def _evaluate_criteria(db: AsyncSession, user_id: uuid.UUID, quest: Quest) -> bool:
    criteria = quest.criteria_json
    ctype = criteria.get("type", "")

    if ctype == "complete_n_habits":
        count = await _count_completions(db, user_id, criteria.get("category"), criteria.get("within", "day"))
        return count >= criteria.get("count", 1)

    if ctype == "maintain_streak":
        score = await _get_category_score(db, user_id, criteria.get("category", quest.target_category))
        return score.streak_days >= criteria.get("days", 3) if score else False

    if ctype == "any_completion":
        count = await _count_completions(db, user_id, criteria.get("category", quest.target_category), "day")
        return count >= 1

    if ctype == "total_completions":
        count = await _count_completions(db, user_id, None, criteria.get("within", "week"))
        return count >= criteria.get("count", 5)

    return False


async def _get_progress(db: AsyncSession, user_id: uuid.UUID, quest: Quest) -> tuple[int, int]:
    """Return (current, target) for progress display."""
    criteria = quest.criteria_json
    ctype = criteria.get("type", "")

    if ctype == "complete_n_habits":
        current = await _count_completions(db, user_id, criteria.get("category"), criteria.get("within", "day"))
        return min(current, criteria["count"]), criteria["count"]

    if ctype == "maintain_streak":
        score = await _get_category_score(db, user_id, criteria.get("category", quest.target_category))
        days = score.streak_days if score else 0
        target = criteria.get("days", 3)
        return min(days, target), target

    if ctype == "any_completion":
        current = await _count_completions(db, user_id, criteria.get("category", quest.target_category), "day")
        return min(current, 1), 1

    if ctype == "total_completions":
        current = await _count_completions(db, user_id, None, criteria.get("within", "week"))
        target = criteria.get("count", 5)
        return min(current, target), target

    return 0, 1


# --- Quest builders (local, no AI needed for speed) ---

def _build_daily_quest(scores: dict, habits: list[str]) -> dict | None:
    weakest = min(scores.items(), key=lambda x: x[1]["vitality"])
    cat = weakest[0]
    count = min(2, max(1, sum(1 for _ in habits) // 3))
    return {
        "quest_type": "daily",
        "title": f"The {cat.title()} Path",
        "description": f"Complete {count} {cat} habit{'s' if count > 1 else ''} today to strengthen your {cat}.",
        "target_category": cat,
        "bonus_points": round(3 + count * 2, 1),
        "criteria": {"type": "complete_n_habits", "category": cat, "count": count, "within": "day"},
    }


def _build_weekly_quest(scores: dict, habits: list[str]) -> dict | None:
    weakest = min(scores.items(), key=lambda x: x[1]["vitality"])
    cat = weakest[0]
    return {
        "quest_type": "weekly",
        "title": f"The Week of {cat.title()}",
        "description": f"Build a 5-day streak in {cat} this week. Consistency is the key to mastery.",
        "target_category": cat,
        "bonus_points": 15.0,
        "criteria": {"type": "maintain_streak", "category": cat, "days": 5},
    }


def _build_comeback_quest(category: str, scores: dict) -> dict | None:
    return {
        "quest_type": "daily",
        "title": f"Reawaken {category.title()}",
        "description": f"Your {category} is fading. Complete just one habit to bring it back to life.",
        "target_category": category,
        "bonus_points": 8.0,
        "criteria": {"type": "any_completion", "category": category},
    }


# --- Helpers ---

async def _count_completions(db: AsyncSession, user_id: uuid.UUID, category: str | None, within: str) -> int:
    today = date.today()
    q = select(func.count()).select_from(HabitCompletion).where(
        HabitCompletion.user_id == user_id,
        HabitCompletion.status == "completed",
    )
    if category:
        q = q.join(Habit).where(Habit.category == category)
    if within == "day":
        q = q.where(HabitCompletion.date == today)
    elif within == "week":
        monday = today - timedelta(days=today.weekday())
        q = q.where(HabitCompletion.date >= monday)
    result = await db.execute(q)
    return result.scalar() or 0


async def _get_category_score(db: AsyncSession, user_id: uuid.UUID, category: str) -> CategoryScore | None:
    result = await db.execute(
        select(CategoryScore).where(
            and_(CategoryScore.user_id == user_id, CategoryScore.category == category)
        )
    )
    return result.scalar_one_or_none()


async def _get_user_scores(db: AsyncSession, user_id: uuid.UUID) -> dict:
    result = await db.execute(select(CategoryScore).where(CategoryScore.user_id == user_id))
    return {s.category: {"level": s.level, "vitality": s.vitality, "streak": s.streak_days} for s in result.scalars().all()}


async def _get_habit_titles(db: AsyncSession, user_id: uuid.UUID) -> list[str]:
    result = await db.execute(
        select(Habit.title).where(Habit.user_id == user_id, Habit.is_active == True)  # noqa: E712
    )
    return [r[0] for r in result.all()]


async def _count_active(db: AsyncSession, user_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count()).select_from(Quest).where(
            Quest.user_id == user_id, Quest.status.in_(["active", "ready_to_claim"])
        )
    )
    return result.scalar() or 0


async def _get_active_quest_types(db: AsyncSession, user_id: uuid.UUID) -> set[str]:
    result = await db.execute(
        select(Quest.quest_type).where(
            Quest.user_id == user_id, Quest.status.in_(["active", "ready_to_claim"])
        )
    )
    return {r[0] for r in result.all()}


async def _has_quest_for_category(db: AsyncSession, user_id: uuid.UUID, category: str) -> bool:
    result = await db.execute(
        select(func.count()).select_from(Quest).where(
            Quest.user_id == user_id,
            Quest.target_category == category,
            Quest.status.in_(["active", "ready_to_claim"]),
        )
    )
    return (result.scalar() or 0) > 0


async def _expire_old(db: AsyncSession, user_id: uuid.UUID) -> None:
    now = datetime.now(UTC)
    result = await db.execute(
        select(Quest).where(Quest.user_id == user_id, Quest.status == "active", Quest.expires_at < now)
    )
    for q in result.scalars().all():
        q.status = QuestStatus.EXPIRED
    await db.commit()


def _quest_expiry(quest_type: str) -> datetime:
    if quest_type == "weekly":
        return datetime.now(UTC) + timedelta(days=7)
    return datetime.now(UTC) + timedelta(days=1)
