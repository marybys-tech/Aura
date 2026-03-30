from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.category_score import CategoryScore
from app.models.user import User
from app.schemas.completion import CategoryScoreResponse
from app.schemas.stats import StatsResponse

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get(
    "",
    response_model=StatsResponse,
    summary="Get all category scores and streaks",
    description="Returns scores for all 6 categories plus total aura value.",
)
async def get_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(CategoryScore).where(CategoryScore.user_id == user.id))
    scores_map = {s.category: CategoryScoreResponse.model_validate(s) for s in result.scalars().all()}
    total = sum(s.score for s in scores_map.values())
    return StatsResponse(scores=scores_map, total_aura=round(total, 1))
