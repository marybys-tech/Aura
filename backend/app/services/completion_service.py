import uuid
from datetime import date, timedelta

from sqlalchemy import and_, func, select
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
    """Record a completion or skip, update score, generate narration, return all three."""
    habit = await _get_owned_habit(db, habit_id, user_id)

    existing = await _get_existing(db, habit_id, completion_date)
    if existing:
        raise ConflictError("Completion already recorded for this date")

    if status == CompletionStatus.COMPLETED:
        streak = await _calculate_streak(db, habit_id, completion_date)
        points = stats_engine.completion_points(streak)
        consecutive_skips = 0
    else:
        streak = 0
        consecutive_skips = await _count_consecutive_skips(db, habit_id, completion_date) + 1
        points = stats_engine.skip_penalty(consecutive_skips)

    completion = HabitCompletion(
        habit_id=habit_id,
        user_id=user_id,
        date=completion_date,
        status=status.value,
        points_delta=round(points, 2),
    )
    db.add(completion)

    score = await _update_score(db, user_id, habit.category, points, status)

    await db.commit()
    await db.refresh(completion)
    await db.refresh(score)

    # Generate AI Master narration (non-blocking — if Bedrock fails, returns fallback)
    narration = await ai_master_service.generate_narration(
        db=db,
        user_id=user_id,
        trigger_type=status.value,
        habit_title=habit.title,
        category=habit.category,
        streak=streak,
        score=score.score,
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
    """Count consecutive completed days before current_date."""
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
    """Count consecutive skipped days before current_date."""
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
    points: float,
    status: CompletionStatus,
) -> CategoryScore:
    result = await db.execute(
        select(CategoryScore).where(
            and_(CategoryScore.user_id == user_id, CategoryScore.category == category)
        )
    )
    score = result.scalar_one()
    score.score = stats_engine.clamp_score(score.score + points)

    if status == CompletionStatus.COMPLETED:
        score.streak_days += 1
        score.longest_streak = max(score.longest_streak, score.streak_days)
    else:
        score.streak_days = 0

    return score
