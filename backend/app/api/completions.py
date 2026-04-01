import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import CompletionStatus
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.completion import (
    CategoryScoreResponse,
    CompletionRequest,
    CompletionResponse,
    CompletionWithScoreResponse,
    NarrationResponse,
)
from app.services import completion_service

router = APIRouter(prefix="/habits", tags=["Completions"])


@router.post(
    "/{habit_id}/complete",
    response_model=CompletionWithScoreResponse,
    summary="Mark habit as completed",
    description="Records a completion, updates category score, generates AI Master narration, and returns all three.",
)
async def complete_habit(
    habit_id: uuid.UUID,
    body: CompletionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    completion, score, narration = await completion_service.record_completion(
        db, habit_id, user.id, body.date, CompletionStatus.COMPLETED
    )
    return CompletionWithScoreResponse(
        completion=CompletionResponse.model_validate(completion),
        updated_score=CategoryScoreResponse.model_validate(score),
        narration=NarrationResponse.model_validate(narration) if narration else None,
    )


@router.post(
    "/{habit_id}/skip",
    response_model=CompletionWithScoreResponse,
    summary="Mark habit as skipped",
    description="Records a skip, applies penalty to category score, generates AI Master narration.",
)
async def skip_habit(
    habit_id: uuid.UUID,
    body: CompletionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    completion, score, narration = await completion_service.record_completion(
        db, habit_id, user.id, body.date, CompletionStatus.SKIPPED
    )
    return CompletionWithScoreResponse(
        completion=CompletionResponse.model_validate(completion),
        updated_score=CategoryScoreResponse.model_validate(score),
        narration=NarrationResponse.model_validate(narration) if narration else None,
    )


@router.get(
    "/{habit_id}/history",
    response_model=list[CompletionResponse],
    summary="Get habit completion history",
)
async def get_history(
    habit_id: uuid.UUID,
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await completion_service.get_habit_history(db, habit_id, user.id, limit, offset)
