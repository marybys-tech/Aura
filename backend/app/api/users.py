from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserUpdateRequest, UserWithScoresResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserWithScoresResponse, summary="Get current user profile with scores")
async def get_me(user: User = Depends(get_current_user)):
    scores = {s.category: {"level": s.level, "vitality": s.vitality} for s in user.category_scores}
    return UserWithScoresResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        oauth_provider=user.oauth_provider,
        timezone=user.timezone,
        created_at=user.created_at,
        scores=scores,
    )


@router.patch("/me", response_model=UserWithScoresResponse, summary="Update user profile")
async def update_me(
    body: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.display_name is not None:
        user.display_name = body.display_name
    if body.timezone is not None:
        user.timezone = body.timezone
    await db.commit()
    await db.refresh(user)
    scores = {s.category: {"level": s.level, "vitality": s.vitality} for s in user.category_scores}
    return UserWithScoresResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        oauth_provider=user.oauth_provider,
        timezone=user.timezone,
        created_at=user.created_at,
        scores=scores,
    )
