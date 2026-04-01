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

# XP & Level constants
BASE_XP_PER_COMPLETION = 2.0
XP_STREAK_BONUS_FACTOR = 0.15
XP_CURVE_BASE = 10.0       # XP for level 0→1
XP_CURVE_EXPONENT = 1.3    # each level needs more XP

# Vitality constants (0-100 daily energy)
VITALITY_COMPLETION_BOOST = 20.0
VITALITY_SKIP_PENALTY = 15.0
VITALITY_DAILY_DECAY = 10.0
VITALITY_MAX = 100.0
VITALITY_MIN = 0.0
INITIAL_VITALITY = 50.0


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
    READY_TO_CLAIM = "ready_to_claim"
    COMPLETED = "completed"
    EXPIRED = "expired"


class TriggerType(StrEnum):
    COMPLETION = "completion"
    SKIP = "skip"
    QUEST_COMPLETE = "quest_complete"
