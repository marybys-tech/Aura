"""Unit tests for the scoring algorithm — the mathematical core of Aura."""

import math

import pytest

from app.services.stats_engine import apply_decay, clamp_score, completion_points, skip_penalty


class TestCompletionPoints:
    def test_no_streak(self):
        pts = completion_points(0)
        assert pts == pytest.approx(2.0)

    def test_short_streak(self):
        pts = completion_points(7)
        expected = 2.0 * (1 + 0.15 * math.log(8))
        assert pts == pytest.approx(expected)

    def test_medium_streak(self):
        pts = completion_points(30)
        expected = 2.0 * (1 + 0.15 * math.log(31))
        assert pts == pytest.approx(expected)
        assert pts > 2.0

    def test_long_streak(self):
        pts = completion_points(100)
        expected = 2.0 * (1 + 0.15 * math.log(101))
        assert pts == pytest.approx(expected)
        assert pts < 4.0  # logarithmic, never gets absurdly high

    def test_points_increase_with_streak(self):
        assert completion_points(0) < completion_points(7) < completion_points(30) < completion_points(100)

    def test_diminishing_returns(self):
        """Gap between streak 0→7 should be larger than 93→100."""
        low_gain = completion_points(7) - completion_points(0)
        high_gain = completion_points(100) - completion_points(93)
        assert low_gain > high_gain


class TestSkipPenalty:
    def test_first_skip(self):
        assert skip_penalty(1) == pytest.approx(-1.0)

    def test_second_skip(self):
        assert skip_penalty(2) == pytest.approx(-1.5)

    def test_third_skip(self):
        assert skip_penalty(3) == pytest.approx(-2.25)

    def test_compounding(self):
        assert skip_penalty(1) > skip_penalty(2) > skip_penalty(3)

    def test_capped_at_max(self):
        assert skip_penalty(10) == pytest.approx(-8.0)
        assert skip_penalty(20) == pytest.approx(-8.0)

    def test_fifth_skip(self):
        expected = -1.0 * (1.5 ** 4)
        assert skip_penalty(5) == pytest.approx(expected)


class TestApplyDecay:
    def test_single_day_decay(self):
        assert apply_decay(50.0, 1) == pytest.approx(49.7)

    def test_multiple_days(self):
        assert apply_decay(50.0, 10) == pytest.approx(47.0)

    def test_decay_never_below_zero(self):
        assert apply_decay(0.5, 5) == 0.0

    def test_no_decay_zero_days(self):
        assert apply_decay(75.0, 0) == 75.0


class TestClampScore:
    def test_normal_range(self):
        assert clamp_score(50.0) == 50.0

    def test_clamp_above_max(self):
        assert clamp_score(150.0) == 100.0

    def test_clamp_below_min(self):
        assert clamp_score(-10.0) == 0.0

    def test_boundary_values(self):
        assert clamp_score(0.0) == 0.0
        assert clamp_score(100.0) == 100.0
