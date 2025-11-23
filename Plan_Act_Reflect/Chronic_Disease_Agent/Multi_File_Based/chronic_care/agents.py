# chronic_care/agents.py
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Tuple, Optional

from .models import (
    Action,
    DailyPlan,
    GlucoseReading,
    PatientDayState,
    PatientProfile,
    Reflection,
    Severity,
    average,
    get_post_meal_window,
)


# ---------- Base Agent (Agentic Pattern) ----------


@dataclass
class AgentContext:
    """
    Context shared across agents if needed later
    (e.g., configuration, logger, external model clients).

    For now, it just carries the timestamp to make testing easier.
    """
    now: datetime


class BaseAgent(ABC):
    """
    Base class for Plan / Act / Reflect agents.

    Makes the "agentic" pattern explicit and extensible.
    """

    def __init__(self, context: AgentContext) -> None:
        self._context = context

    @property
    def context(self) -> AgentContext:
        return self._context


# ---------- Planner Agent (PLAN) ----------


class PlannerAgent(BaseAgent):
    """
    PLAN: look at the previous day's state and propose a daily plan.
    """

    def create_plan(self, state: PatientDayState) -> DailyPlan:
        if not state.glucose_readings:
            # Fallback: generic plan
            today = self.context.now.date()
            return DailyPlan(
                date=datetime.combine(today, datetime.min.time()),
                glucose_target_range=(120, 150),
                post_meal_walk_minutes=state.profile.post_meal_walk_minutes,
                walk_after_meals=["lunch", "dinner"],
                medication_reminders=["Take your prescribed medications as directed."],
                notes=["No glucose readings available yesterday. Using default targets."],
            )

        yesterday_date = state.glucose_readings[-1].timestamp.date()
        today = yesterday_date + timedelta(days=1)

        glucose_values = [g.value_mg_dl for g in state.glucose_readings]
        avg_glucose = average(glucose_values) or 140

        target_range = self._compute_glucose_target(avg_glucose)
        walk_minutes = self._compute_walk_minutes(state, avg_glucose)
        walk_after_meals = self._detect_risky_meals(state) or ["lunch", "dinner"]
        med_reminders = self._build_medication_reminders(state)
        notes = self._build_notes(state, avg_glucose)

        return DailyPlan(
            date=datetime.combine(today, datetime.min.time()),
            glucose_target_range=target_range,
            post_meal_walk_minutes=walk_minutes,
            walk_after_meals=walk_after_meals,
            medication_reminders=med_reminders,
            notes=notes,
        )

    @staticmethod
    def _compute_glucose_target(avg_glucose: float) -> Tuple[int, int]:
        if avg_glucose > 180:
            return 130, 160
        if avg_glucose < 90:
            return 100, 130
        return 120, 150

    @staticmethod
    def _compute_walk_minutes(
        state: PatientDayState,
        avg_glucose: float,
    ) -> int:
        minutes = state.profile.post_meal_walk_minutes

        if avg_glucose > 180:
            minutes += 5
        if state.sleep and state.sleep.hours < 6:
            minutes = max(10, minutes - 5)
        if state.stress and state.stress.level_1_to_5 >= 4:
            minutes += 5

        return minutes

    @staticmethod
    def _build_medication_reminders(state: PatientDayState) -> List[str]:
        missed = [m for m in state.medication_events if not m.taken]
        if not missed:
            return []

        names = sorted({m.name for m in missed})
        msg = (
            f"Yesterday you missed: {', '.join(names)}. "
            "Let's double-check your medication schedule today."
        )
        return [msg]

    @staticmethod
    def _build_notes(
        state: PatientDayState,
        avg_glucose: float,
    ) -> List[str]:
        notes: List[str] = [f"Average glucose yesterday: {avg_glucose:.1f} mg/dL."]

        if state.sleep:
            notes.append(f"Sleep last night: {state.sleep.hours:.1f} hours.")
        if state.stress:
            notes.append(f"Stress level: {state.stress.level_1_to_5}/5.")

        notes.append("Try to avoid large carb loads in a single meal.")
        return notes

    @staticmethod
    def _detect_risky_meals(state: PatientDayState) -> List[str]:
        risky = set()

        for meal in state.meals:
            start, end = get_post_meal_window(meal)
            post_meal_values = [
                g.value_mg_dl
                for g in state.glucose_readings
                if start <= g.timestamp <= end
            ]
            if post_meal_values and (average(post_meal_values) or 0) > 180:
                risky.add(meal.tag)

        return sorted(risky)


