"""Pure scoring logic — no DB access, fully testable."""

import math

from app.core.constants import (
    BASE_COMPLETION_POINTS,
    BASE_SKIP_PENALTY,
    CONSECUTIVE_SKIP_MULTIPLIER,
    DAILY_DECAY_RATE,
    MAX_SKIP_PENALTY,
    SCORE_MAX,
    SCORE_MIN,
    STREAK_BONUS_FACTOR,
)


def completion_points(streak_days: int) -> float:
    """Calculate points for completing a habit given current streak."""
    return BASE_COMPLETION_POINTS * (1 + STREAK_BONUS_FACTOR * math.log(1 + streak_days))


def skip_penalty(consecutive_skips: int) -> float:
    """Calculate penalty for skipping. Compounds with consecutive skips, capped."""
    raw = BASE_SKIP_PENALTY * (CONSECUTIVE_SKIP_MULTIPLIER ** (consecutive_skips - 1))
    return max(raw, MAX_SKIP_PENALTY)


def apply_decay(score: float, inactive_days: int) -> float:
    """Apply daily decay for inactive categories."""
    decayed = score - (DAILY_DECAY_RATE * inactive_days)
    return clamp_score(decayed)


def clamp_score(score: float) -> float:
    return max(SCORE_MIN, min(SCORE_MAX, score))
