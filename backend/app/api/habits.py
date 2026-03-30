import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.habit import HabitCreateRequest, HabitResponse, HabitUpdateRequest
from app.services import habit_service

router = APIRouter(prefix="/habits", tags=["Habits"])


@router.post("", response_model=HabitResponse, status_code=201, summary="Create a new habit")
async def create_habit(
    body: HabitCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        habit = await habit_service.create_habit(db, user.id, body)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return habit


@router.get("", response_model=list[HabitResponse], summary="List user habits")
async def list_habits(
    category: str | None = Query(None),
    is_active: bool | None = Query(True),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await habit_service.list_habits(db, user.id, category, is_active)


@router.get("/{habit_id}", response_model=HabitResponse, summary="Get habit detail")
async def get_habit(
    habit_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await habit_service.get_habit(db, habit_id, user.id)


@router.patch("/{habit_id}", response_model=HabitResponse, summary="Update a habit")
async def update_habit(
    habit_id: uuid.UUID,
    body: HabitUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await habit_service.update_habit(db, habit_id, user.id, body)


@router.delete("/{habit_id}", response_model=HabitResponse, summary="Soft-delete a habit")
async def delete_habit(
    habit_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await habit_service.delete_habit(db, habit_id, user.id)
