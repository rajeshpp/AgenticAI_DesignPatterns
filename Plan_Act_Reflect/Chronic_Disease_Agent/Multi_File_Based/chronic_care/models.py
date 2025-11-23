# chronic_care/models.py
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from enum import Enum
from statistics import mean
from typing import List, Optional, Tuple


# ---------- Core domain models ----------


@dataclass(frozen=True)
class GlucoseReading:
    timestamp: datetime
    value_mg_dl: float


@dataclass(frozen=True)
class BloodPressureReading:
    timestamp: datetime
    systolic: int
    diastolic: int


@dataclass(frozen=True)
class MedicationEvent:
    timestamp: datetime
    name: str
    taken: bool


@dataclass(frozen=True)
class MealLog:
    timestamp: datetime
    description: str
    carbs_g: float
    tag: str  # "breakfast", "lunch", "dinner", "snack"


@dataclass(frozen=True)
class ActivityLog:
    timestamp: datetime
    minutes: int
    intensity: str  # "low", "moderate", "high"
    tag: str        # e.g. "post-meal-walk"


@dataclass(frozen=True)
class SleepLog:
    date: datetime
    hours: float


@dataclass(frozen=True)
class StressLog:
    date: datetime
    level_1_to_5: int  # 1 = very low, 5 = very high


@dataclass(frozen=True)
class PatientProfile:
    id: str
    disease: str = "type2_diabetes"
    caregiver_contact: Optional[str] = None
    post_meal_walk_minutes: int = 20
    expected_walk_glucose_drop_pct: float = 0.15  # 15%

    def with_updates(
        self,
        *,
        post_meal_walk_minutes: Optional[int] = None,
        expected_walk_glucose_drop_pct: Optional[float] = None,
    ) -> "PatientProfile":
        """Return a new profile with updated parameters."""
        return replace(
            self,
            post_meal_walk_minutes=(
                self.post_meal_walk_minutes
                if post_meal_walk_minutes is None
                else post_meal_walk_minutes
            ),
            expected_walk_glucose_drop_pct=(
                self.expected_walk_glucose_drop_pct
                if expected_walk_glucose_drop_pct is None
                else expected_walk_glucose_drop_pct
            ),
        )


@dataclass(frozen=True)
class PatientDayState:
    """
    Snapshot of a patient's previous day.

    This is the "memory" passed into the PlannerAgent to create the next day's plan,
    and to the ReflectAgent to analyze performance.
    """

    profile: PatientProfile
    glucose_readings: List[GlucoseReading]
    bp_readings: List[BloodPressureReading]
    medication_events: List[MedicationEvent]
    meals: List[MealLog]
    activities: List[ActivityLog]
    sleep: Optional[SleepLog] = None
    stress: Optional[StressLog] = None


# ---------- Plan / Act / Reflect models ----------


@dataclass(frozen=True)
class DailyPlan:
    date: datetime
    glucose_target_range: Tuple[int, int]
    post_meal_walk_minutes: int
    walk_after_meals: List[str]
    medication_reminders: List[str]
    notes: List[str] = field(default_factory=list)


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class Action:
    timestamp: datetime
    message: str
    severity: Severity = Severity.INFO


@dataclass(frozen=True)
class Reflection:
    date: datetime
    what_worked: List[str]
    what_didnt: List[str]
    spike_reduction_pct: Optional[float]
    updated_profile: PatientProfile


# ---------- Utility functions (pure, reusable) ----------


def average(values: List[float]) -> Optional[float]:
    return mean(values) if values else None


def get_post_meal_window(meal: MealLog, hours: int = 2) -> Tuple[datetime, datetime]:
    start = meal.timestamp
    end = meal.timestamp + timedelta(hours=hours)
    return start, end
