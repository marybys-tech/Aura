"""Unit tests for habit schedule validation logic."""

import pytest

from app.core.constants import Category, ScheduleType
from app.schemas.habit import HabitCreateRequest
from app.services.habit_service import _validate_schedule


def _make_request(**overrides):
    defaults = {
        "title": "Test Habit",
        "category": Category.INTELLIGENCE,
        "schedule_type": ScheduleType.DAILY,
    }
    defaults.update(overrides)
    return HabitCreateRequest(**defaults)


class TestDailySchedule:
    def test_daily_no_days_is_valid(self):
        req = _make_request(schedule_type=ScheduleType.DAILY)
        _validate_schedule(req)  # should not raise

    def test_daily_with_days_is_valid(self):
        req = _make_request(schedule_type=ScheduleType.DAILY, schedule_days=[1, 2])
        _validate_schedule(req)  # daily ignores schedule_days


class TestSpecificDaysSchedule:
    def test_valid_specific_days(self):
        req = _make_request(
            schedule_type=ScheduleType.SPECIFIC_DAYS,
            schedule_days=[1, 3, 5],
        )
        _validate_schedule(req)  # should not raise

    def test_missing_schedule_days_raises(self):
        req = _make_request(schedule_type=ScheduleType.SPECIFIC_DAYS)
        with pytest.raises(ValueError, match="schedule_days required"):
            _validate_schedule(req)

    def test_empty_list_raises(self):
        req = _make_request(
            schedule_type=ScheduleType.SPECIFIC_DAYS,
            schedule_days=[],
        )
        with pytest.raises(ValueError, match="schedule_days required"):
            _validate_schedule(req)

    def test_day_below_1_raises(self):
        req = _make_request(
            schedule_type=ScheduleType.SPECIFIC_DAYS,
            schedule_days=[0, 3],
        )
        with pytest.raises(ValueError, match="ISO weekdays 1-7"):
            _validate_schedule(req)

    def test_day_above_7_raises(self):
        req = _make_request(
            schedule_type=ScheduleType.SPECIFIC_DAYS,
            schedule_days=[1, 8],
        )
        with pytest.raises(ValueError, match="ISO weekdays 1-7"):
            _validate_schedule(req)

    def test_boundary_days_1_and_7_valid(self):
        req = _make_request(
            schedule_type=ScheduleType.SPECIFIC_DAYS,
            schedule_days=[1, 7],
        )
        _validate_schedule(req)  # should not raise

    def test_all_seven_days_valid(self):
        req = _make_request(
            schedule_type=ScheduleType.SPECIFIC_DAYS,
            schedule_days=[1, 2, 3, 4, 5, 6, 7],
        )
        _validate_schedule(req)  # should not raise


class TestMultipleDailySchedule:
    def test_times_2_is_valid(self):
        req = _make_request(
            schedule_type=ScheduleType.MULTIPLE_DAILY,
            times_per_day=2,
        )
        _validate_schedule(req)  # should not raise

    def test_times_1_raises(self):
        req = _make_request(
            schedule_type=ScheduleType.MULTIPLE_DAILY,
            times_per_day=1,
        )
        with pytest.raises(ValueError, match="times_per_day must be >= 2"):
            _validate_schedule(req)
