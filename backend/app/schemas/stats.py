from datetime import date

from pydantic import BaseModel

from app.schemas.completion import CategoryScoreResponse


class StatsResponse(BaseModel):
    scores: dict[str, CategoryScoreResponse]
    total_aura: float


class ScoreSnapshot(BaseModel):
    date: date
    scores: dict[str, float]


class StatsHistoryResponse(BaseModel):
    period: str
    snapshots: list[ScoreSnapshot]
