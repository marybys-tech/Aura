import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.category_score import CategoryScore
from app.models.habit import Habit
from app.models.quest import Quest
from app.models.user import User
from app.schemas.quest import QuestResponse
from app.core.constants import QuestStatus
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
    summary="Request a quest from the Master",
    description="The Master analyzes your progress and creates a personalized quest. Falls back to local generation if AI is unavailable.",
)
async def generate_quest(
    quest_type: str = Query("daily", description="'daily' or 'weekly'"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check active quest limit
    active_count = await quest_service._count_active(db, user.id)
    if active_count >= quest_service.MAX_ACTIVE_QUESTS:
        return None

    # Get user context
    scores_result = await db.execute(select(CategoryScore).where(CategoryScore.user_id == user.id))
    scores = {s.category: {"level": s.level, "vitality": s.vitality, "streak": s.streak_days} for s in scores_result.scalars().all()}

    habits_result = await db.execute(
        select(Habit.title).where(Habit.user_id == user.id, Habit.is_active == True)  # noqa: E712
    )
    habit_titles = [r[0] for r in habits_result.all()]

    if not habit_titles:
        return None

    # Pick target category in code — weakest vitality that doesn't already have a quest
    existing_result = await db.execute(
        select(Quest.target_category).where(
            Quest.user_id == user.id, Quest.status.in_([QuestStatus.ACTIVE, QuestStatus.READY_TO_CLAIM])
        )
    )
    taken = set(r[0] for r in existing_result.all())

    vitality_scores = {k: v["vitality"] for k, v in scores.items()}
    available = [(k, v) for k, v in vitality_scores.items() if k not in taken]

    if not available:
        return None  # all categories have quests

    # Pick weakest available category
    target_cat, target_vitality = min(available, key=lambda x: x[1])

    # AI generates only the creative content (title + description)
    quest_data = await ai_master_service.generate_quest_data(
        target_category=target_cat,
        habits=habit_titles,
        quest_type=quest_type,
        vitality=target_vitality,
    )

    if not quest_data:
        return None

    return await quest_service.create_quest(db, user.id, quest_data)


@router.post(
    "/{quest_id}/claim",
    response_model=QuestResponse,
    summary="Claim a completed quest",
    description="Awards bonus XP and vitality for the quest's target category.",
)
async def claim_quest(
    quest_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await quest_service.claim_quest(db, quest_id, user.id)


@router.delete(
    "/{quest_id}",
    summary="Dismiss a quest",
)
async def delete_quest(
    quest_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.core.exceptions import NotFoundError
    result = await db.execute(select(Quest).where(Quest.id == quest_id))
    quest = result.scalar_one_or_none()
    if not quest or quest.user_id != user.id:
        raise NotFoundError("Quest not found")
    await db.delete(quest)
    await db.commit()
    return {"status": "ok"}