# ---------- Act Agent (ACT) ----------


class ActAgent(BaseAgent):
    """
    ACT: respond to real-time signals given the plan and patient profile.

    In a real system this would integrate with notification systems, wearables,
    and potentially LLMs for personalized messaging.
    """

    def handle_glucose_reading(
        self,
        plan: DailyPlan,
        reading: GlucoseReading,
        profile: PatientProfile,
    ) -> List[Action]:
        lo, hi = plan.glucose_target_range
        value = reading.value_mg_dl

        if value < 70:
            return self._handle_hypo(reading)
        if value > hi:
            return self._handle_hyper(reading, plan, profile)
        return [self._handle_normal(reading, plan)]

    @staticmethod
    def _handle_hypo(reading: GlucoseReading) -> List[Action]:
        return [
            Action(
                timestamp=reading.timestamp,
                message=(
                    f"Glucose is {reading.value_mg_dl:.0f} mg/dL (low). "
                    "Take fast-acting carbs and recheck in 15 minutes. "
                    "If symptoms are severe, seek medical help immediately."
                ),
                severity=Severity.CRITICAL,
            )
        ]

    @staticmethod
    def _handle_normal(
        reading: GlucoseReading,
        plan: DailyPlan,
    ) -> Action:
        lo, hi = plan.glucose_target_range
        return Action(
            timestamp=reading.timestamp,
            message=(
                f"Nice! Glucose {reading.value_mg_dl:.0f} mg/dL is within your "
                f"target range ({lo}–{hi} mg/dL). Keep up the routine."
            ),
            severity=Severity.INFO,
        )

    @staticmethod
    def _handle_hyper(
        reading: GlucoseReading,
        plan: DailyPlan,
        profile: PatientProfile,
    ) -> List[Action]:
        lo, hi = plan.glucose_target_range
        actions: List[Action] = []

        actions.append(
            Action(
                timestamp=reading.timestamp,
                message=(
                    f"Glucose is {reading.value_mg_dl:.0f} mg/dL, above your "
                    f"target ({lo}–{hi} mg/dL). "
                    f"Consider a {profile.post_meal_walk_minutes}-minute walk now"
                    " if it's safe, and choose a lower-carb option next meal."
                ),
                severity=Severity.WARNING,
            )
        )

        if reading.value_mg_dl > 250 and profile.caregiver_contact:
            actions.append(
                Action(
                    timestamp=reading.timestamp,
                    message=(
                        "Glucose is very high. Consider informing your caregiver "
                        f"({profile.caregiver_contact}) and following your emergency plan."
                    ),
                    severity=Severity.CRITICAL,
                )
            )

        return actions

    def build_meal_reminder(self, plan: DailyPlan, meal_tag: str) -> Action:
        if meal_tag in plan.walk_after_meals:
            message = (
                f"Before {meal_tag}, aim for a balanced plate and be ready "
                f"for a {plan.post_meal_walk_minutes}-minute walk afterwards."
            )
        else:
            message = (
                f"Before {meal_tag}, keep carbs moderate and stick to your plan."
            )
        return Action(timestamp=self.context.now, message=message, severity=Severity.INFO)


# ---------- Reflect Agent (REFLECT) ----------


