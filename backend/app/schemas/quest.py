import uuid
from datetime import date, datetime

from pydantic import BaseModel


class QuestResponse(BaseModel):
    id: uuid.UUID
    quest_type: str
    title: str
    description: str
    target_category: str
    criteria_json: dict
    bonus_points: float
    status: str
    issued_date: date
    expires_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
