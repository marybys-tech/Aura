import uuid
from datetime import date, timedelta

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ScheduleType
from app.models.category_score import CategoryScore
from app.models.completion import HabitCompletion
from app.models.habit import Habit
from app.models.quest import Quest
from app.schemas.completion import CategoryScoreResponse
from app.schemas.dashboard import (
    DashboardHabit,
    MonthDaySummary,
    MonthResponse,
    QuestSummary,
    TodayResponse,
    WeekDayStatus,
    WeekHabitRow,
    WeekResponse,
)


async def get_today(db: AsyncSession, user_id: uuid.UUID, today: date) -> TodayResponse:
    habits = await _get_active_habits(db, user_id)
    due_habits = [h for h in habits if _is_due(h, today)]

    completions = await _get_completions_for_date(db, user_id, today)
    completion_map = {c.habit_id: c for c in completions}

    dashboard_habits = []
    for h in due_habits:
        c = completion_map.get(h.id)
        if c:
            status = c.status
            count = c.completion_count
        else:
            status = "pending"
            count = 0
        dashboard_habits.append(DashboardHabit(
            id=h.id, title=h.title, category=h.category,
            times_per_day=h.times_per_day, completions_today=count, status=status,
        ))

    scores = await _get_scores(db, user_id)
    quests = await _get_active_quests(db, user_id)
    return TodayResponse(date=today, habits=dashboard_habits, scores=scores, active_quests=quests)


async def get_week(db: AsyncSession, user_id: uuid.UUID, ref_date: date) -> WeekResponse:
    monday = ref_date - timedelta(days=ref_date.weekday())
    sunday = monday + timedelta(days=6)
    week_dates = [monday + timedelta(days=i) for i in range(7)]

    habits = await _get_active_habits(db, user_id)
    completions = await _get_completions_range(db, user_id, monday, sunday)
    comp_index: dict[tuple[uuid.UUID, date], str] = {
        (c.habit_id, c.date): c.status for c in completions
    }

    rows = []
    for h in habits:
        days = []
        for d in week_dates:
            if not _is_due(h, d):
                days.append(WeekDayStatus(date=d, status=None))
            elif (h.id, d) in comp_index:
                days.append(WeekDayStatus(date=d, status=comp_index[(h.id, d)]))
            else:
                days.append(WeekDayStatus(date=d, status="pending"))
        rows.append(WeekHabitRow(habit_id=h.id, title=h.title, category=h.category, days=days))

    scores = await _get_scores(db, user_id)
    quests = await _get_active_quests(db, user_id)
    return WeekResponse(start_date=monday, end_date=sunday, habits=rows, scores=scores, active_quests=quests)


async def get_month(db: AsyncSession, user_id: uuid.UUID, ref_date: date) -> MonthResponse:
    first_day = ref_date.replace(day=1)
    if ref_date.month == 12:
        last_day = ref_date.replace(year=ref_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = ref_date.replace(month=ref_date.month + 1, day=1) - timedelta(days=1)

    habits = await _get_active_habits(db, user_id)
    completions = await _get_completions_range(db, user_id, first_day, last_day)
    comp_by_date: dict[date, int] = {}
    for c in completions:
        if c.status == "completed":
            comp_by_date[c.date] = comp_by_date.get(c.date, 0) + 1

    days = []
    d = first_day
    while d <= last_day:
        due_count = sum(1 for h in habits if _is_due(h, d))
        completed = comp_by_date.get(d, 0)
        days.append(MonthDaySummary(date=d, completed=completed, total=due_count))
        d += timedelta(days=1)

    scores = await _get_scores(db, user_id)
    quests = await _get_active_quests(db, user_id)
    return MonthResponse(month=ref_date.month, year=ref_date.year, days=days, scores=scores, active_quests=quests)


def _is_due(habit: Habit, d: date) -> bool:
    if habit.schedule_type == ScheduleType.DAILY or habit.schedule_type == ScheduleType.MULTIPLE_DAILY:
        return True
    if habit.schedule_type == ScheduleType.SPECIFIC_DAYS and habit.schedule_days:
        return d.isoweekday() in habit.schedule_days
    return True


async def _get_active_habits(db: AsyncSession, user_id: uuid.UUID) -> list[Habit]:
    result = await db.execute(
        select(Habit).where(Habit.user_id == user_id, Habit.is_active == True)  # noqa: E712
    )
    return list(result.scalars().all())


async def _get_completions_for_date(db: AsyncSession, user_id: uuid.UUID, d: date) -> list[HabitCompletion]:
    result = await db.execute(
        select(HabitCompletion).where(HabitCompletion.user_id == user_id, HabitCompletion.date == d)
    )
    return list(result.scalars().all())


async def _get_completions_range(
    db: AsyncSession, user_id: uuid.UUID, start: date, end: date
) -> list[HabitCompletion]:
    result = await db.execute(
        select(HabitCompletion).where(
            and_(
                HabitCompletion.user_id == user_id,
                HabitCompletion.date >= start,
                HabitCompletion.date <= end,
            )
        )
    )
    return list(result.scalars().all())


async def _get_scores(db: AsyncSession, user_id: uuid.UUID) -> dict[str, CategoryScoreResponse]:
    result = await db.execute(select(CategoryScore).where(CategoryScore.user_id == user_id))
    return {s.category: CategoryScoreResponse.model_validate(s) for s in result.scalars().all()}


async def _get_active_quests(db: AsyncSession, user_id: uuid.UUID) -> list[QuestSummary]:
    result = await db.execute(
        select(Quest).where(Quest.user_id == user_id, Quest.status == "active")
    )
    return [QuestSummary.model_validate(q) for q in result.scalars().all()]
