"""Unit tests for the Level + Vitality scoring engine."""

import math

import pytest

from app.services.stats_engine import (
    apply_xp,
    clamp_vitality,
    completion_xp,
    compute_aura_score,
    vitality_daily_decay,
    vitality_on_completion,
    vitality_on_skip,
    xp_for_level,
)


class TestCompletionXP:
    def test_no_streak(self):
        assert completion_xp(0) == pytest.approx(2.0)

    def test_short_streak(self):
        expected = 2.0 * (1 + 0.15 * math.log(8))
        assert completion_xp(7) == pytest.approx(expected)

    def test_xp_increases_with_streak(self):
        assert completion_xp(0) < completion_xp(7) < completion_xp(30) < completion_xp(100)

    def test_diminishing_returns(self):
        low_gain = completion_xp(7) - completion_xp(0)
        high_gain = completion_xp(100) - completion_xp(93)
        assert low_gain > high_gain


class TestXPForLevel:
    def test_level_zero(self):
        assert xp_for_level(0) == 10.0

    def test_level_one(self):
        assert xp_for_level(1) == 10.0  # 10 * 1^1.3 = 10

    def test_level_five(self):
        expected = 10.0 * (5 ** 1.3)
        assert xp_for_level(5) == pytest.approx(expected)

    def test_increases_with_level(self):
        assert xp_for_level(1) < xp_for_level(5) < xp_for_level(10) < xp_for_level(20)


class TestApplyXP:
    def test_no_level_up(self):
        xp, level, leveled = apply_xp(0, 0, 5.0)
        assert xp == 5.0
        assert level == 0
        assert leveled is False

    def test_exact_level_up(self):
        xp, level, leveled = apply_xp(0, 0, 10.0)
        assert level == 1
        assert leveled is True
        assert xp == 0.0

    def test_overflow_level_up(self):
        xp, level, leveled = apply_xp(0, 0, 12.0)
        assert level == 1
        assert leveled is True
        assert xp == 2.0

    def test_multiple_level_ups(self):
        xp, level, leveled = apply_xp(0, 0, 100.0)
        assert level > 2
        assert leveled is True

    def test_accumulation(self):
        xp, level, _ = apply_xp(8.0, 0, 3.0)
        # 8 + 3 = 11, need 10 for level 1, so level=1, xp=1
        assert level == 1
        assert xp == 1.0


class TestVitality:
    def test_completion_boost(self):
        assert vitality_on_completion(50) == 70.0

    def test_completion_capped(self):
        assert vitality_on_completion(90) == 100.0

    def test_skip_penalty(self):
        assert vitality_on_skip(50) == 35.0

    def test_skip_floored(self):
        assert vitality_on_skip(5) == 0.0

    def test_daily_decay(self):
        assert vitality_daily_decay(50) == 40.0

    def test_daily_decay_floored(self):
        assert vitality_daily_decay(3) == 0.0

    def test_clamp_bounds(self):
        assert clamp_vitality(-10) == 0.0
        assert clamp_vitality(150) == 100.0
        assert clamp_vitality(50) == 50.0


class TestAuraScore:
    def test_all_zero(self):
        assert compute_aura_score([0, 0, 0, 0, 0, 0], [50, 50, 50, 50, 50, 50]) == 0.0

    def test_with_levels(self):
        # Level 10, vitality 100: 10 * (1.0 + 0.2) = 12.0
        score = compute_aura_score([10], [100])
        assert score == 12.0

    def test_low_vitality_still_contributes(self):
        # Level 10, vitality 0: 10 * (0.0 + 0.2) = 2.0
        score = compute_aura_score([10], [0])
        assert score == 2.0

    def test_mixed(self):
        levels = [5, 3, 0, 0, 0, 0]
        vitalities = [80, 60, 50, 50, 50, 50]
        score = compute_aura_score(levels, vitalities)
        expected = 5 * (0.8 + 0.2) + 3 * (0.6 + 0.2)
        assert score == pytest.approx(expected, rel=0.01)
