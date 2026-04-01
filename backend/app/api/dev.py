"""Dev-only endpoints for testing scoring/aura scenarios. Not for production."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.category_score import CategoryScore
from app.models.user import User

router = APIRouter(prefix="/dev", tags=["Dev / Testing"])

SCENARIOS = {
    "fresh": {
        "description": "Fresh user — just signed up, no activity",
        "scores": {
            "intelligence": {"level": 0, "xp": 0, "vitality": 50},
            "stamina": {"level": 0, "xp": 0, "vitality": 50},
            "sociality": {"level": 0, "xp": 0, "vitality": 50},
            "creativity": {"level": 0, "xp": 0, "vitality": 50},
            "discipline": {"level": 0, "xp": 0, "vitality": 50},
            "wellness": {"level": 0, "xp": 0, "vitality": 50},
        },
    },
    "day1_active": {
        "description": "Day 1 — completed a few habits in Intelligence and Stamina",
        "scores": {
            "intelligence": {"level": 0, "xp": 6, "vitality": 90},
            "stamina": {"level": 0, "xp": 4, "vitality": 70},
            "sociality": {"level": 0, "xp": 0, "vitality": 50},
            "creativity": {"level": 0, "xp": 0, "vitality": 50},
            "discipline": {"level": 0, "xp": 0, "vitality": 50},
            "wellness": {"level": 0, "xp": 0, "vitality": 50},
        },
    },
    "week1": {
        "description": "After 1 week — steady progress in 3 categories",
        "scores": {
            "intelligence": {"level": 1, "xp": 5, "vitality": 85},
            "stamina": {"level": 1, "xp": 2, "vitality": 80},
            "sociality": {"level": 0, "xp": 8, "vitality": 70},
            "creativity": {"level": 0, "xp": 0, "vitality": 30},
            "discipline": {"level": 0, "xp": 0, "vitality": 20},
            "wellness": {"level": 0, "xp": 0, "vitality": 15},
        },
    },
    "month1": {
        "description": "After 1 month — strong in 2 categories, moderate in 2, weak in 2",
        "scores": {
            "intelligence": {"level": 5, "xp": 15, "vitality": 95},
            "stamina": {"level": 4, "xp": 8, "vitality": 90},
            "sociality": {"level": 2, "xp": 5, "vitality": 60},
            "creativity": {"level": 1, "xp": 3, "vitality": 45},
            "discipline": {"level": 0, "xp": 2, "vitality": 10},
            "wellness": {"level": 0, "xp": 0, "vitality": 0},
        },
    },
    "balanced_pro": {
        "description": "3 months — balanced development across all categories",
        "scores": {
            "intelligence": {"level": 8, "xp": 30, "vitality": 85},
            "stamina": {"level": 7, "xp": 25, "vitality": 80},
            "sociality": {"level": 6, "xp": 20, "vitality": 75},
            "creativity": {"level": 7, "xp": 15, "vitality": 80},
            "discipline": {"level": 5, "xp": 10, "vitality": 70},
            "wellness": {"level": 6, "xp": 28, "vitality": 85},
        },
    },
    "one_dominant": {
        "description": "Intelligence master — one category way ahead",
        "scores": {
            "intelligence": {"level": 13, "xp": 50, "vitality": 98},
            "stamina": {"level": 1, "xp": 3, "vitality": 30},
            "sociality": {"level": 0, "xp": 0, "vitality": 10},
            "creativity": {"level": 0, "xp": 5, "vitality": 15},
            "discipline": {"level": 0, "xp": 0, "vitality": 5},
            "wellness": {"level": 0, "xp": 0, "vitality": 0},
        },
    },
    "neglected": {
        "description": "Abandoned for a week — all vitality drained",
        "scores": {
            "intelligence": {"level": 5, "xp": 15, "vitality": 0},
            "stamina": {"level": 3, "xp": 8, "vitality": 0},
            "sociality": {"level": 2, "xp": 5, "vitality": 2},
            "creativity": {"level": 1, "xp": 3, "vitality": 0},
            "discipline": {"level": 0, "xp": 2, "vitality": 0},
            "wellness": {"level": 0, "xp": 0, "vitality": 0},
        },
    },
    "comeback": {
        "description": "Coming back after neglect — completed 2 habits today",
        "scores": {
            "intelligence": {"level": 5, "xp": 17, "vitality": 40},
            "stamina": {"level": 3, "xp": 10, "vitality": 25},
            "sociality": {"level": 2, "xp": 5, "vitality": 0},
            "creativity": {"level": 1, "xp": 3, "vitality": 0},
            "discipline": {"level": 0, "xp": 2, "vitality": 0},
            "wellness": {"level": 0, "xp": 0, "vitality": 0},
        },
    },
}


@router.get(
    "/scenarios",
    summary="List available test scenarios",
    description="Returns all predefined test scenarios with descriptions.",
)
async def list_scenarios():
    return {name: {"description": s["description"]} for name, s in SCENARIOS.items()}


@router.post(
    "/scenarios/{scenario_name}",
    summary="Apply a test scenario to current user",
    description="Overwrites all category scores with the scenario values. Dev only.",
)
async def apply_scenario(
    scenario_name: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if scenario_name not in SCENARIOS:
        return {"error": f"Unknown scenario. Available: {list(SCENARIOS.keys())}"}

    scenario = SCENARIOS[scenario_name]
    result = await db.execute(
        select(CategoryScore).where(CategoryScore.user_id == user.id)
    )
    rows = {s.category: s for s in result.scalars().all()}

    for category, values in scenario["scores"].items():
        if category in rows:
            s = rows[category]
            s.level = values["level"]
            s.xp = values["xp"]
            s.xp_to_next = round(10.0 * max(values["level"], 1) ** 1.3, 2) if values["level"] > 0 else 10.0
            s.vitality = values["vitality"]
            s.streak_days = 0

    await db.commit()
    return {"applied": scenario_name, "description": scenario["description"]}
