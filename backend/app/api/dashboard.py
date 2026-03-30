from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.dashboard import MonthResponse, TodayResponse, WeekResponse
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/today",
    response_model=TodayResponse,
    summary="Get today's dashboard",
    description="Returns today's due habits with statuses, category scores, and active quests.",
)
async def get_today(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await dashboard_service.get_today(db, user.id, date.today())


@router.get(
    "/week",
    response_model=WeekResponse,
    summary="Get weekly habit grid",
    description="Returns a 7-day grid of habits with completion statuses. Read-only view.",
)
async def get_week(
    ref_date: date = Query(default_factory=date.today, alias="date"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await dashboard_service.get_week(db, user.id, ref_date)


@router.get(
    "/month",
    response_model=MonthResponse,
    summary="Get monthly calendar view",
    description="Returns daily completion summaries for the month. Read-only view.",
)
async def get_month(
    ref_date: date = Query(default_factory=date.today, alias="date"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await dashboard_service.get_month(db, user.id, ref_date)