class ReflectAgent(BaseAgent):
    """
    REFLECT: daily retrospective and adaptation.

    Analyzes what worked and updates the patient profile (closed feedback loop).
    """

    def reflect(
        self,
        state: PatientDayState,
        plan: DailyPlan,
    ) -> Reflection:
        with_walk, without_walk = self._collect_post_meal_spikes(state)

        spike_reduction_pct = self._compute_spike_reduction(with_walk, without_walk)
        what_worked, what_didnt = self._build_narrative(state, spike_reduction_pct)

        updated_profile = self._update_profile(state.profile, spike_reduction_pct)

        reflection_date = state.glucose_readings[-1].timestamp.date()
        return Reflection(
            date=datetime.combine(reflection_date, datetime.min.time()),
            what_worked=what_worked,
            what_didnt=what_didnt,
            spike_reduction_pct=spike_reduction_pct,
            updated_profile=updated_profile,
        )

    @staticmethod
    def _collect_post_meal_spikes(
        state: PatientDayState,
    ) -> Tuple[List[float], List[float]]:
        with_walk: List[float] = []
        without_walk: List[float] = []

        for meal in state.meals:
            start, end = get_post_meal_window(meal)

            post_meal_values = [
                g.value_mg_dl
                for g in state.glucose_readings
                if start <= g.timestamp <= end
            ]
            baseline_values = [
                g.value_mg_dl
                for g in state.glucose_readings
                if start - timedelta(minutes=30) <= g.timestamp < start
            ]

            if not post_meal_values or not baseline_values:
                continue

            post_meal_avg = average(post_meal_values)
            baseline_avg = average(baseline_values)

            if post_meal_avg is None or baseline_avg is None:
                continue

            spike = post_meal_avg - baseline_avg
            walked = any(
                a.tag == "post-meal-walk"
                and meal.timestamp <= a.timestamp <= end
                for a in state.activities
            )

            (with_walk if walked else without_walk).append(spike)

        return with_walk, without_walk

    @staticmethod
    def _compute_spike_reduction(
        with_walk: List[float],
        without_walk: List[float],
    ) -> Optional[float]:
        avg_with = average(with_walk)
        avg_without = average(without_walk)

        if avg_with is None or avg_without is None or avg_without <= 0:
            return None

        return (avg_without - avg_with) / avg_without

    @staticmethod
    def _build_narrative(
        state: PatientDayState,
        spike_reduction_pct: Optional[float],
    ) -> Tuple[List[str], List[str]]:
        what_worked: List[str] = []
        what_didnt: List[str] = []

        if spike_reduction_pct is not None:
            if spike_reduction_pct > 0.1:
                what_worked.append(
                    f"Post-meal walks reduced average glucose spikes by "
                    f"{spike_reduction_pct * 100:.1f}%."
                )
            else:
                what_didnt.append(
                    "Post-meal walks did not significantly reduce glucose spikes today."
                )

        avg_glucose = average([g.value_mg_dl for g in state.glucose_readings])

        if avg_glucose is not None:
            if avg_glucose > 180:
                what_didnt.append(
                    f"Average glucose was high at {avg_glucose:.1f} mg/dL."
                )
            else:
                what_worked.append(
                    f"Average glucose was acceptable at {avg_glucose:.1f} mg/dL."
                )

        return what_worked, what_didnt

    @staticmethod
    def _update_profile(
        profile: PatientProfile,
        spike_reduction_pct: Optional[float],
    ) -> PatientProfile:
        if spike_reduction_pct is None:
            return profile

        expected_drop = max(0.05, min(0.3, spike_reduction_pct))

        if spike_reduction_pct < 0.05:
            new_minutes = max(10, profile.post_meal_walk_minutes - 5)
        elif spike_reduction_pct > 0.2:
            new_minutes = min(40, profile.post_meal_walk_minutes + 5)
        else:
            new_minutes = profile.post_meal_walk_minutes

        return profile.with_updates(
            post_meal_walk_minutes=new_minutes,
            expected_walk_glucose_drop_pct=expected_drop,
        )
