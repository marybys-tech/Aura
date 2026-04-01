"""Level + Vitality scoring engine — pure logic, no DB access."""

import math

from app.core.constants import (
    BASE_XP_PER_COMPLETION,
    INITIAL_VITALITY,
    VITALITY_COMPLETION_BOOST,
    VITALITY_DAILY_DECAY,
    VITALITY_MAX,
    VITALITY_MIN,
    VITALITY_SKIP_PENALTY,
    XP_CURVE_BASE,
    XP_CURVE_EXPONENT,
    XP_STREAK_BONUS_FACTOR,
)


# --- XP & Leveling ---

def completion_xp(streak_days: int) -> float:
    """XP earned from completing a habit. Streak gives logarithmic bonus."""
    return BASE_XP_PER_COMPLETION * (1 + XP_STREAK_BONUS_FACTOR * math.log(1 + streak_days))


def xp_for_level(level: int) -> float:
    """XP required to advance from `level` to `level + 1`."""
    if level <= 0:
        return XP_CURVE_BASE
    return XP_CURVE_BASE * (level ** XP_CURVE_EXPONENT)


def apply_xp(
    current_xp: float, current_level: int, earned_xp: float
) -> tuple[float, int, bool]:
    """Add XP, handle level-ups. Returns (new_xp, new_level, leveled_up)."""
    xp = current_xp + earned_xp
    level = current_level
    leveled_up = False
    required = xp_for_level(level)

    while xp >= required:
        xp -= required
        level += 1
        leveled_up = True
        required = xp_for_level(level)

    return round(xp, 2), level, leveled_up


# --- Vitality (daily energy, drives Aura) ---

def vitality_on_completion(current: float) -> float:
    """Boost vitality when completing a habit."""
    return clamp_vitality(current + VITALITY_COMPLETION_BOOST)


def vitality_on_skip(current: float) -> float:
    """Reduce vitality when skipping a habit."""
    return clamp_vitality(current - VITALITY_SKIP_PENALTY)


def vitality_daily_decay(current: float) -> float:
    """Natural daily drain for inactive categories."""
    return clamp_vitality(current - VITALITY_DAILY_DECAY)


def clamp_vitality(v: float) -> float:
    return max(VITALITY_MIN, min(VITALITY_MAX, v))


# --- Aura Score ---

def compute_aura_score(levels: list[int], vitalities: list[float]) -> float:
    """Single Aura power number: Σ (level × (vitality/100 + 0.2))."""
    total = 0.0
    for level, vitality in zip(levels, vitalities):
        total += level * (vitality / 100 + 0.2)
    return round(total, 1)
