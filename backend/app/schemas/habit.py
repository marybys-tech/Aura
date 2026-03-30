import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.core.constants import Category, ScheduleType


class HabitCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str | None = Field(None, max_length=500)
    category: Category
    schedule_type: ScheduleType
    schedule_days: list[int] | None = Field(None, description="ISO weekdays 1-7")
    times_per_day: int = Field(1, ge=1, le=10)


class HabitUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=150)
    description: str | None = Field(None, max_length=500)
    category: Category | None = None
    schedule_type: ScheduleType | None = None
    schedule_days: list[int] | None = None
    times_per_day: int | None = Field(None, ge=1, le=10)


class HabitResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    category: str
    schedule_type: str
    schedule_days: list[int] | None
    times_per_day: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
