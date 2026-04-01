"""Unit tests for quest builder pure functions."""

import pytest

from app.services.quest_service import (
    _build_comeback_quest,
    _build_daily_quest,
    _build_weekly_quest,
)


def _make_scores(**overrides):
    """Build a scores dict with default vitality=50 for all categories."""
    base = {
        cat: {"level": 1, "vitality": 50, "streak": 0}
        for cat in ("intelligence", "stamina", "sociality", "creativity", "discipline", "wellness")
    }
    for cat, vit in overrides.items():
        base[cat]["vitality"] = vit
    return base


class TestBuildDailyQuest:
    def test_targets_weakest_category(self):
        scores = _make_scores(wellness=10, intelligence=90)
        quest = _build_daily_quest(scores, ["Read", "Run", "Meditate"])
        assert quest["target_category"] == "wellness"

    def test_returns_daily_type(self):
        scores = _make_scores()
        quest = _build_daily_quest(scores, ["Read"])
        assert quest["quest_type"] == "daily"

    def test_criteria_type_is_complete_n_habits(self):
        scores = _make_scores()
        quest = _build_daily_quest(scores, ["Read"])
        assert quest["criteria"]["type"] == "complete_n_habits"

    def test_count_is_1_for_few_habits(self):
        scores = _make_scores()
        quest = _build_daily_quest(scores, ["Read", "Run"])
        assert quest["criteria"]["count"] == 1

    def test_count_is_2_for_many_habits(self):
        scores = _make_scores()
        quest = _build_daily_quest(scores, list(range(9)))  # 9 habits -> 9//3=3, clamped to 2
        assert quest["criteria"]["count"] == 2

    def test_bonus_points_scales_with_count(self):
        scores = _make_scores()
        q1 = _build_daily_quest(scores, ["a"])
        q2 = _build_daily_quest(scores, list(range(9)))
        assert q2["bonus_points"] > q1["bonus_points"]

    def test_title_includes_category_name(self):
        scores = _make_scores(stamina=5)
        quest = _build_daily_quest(scores, ["Run"])
        assert "Stamina" in quest["title"]


class TestBuildWeeklyQuest:
    def test_targets_weakest_category(self):
        scores = _make_scores(creativity=5, discipline=90)
        quest = _build_weekly_quest(scores, ["Draw", "Code"])
        assert quest["target_category"] == "creativity"

    def test_weekly_type(self):
        scores = _make_scores()
        quest = _build_weekly_quest(scores, ["Read"])
        assert quest["quest_type"] == "weekly"

    def test_criteria_is_maintain_streak_5_days(self):
        scores = _make_scores()
        quest = _build_weekly_quest(scores, ["Read"])
        assert quest["criteria"]["type"] == "maintain_streak"
        assert quest["criteria"]["days"] == 5

    def test_bonus_points_is_15(self):
        scores = _make_scores()
        quest = _build_weekly_quest(scores, ["Read"])
        assert quest["bonus_points"] == 15.0


class TestBuildComebackQuest:
    def test_returns_correct_category(self):
        scores = _make_scores(wellness=10)
        quest = _build_comeback_quest("wellness", scores)
        assert quest["target_category"] == "wellness"

    def test_criteria_is_any_completion(self):
        scores = _make_scores()
        quest = _build_comeback_quest("stamina", scores)
        assert quest["criteria"]["type"] == "any_completion"

    def test_bonus_is_8_points(self):
        scores = _make_scores()
        quest = _build_comeback_quest("intelligence", scores)
        assert quest["bonus_points"] == 8.0

    def test_title_contains_category(self):
        quest = _build_comeback_quest("discipline", _make_scores())
        assert "Discipline" in quest["title"]

    def test_description_mentions_fading(self):
        quest = _build_comeback_quest("creativity", _make_scores())
        assert "fading" in quest["description"]
