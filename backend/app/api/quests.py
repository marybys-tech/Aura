import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.category_score import CategoryScore
from app.models.habit import Habit
from app.models.user import User
from app.schemas.quest import QuestResponse
from app.services import ai_master_service, quest_service

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
    "/generate",
    response_model=QuestResponse | None,
    summary="Generate a new quest via AI Master",
    description="AI Master analyzes your scores and habits to create a personalized quest targeting your weakest category.",
)
async def generate_quest(
    quest_type: str = "daily",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    scores_result = await db.execute(select(CategoryScore).where(CategoryScore.user_id == user.id))
    scores = {s.category: s.vitality for s in scores_result.scalars().all()}

    habits_result = await db.execute(
        select(Habit.title).where(Habit.user_id == user.id, Habit.is_active == True)  # noqa: E712
    )
    habit_titles = [r[0] for r in habits_result.all()]

    quest_data = await ai_master_service.generate_quest_data(scores, habit_titles, quest_type)
    if not quest_data:
        return None

    quest = await quest_service.create_quest(db, user.id, quest_data)
    return quest


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
