from enum import StrEnum


class Category(StrEnum):
    INTELLIGENCE = "intelligence"
    STAMINA = "stamina"
    SOCIALITY = "sociality"
    CREATIVITY = "creativity"
    DISCIPLINE = "discipline"
    WELLNESS = "wellness"


CATEGORY_META = {
    Category.INTELLIGENCE: {"color": "#A78BFA", "glow": "#C4B5FD", "label": "Intelligence", "icon": "brain"},
    Category.STAMINA: {"color": "#34D399", "glow": "#6EE7B7", "label": "Stamina", "icon": "flame"},
    Category.SOCIALITY: {"color": "#FBBF24", "glow": "#FDE68A", "label": "Sociality", "icon": "users"},
    Category.CREATIVITY: {"color": "#FB923C", "glow": "#FDBA74", "label": "Creativity", "icon": "palette"},
    Category.DISCIPLINE: {"color": "#38BDF8", "glow": "#7DD3FC", "label": "Discipline", "icon": "shield"},
    Category.WELLNESS: {"color": "#F472B6", "glow": "#F9A8D4", "label": "Wellness", "icon": "heart"},
}

ALL_CATEGORIES = list(Category)

# Scoring constants
BASE_COMPLETION_POINTS = 2.0
STREAK_BONUS_FACTOR = 0.15
BASE_SKIP_PENALTY = -1.0
CONSECUTIVE_SKIP_MULTIPLIER = 1.5
MAX_SKIP_PENALTY = -8.0
DAILY_DECAY_RATE = 0.3
SCORE_MIN = 0.0
SCORE_MAX = 100.0


class ScheduleType(StrEnum):
    DAILY = "daily"
    SPECIFIC_DAYS = "specific_days"
    MULTIPLE_DAILY = "multiple_daily"


class CompletionStatus(StrEnum):
    COMPLETED = "completed"
    SKIPPED = "skipped"


class QuestType(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"


class QuestStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"


class TriggerType(StrEnum):
    COMPLETION = "completion"
    SKIP = "skip"
    QUEST_COMPLETE = "quest_complete"
