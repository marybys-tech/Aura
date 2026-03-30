from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.narration import Narration
from app.models.user import User
from app.schemas.completion import NarrationResponse

router = APIRouter(prefix="/ai", tags=["AI Master"])


@router.get(
    "/narrations",
    response_model=list[NarrationResponse],
    summary="Get recent narrations",
    description="Returns recent AI Master narrations for the current user.",
)
async def get_narrations(
    limit: int = Query(10, ge=1, le=50),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Narration)
        .where(Narration.user_id == user.id)
        .order_by(Narration.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
