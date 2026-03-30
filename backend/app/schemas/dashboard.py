import uuid
from datetime import date

from pydantic import BaseModel

from app.schemas.completion import CategoryScoreResponse


class DashboardHabit(BaseModel):
    id: uuid.UUID
    title: str
    category: str
    times_per_day: int
    completions_today: int
    status: str  # "pending", "completed", "skipped"

    model_config = {"from_attributes": True}


class QuestSummary(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    target_category: str
    bonus_points: float
    quest_type: str
    status: str

    model_config = {"from_attributes": True}


class TodayResponse(BaseModel):
    date: date
    habits: list[DashboardHabit]
    scores: dict[str, CategoryScoreResponse]
    active_quests: list[QuestSummary]


class WeekDayStatus(BaseModel):
    date: date
    status: str | None  # "completed", "skipped", None (not scheduled), "pending"


class WeekHabitRow(BaseModel):
    habit_id: uuid.UUID
    title: str
    category: str
    days: list[WeekDayStatus]


class WeekResponse(BaseModel):
    start_date: date
    end_date: date
    habits: list[WeekHabitRow]
    scores: dict[str, CategoryScoreResponse]
    active_quests: list[QuestSummary]


class MonthDaySummary(BaseModel):
    date: date
    completed: int
    total: int


class MonthResponse(BaseModel):
    month: int
    year: int
    days: list[MonthDaySummary]
    scores: dict[str, CategoryScoreResponse]
    active_quests: list[QuestSummary]
