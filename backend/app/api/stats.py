from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.category_score import CategoryScore
from app.models.user import User
from app.schemas.completion import CategoryScoreResponse
from app.schemas.stats import StatsResponse
from app.services.stats_engine import compute_aura_score

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get(
    "",
    response_model=StatsResponse,
    summary="Get all category scores, levels, and vitality",
    description="Returns level, XP, vitality for all 6 categories plus total Aura power.",
)
async def get_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(CategoryScore).where(CategoryScore.user_id == user.id))
    rows = list(result.scalars().all())
    scores_map = {s.category: CategoryScoreResponse.model_validate(s) for s in rows}
    total = compute_aura_score([s.level for s in rows], [s.vitality for s in rows])
    return StatsResponse(scores=scores_map, total_aura=total)
