import uuid
from datetime import date, timedelta

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import CompletionStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.models.category_score import CategoryScore
from app.models.completion import HabitCompletion
from app.models.habit import Habit
from app.models.narration import Narration
from app.services import ai_master_service, stats_engine


async def record_completion(
    db: AsyncSession,
    habit_id: uuid.UUID,
    user_id: uuid.UUID,
    completion_date: date,
    status: CompletionStatus,
) -> tuple[HabitCompletion, CategoryScore, Narration | None]:
    """Record a completion or skip, update level/vitality, generate narration."""
    habit = await _get_owned_habit(db, habit_id, user_id)

    existing = await _get_existing(db, habit_id, completion_date)
    if existing:
        raise ConflictError("Completion already recorded for this date")

    if status == CompletionStatus.COMPLETED:
        streak = await _calculate_streak(db, habit_id, completion_date)
        xp_earned = stats_engine.completion_xp(streak)
        consecutive_skips = 0
    else:
        streak = 0
        xp_earned = 0.0
        consecutive_skips = await _count_consecutive_skips(db, habit_id, completion_date) + 1

    # Points delta for the completion record (XP earned or 0 for skip)
    completion = HabitCompletion(
        habit_id=habit_id,
        user_id=user_id,
        date=completion_date,
        status=status.value,
        points_delta=round(xp_earned, 2),
    )
    db.add(completion)

    # Update level, XP, and vitality
    score = await _update_score(db, user_id, habit.category, xp_earned, status, streak)

    await db.commit()
    await db.refresh(completion)
    await db.refresh(score)

    # Generate AI Master narration
    narration = await ai_master_service.generate_narration(
        db=db,
        user_id=user_id,
        trigger_type=status.value,
        habit_title=habit.title,
        category=habit.category,
        streak=streak,
        score=score.vitality,
        consecutive_skips=consecutive_skips,
        trigger_ref_id=completion.id,
    )

    return completion, score, narration


async def get_habit_history(
    db: AsyncSession,
    habit_id: uuid.UUID,
    user_id: uuid.UUID,
    limit: int = 30,
    offset: int = 0,
) -> list[HabitCompletion]:
    await _get_owned_habit(db, habit_id, user_id)
    result = await db.execute(
        select(HabitCompletion)
        .where(HabitCompletion.habit_id == habit_id)
        .order_by(HabitCompletion.date.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def _get_owned_habit(db: AsyncSession, habit_id: uuid.UUID, user_id: uuid.UUID) -> Habit:
    result = await db.execute(select(Habit).where(Habit.id == habit_id))
    habit = result.scalar_one_or_none()
    if not habit or habit.user_id != user_id:
        raise NotFoundError("Habit not found")
    return habit


async def _get_existing(db: AsyncSession, habit_id: uuid.UUID, d: date) -> HabitCompletion | None:
    result = await db.execute(
        select(HabitCompletion).where(HabitCompletion.habit_id == habit_id, HabitCompletion.date == d)
    )
    return result.scalar_one_or_none()


async def _calculate_streak(db: AsyncSession, habit_id: uuid.UUID, current_date: date) -> int:
    result = await db.execute(
        select(HabitCompletion.date)
        .where(
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.status == CompletionStatus.COMPLETED,
            HabitCompletion.date < current_date,
        )
        .order_by(HabitCompletion.date.desc())
    )
    dates = [row[0] for row in result.all()]
    streak = 0
    expected = current_date - timedelta(days=1)
    for d in dates:
        if d == expected:
            streak += 1
            expected -= timedelta(days=1)
        else:
            break
    return streak


async def _count_consecutive_skips(db: AsyncSession, habit_id: uuid.UUID, current_date: date) -> int:
    result = await db.execute(
        select(HabitCompletion.date, HabitCompletion.status)
        .where(HabitCompletion.habit_id == habit_id, HabitCompletion.date < current_date)
        .order_by(HabitCompletion.date.desc())
        .limit(30)
    )
    count = 0
    for row in result.all():
        if row[1] == CompletionStatus.SKIPPED:
            count += 1
        else:
            break
    return count


async def _update_score(
    db: AsyncSession,
    user_id: uuid.UUID,
    category: str,
    xp_earned: float,
    status: CompletionStatus,
    streak: int,
) -> CategoryScore:
    result = await db.execute(
        select(CategoryScore).where(
            and_(CategoryScore.user_id == user_id, CategoryScore.category == category)
        )
    )
    score = result.scalar_one()

    if status == CompletionStatus.COMPLETED:
        # Apply XP and level up
        new_xp, new_level, _ = stats_engine.apply_xp(score.xp, score.level, xp_earned)
        score.xp = new_xp
        score.level = new_level
        score.xp_to_next = round(stats_engine.xp_for_level(new_level), 2)

        # Boost vitality
        score.vitality = stats_engine.vitality_on_completion(score.vitality)

        # Update streak
        score.streak_days = streak + 1
        score.longest_streak = max(score.longest_streak, score.streak_days)
    else:
        # Skip: no XP, reduce vitality
        score.vitality = stats_engine.vitality_on_skip(score.vitality)
        score.streak_days = 0

    return score
