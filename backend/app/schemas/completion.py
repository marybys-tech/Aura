import uuid
from datetime import date

from pydantic import BaseModel


class CompletionRequest(BaseModel):
    date: date


class CompletionResponse(BaseModel):
    id: uuid.UUID
    habit_id: uuid.UUID
    date: date
    status: str
    completion_count: int
    points_delta: float

    model_config = {"from_attributes": True}


class CompletionWithScoreResponse(BaseModel):
    completion: CompletionResponse
    updated_score: "CategoryScoreResponse"
    narration: "NarrationResponse | None" = None


class CategoryScoreResponse(BaseModel):
    category: str
    level: int
    xp: float
    xp_to_next: float
    vitality: float
    streak_days: int
    longest_streak: int

    model_config = {"from_attributes": True}


class NarrationResponse(BaseModel):
    id: uuid.UUID
    content: str

    model_config = {"from_attributes": True}
