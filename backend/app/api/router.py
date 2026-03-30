from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.completions import router as completions_router
from app.api.dashboard import router as dashboard_router
from app.api.habits import router as habits_router
from app.api.quests import router as quests_router
from app.api.stats import router as stats_router
from app.api.users import router as users_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(habits_router)
api_router.include_router(completions_router)
api_router.include_router(dashboard_router)
api_router.include_router(stats_router)
api_router.include_router(quests_router)


@api_router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
