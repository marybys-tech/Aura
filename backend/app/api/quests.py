import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.quest import QuestResponse
from app.services import quest_service

router = APIRouter(prefix="/quests", tags=["Quests"])


@router.get(
    "",
    response_model=list[QuestResponse],
    summary="List quests",
    description="Returns active and recently completed/expired quests.",
)
async def list_quests(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await quest_service.get_quests(db, user.id)


@router.post(
    "/{quest_id}/claim",
    response_model=QuestResponse,
    summary="Claim a completed quest",
    description="Awards bonus points for the quest's target category.",
)
async def claim_quest(
    quest_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await quest_service.claim_quest(db, quest_id, user.id)
