import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str
    avatar_url: str | None
    oauth_provider: str
    timezone: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserScoreSummary(BaseModel):
    level: int
    vitality: float

class UserWithScoresResponse(UserResponse):
    scores: dict[str, UserScoreSummary] = Field(default_factory=dict)


class UserUpdateRequest(BaseModel):
    display_name: str | None = Field(None, max_length=100)
    timezone: str | None = Field(None, max_length=50)
