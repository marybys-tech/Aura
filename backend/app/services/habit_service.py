import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ScheduleType
from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.habit import Habit
from app.schemas.habit import HabitCreateRequest, HabitUpdateRequest


async def create_habit(db: AsyncSession, user_id: uuid.UUID, data: HabitCreateRequest) -> Habit:
    _validate_schedule(data)
    habit = Habit(user_id=user_id, **data.model_dump())
    db.add(habit)
    await db.commit()
    await db.refresh(habit)
    return habit


async def list_habits(
    db: AsyncSession,
    user_id: uuid.UUID,
    category: str | None = None,
    is_active: bool | None = True,
) -> list[Habit]:
    q = select(Habit).where(Habit.user_id == user_id)
    if category:
        q = q.where(Habit.category == category)
    if is_active is not None:
        q = q.where(Habit.is_active == is_active)
    q = q.order_by(Habit.created_at.desc())
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_habit(db: AsyncSession, habit_id: uuid.UUID, user_id: uuid.UUID) -> Habit:
    result = await db.execute(select(Habit).where(Habit.id == habit_id))
    habit = result.scalar_one_or_none()
    if not habit:
        raise NotFoundError("Habit not found")
    if habit.user_id != user_id:
        raise ForbiddenError("Not your habit")
    return habit


async def update_habit(db: AsyncSession, habit_id: uuid.UUID, user_id: uuid.UUID, data: HabitUpdateRequest) -> Habit:
    habit = await get_habit(db, habit_id, user_id)
    updates = data.model_dump(exclude_unset=True)
    for k, v in updates.items():
        setattr(habit, k, v)
    await db.commit()
    await db.refresh(habit)
    return habit


async def delete_habit(db: AsyncSession, habit_id: uuid.UUID, user_id: uuid.UUID) -> Habit:
    """Soft-delete by setting is_active=False."""
    habit = await get_habit(db, habit_id, user_id)
    habit.is_active = False
    await db.commit()
    await db.refresh(habit)
    return habit


def _validate_schedule(data: HabitCreateRequest) -> None:
    if data.schedule_type == ScheduleType.SPECIFIC_DAYS:
        if not data.schedule_days:
            raise ValueError("schedule_days required for specific_days schedule")
        if not all(1 <= d <= 7 for d in data.schedule_days):
            raise ValueError("schedule_days must be ISO weekdays 1-7")
    if data.schedule_type == ScheduleType.MULTIPLE_DAILY and data.times_per_day < 2:
        raise ValueError("times_per_day must be >= 2 for multiple_daily schedule")
