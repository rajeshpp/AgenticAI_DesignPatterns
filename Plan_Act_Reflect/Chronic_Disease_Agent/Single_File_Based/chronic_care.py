from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from statistics import mean
from typing import List, Optional, Tuple


# ---------- Domain Models ----------

@dataclass
class GlucoseReading:
    timestamp: datetime
    value_mg_dl: float  # e.g. 110


@dataclass
class BloodPressureReading:
    timestamp: datetime
    systolic: int
    diastolic: int


@dataclass
class MedicationEvent:
    timestamp: datetime
    name: str
    taken: bool


@dataclass
class MealLog:
    timestamp: datetime
    description: str
    carbs_g: float
    tag: str  # "breakfast", "lunch", "dinner", "snack"


@dataclass
class ActivityLog:
    timestamp: datetime
    minutes: int
    intensity: str  # "low", "moderate", "high"
    tag: str        # e.g. "post-meal-walk"


@dataclass
class SleepLog:
    date: datetime
    hours: float


@dataclass
class StressLog:
    date: datetime
    level_1_to_5: int  # 1 = very low, 5 = very high


@dataclass
class PatientProfile:
    id: str
    disease: str = "type2_diabetes"
    caregiver_contact: Optional[str] = None
    # Adaptive parameters that ReflectAgent can tune
    post_meal_walk_minutes: int = 20
    expected_walk_glucose_drop_pct: float = 0.15  # 15%


@dataclass
class PatientDayState:
    """
    Snapshot of 'yesterday' used for planning 'today'.
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

@dataclass
class DailyPlan:
    date: datetime
    glucose_target_range: Tuple[int, int]
    post_meal_walk_minutes: int
    walk_after_meals: List[str]  # ["lunch", "dinner"]
    medication_reminders: List[str]
    notes: List[str] = field(default_factory=list)


@dataclass
class Action:
    timestamp: datetime
    message: str
    severity: str = "info"  # "info", "warning", "critical"


@dataclass
class Reflection:
    date: datetime
    what_worked: List[str]
    what_didnt: List[str]
    spike_reduction_pct: Optional[float]
    updated_profile: PatientProfile


# ---------- Agents ----------

class PlannerAgent:
    """
    PLAN: Look at recent data and create a personalized daily plan.
    """

    def create_plan(self, state: PatientDayState) -> DailyPlan:
        today = state.glucose_readings[-1].timestamp.date() + timedelta(days=1)

        glucose_values = [g.value_mg_dl for g in state.glucose_readings]
        avg_glucose = mean(glucose_values) if glucose_values else 140

        # Basic rule-based glucose target
        if avg_glucose > 180:
            target_range = (130, 160)
        elif avg_glucose < 90:
            target_range = (100, 130)  # be cautious of hypos
        else:
            target_range = (120, 150)

        # Modify walking time based on yesterday's readings & stress/sleep
        walk_minutes = state.profile.post_meal_walk_minutes
        if avg_glucose > 180:
            walk_minutes += 5
        if state.sleep and state.sleep.hours < 6:
            walk_minutes = max(10, walk_minutes - 5)  # tired → don't push too hard
        if state.stress and state.stress.level_1_to_5 >= 4:
            walk_minutes += 5  # gentle bump for stress relief

        # Simple medication adherence check
        missed_meds = [
            m for m in state.medication_events if not m.taken
        ]
        med_reminders = []
        if missed_meds:
            med_names = sorted({m.name for m in missed_meds})
            med_reminders.append(
                f"Yesterday you missed: {', '.join(med_names)}. "
                f"Let's double-check times today."
            )

        # Recommend walking after meals where spikes were common
        risky_meals = self._detect_risky_meals(state)
        walk_after = risky_meals or ["lunch", "dinner"]

        notes = [
            f"Avg glucose yesterday: {avg_glucose:.1f} mg/dL.",
            "Try to avoid large carb loads in a single meal.",
        ]
        if state.sleep:
            notes.append(f"Sleep last night: {state.sleep.hours:.1f}h.")
        if state.stress:
            notes.append(f"Stress level: {state.stress.level_1_to_5}/5.")

        return DailyPlan(
            date=datetime.combine(today, datetime.min.time()),
            glucose_target_range=target_range,
            post_meal_walk_minutes=walk_minutes,
            walk_after_meals=walk_after,
            medication_reminders=med_reminders,
            notes=notes,
        )

    def _detect_risky_meals(self, state: PatientDayState) -> List[str]:
        """
        Naive heuristic: if avg glucose in 2h window after a meal > 180 → mark that meal tag as risky.
        """
        risky = set()
        for meal in state.meals:
            window_start = meal.timestamp
            window_end = meal.timestamp + timedelta(hours=2)
            post_meal_values = [
                g.value_mg_dl
                for g in state.glucose_readings
                if window_start <= g.timestamp <= window_end
            ]
            if post_meal_values and mean(post_meal_values) > 180:
                risky.add(meal.tag)
        return sorted(risky)


class ActAgent:
    """
    ACT: Given real-time events & the plan, suggest actions.
    """

    def handle_glucose_reading(
        self, plan: DailyPlan, reading: GlucoseReading, profile: PatientProfile
    ) -> List[Action]:
        lo, hi = plan.glucose_target_range
        actions: List[Action] = []

        if reading.value_mg_dl < 70:
            actions.append(
                Action(
                    timestamp=reading.timestamp,
                    message=(
                        f"Glucose is {reading.value_mg_dl:.0f} mg/dL (low). "
                        "Consider fast-acting carbs and recheck in 15 minutes. "
                        "If you feel unwell, contact your doctor or emergency services."
                    ),
                    severity="critical",
                )
            )
        elif reading.value_mg_dl > hi:
            # coach a short walk if near term.
            walk_minutes = profile.post_meal_walk_minutes
            actions.append(
                Action(
                    timestamp=reading.timestamp,
                    message=(
                        f"Glucose is {reading.value_mg_dl:.0f} mg/dL, above your target "
                        f"({lo}–{hi}). Take a {walk_minutes}-minute walk now "
                        "if it's safe, and choose a lower-carb option for your next meal."
                    ),
                    severity="warning",
                )
            )

            if reading.value_mg_dl > 250 and profile.caregiver_contact:
                actions.append(
                    Action(
                        timestamp=reading.timestamp,
                        message=(
                            "Glucose is very high. Consider informing your caregiver "
                            f"({profile.caregiver_contact}) and following your "
                            "emergency plan if you have one."
                        ),
                        severity="critical",
                    )
                )
        else:
            actions.append(
                Action(
                    timestamp=reading.timestamp,
                    message=(
                        f"Nice! Glucose {reading.value_mg_dl:.0f} mg/dL is within target "
                        f"({lo}–{hi}). Keep up the current routine."
                    ),
                    severity="info",
                )
            )
        return actions

    def reminder_before_meal(self, plan: DailyPlan, meal_tag: str) -> Action:
        if meal_tag in plan.walk_after_meals:
            msg = (
                f"Before {meal_tag}, aim for a balanced plate and be ready "
                f"for a {plan.post_meal_walk_minutes}-minute walk afterwards."
            )
        else:
            msg = f"Before {meal_tag}, keep carbs moderate and stick to your plan."
        return Action(timestamp=datetime.now(), message=msg)


class ReflectAgent:
    """
    REFLECT: End-of-day analysis & parameter update.
    """

    def reflect(
        self,
        state: PatientDayState,
        plan: DailyPlan,
    ) -> Reflection:
        # Simple: compare post-meal spikes on meals with a walk vs without
        with_walk, without_walk = self._collect_post_meal_spikes(state)

        def avg_or_none(values: List[float]) -> Optional[float]:
            return mean(values) if values else None

        avg_with = avg_or_none(with_walk)
        avg_without = avg_or_none(without_walk)

        spike_reduction_pct: Optional[float] = None
        what_worked: List[str] = []
        what_didnt: List[str] = []

        if avg_with is not None and avg_without is not None and avg_without > 0:
            spike_reduction_pct = (avg_without - avg_with) / avg_without
            if spike_reduction_pct > 0.1:
                what_worked.append(
                    f"Post-meal walks reduced average glucose spikes by "
                    f"{spike_reduction_pct * 100:.1f}%."
                )
            else:
                what_didnt.append(
                    "Post-meal walks did not significantly reduce glucose spikes today."
                )

        # Update personalization: if walks are effective, we can keep or slightly
        # increase expectations; if not, maybe reduce.
        updated_profile = PatientProfile(**vars(state.profile))
        if spike_reduction_pct is not None:
            updated_profile.expected_walk_glucose_drop_pct = max(
                0.05, min(0.3, spike_reduction_pct)
            )
            if spike_reduction_pct < 0.05:
                updated_profile.post_meal_walk_minutes = max(
                    10, updated_profile.post_meal_walk_minutes - 5
                )
            elif spike_reduction_pct > 0.2:
                updated_profile.post_meal_walk_minutes = min(
                    40, updated_profile.post_meal_walk_minutes + 5
                )

        # Generic comments
        avg_glucose = mean([g.value_mg_dl for g in state.glucose_readings])
        if avg_glucose > 180:
            what_didnt.append(
                f"Average glucose was still high at {avg_glucose:.1f} mg/dL."
            )
        else:
            what_worked.append(
                f"Average glucose was acceptable at {avg_glucose:.1f} mg/dL."
            )

        return Reflection(
            date=datetime.combine(state.glucose_readings[-1].timestamp.date(), datetime.min.time()),
            what_worked=what_worked,
            what_didnt=what_didnt,
            spike_reduction_pct=spike_reduction_pct,
            updated_profile=updated_profile,
        )

    def _collect_post_meal_spikes(
        self, state: PatientDayState
    ) -> Tuple[List[float], List[float]]:
        with_walk: List[float] = []
        without_walk: List[float] = []

        for meal in state.meals:
            window_start = meal.timestamp
            window_end = meal.timestamp + timedelta(hours=2)
            readings = [
                g.value_mg_dl
                for g in state.glucose_readings
                if window_start <= g.timestamp <= window_end
            ]
            if not readings:
                continue
            baseline = [
                g.value_mg_dl
                for g in state.glucose_readings
                if window_start - timedelta(minutes=30)
                <= g.timestamp
                < window_start
            ]
            if not baseline:
                continue

            spike = mean(readings) - mean(baseline)

            # Did the patient walk after this meal?
            walked = any(
                a.tag == "post-meal-walk"
                and meal.timestamp <= a.timestamp <= meal.timestamp + timedelta(hours=2)
                for a in state.activities
            )
            if walked:
                with_walk.append(spike)
            else:
                without_walk.append(spike)

        return with_walk, without_walk


# ---------- Orchestrator / POC Simulation ----------

class ChronicCareCoach:
    def __init__(self, profile: PatientProfile):
        self.profile = profile
        self.planner = PlannerAgent()
        self.actor = ActAgent()
        self.reflector = ReflectAgent()

    def run_day(self, yesterday_state: PatientDayState) -> None:
        print("\n=== PLAN ===")
        plan = self.planner.create_plan(yesterday_state)
        self._print_plan(plan)

        print("\n=== ACT (example events) ===")
        # Simulate a couple of readings to show behavior
        example_readings = [
            GlucoseReading(
                timestamp=datetime.now().replace(hour=9, minute=0),
                value_mg_dl=135,
            ),
            GlucoseReading(
                timestamp=datetime.now().replace(hour=14, minute=30),
                value_mg_dl=210,
            ),
        ]
        for r in example_readings:
            actions = self.actor.handle_glucose_reading(plan, r, self.profile)
            for a in actions:
                print(f"[{a.severity.upper()}] {a.timestamp.time()} - {a.message}")

        # End of day reflection
        print("\n=== REFLECT ===")
        reflection = self.reflector.reflect(yesterday_state, plan)
        self.profile = reflection.updated_profile  # update for next day
        self._print_reflection(reflection)

    @staticmethod
    def _print_plan(plan: DailyPlan) -> None:
        print(f"Date: {plan.date.date()}")
        lo, hi = plan.glucose_target_range
        print(f"- Target post-meal glucose: {lo}–{hi} mg/dL")
        print(f"- Post-meal walk minutes: {plan.post_meal_walk_minutes}")
        print(f"- Walk after meals: {', '.join(plan.walk_after_meals)}")
        for m in plan.medication_reminders:
            print(f"- Med reminder: {m}")
        for note in plan.notes:
            print(f"- Note: {note}")

    @staticmethod
    def _print_reflection(reflection: Reflection) -> None:
        print(f"Date reflected: {reflection.date.date()}")
        if reflection.spike_reduction_pct is not None:
            print(
                f"- Spike reduction from walks: "
                f"{reflection.spike_reduction_pct * 100:.1f}%"
            )
        if reflection.what_worked:
            print("- What worked:")
            for w in reflection.what_worked:
                print(f"  • {w}")
        if reflection.what_didnt:
            print("- What didn't work:")
            for w in reflection.what_didnt:
                print(f"  • {w}")
        print(
            f"- Updated walk minutes: "
            f"{reflection.updated_profile.post_meal_walk_minutes}"
        )
        print(
            f"- Expected walk effect: "
            f"{reflection.updated_profile.expected_walk_glucose_drop_pct * 100:.1f}%"
        )


# ---------- Quick fake data + demo ----------

def _fake_yesterday_state() -> PatientDayState:
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    readings = [
        GlucoseReading(timestamp=now + timedelta(hours=h), value_mg_dl=v)
        for h, v in [
            (7, 115),
            (9, 160),
            (11, 190),
            (13, 175),
            (15, 185),
            (18, 200),
            (21, 170),
        ]
    ]
    meals = [
        MealLog(
            timestamp=now + timedelta(hours=8),
            description="Idli + chutney",
            carbs_g=45,
            tag="breakfast",
        ),
        MealLog(
            timestamp=now + timedelta(hours=13),
            description="Rice + dal + sabzi",
            carbs_g=70,
            tag="lunch",
        ),
        MealLog(
            timestamp=now + timedelta(hours=20),
            description="Chapati + curry",
            carbs_g=60,
            tag="dinner",
        ),
    ]
    activities = [
        ActivityLog(
            timestamp=now + timedelta(hours=14),
            minutes=20,
            intensity="moderate",
            tag="post-meal-walk",
        ),
        # No walk after dinner to demonstrate comparison
    ]

    meds = [
        MedicationEvent(timestamp=now + timedelta(hours=7), name="Metformin", taken=True),
        MedicationEvent(timestamp=now + timedelta(hours=19), name="Metformin", taken=False),
    ]

    bp = [
        BloodPressureReading(
            timestamp=now + timedelta(hours=9),
            systolic=130,
            diastolic=85,
        )
    ]

    sleep = SleepLog(date=now - timedelta(days=1), hours=6.5)
    stress = StressLog(date=now - timedelta(days=1), level_1_to_5=3)

    profile = PatientProfile(
        id="patient-001",
        caregiver_contact="+91-99999-99999",
    )

    return PatientDayState(
        profile=profile,
        glucose_readings=readings,
        bp_readings=bp,
        medication_events=meds,
        meals=meals,
        activities=activities,
        sleep=sleep,
        stress=stress,
    )


if __name__ == "__main__":
    """
    DISCLAIMER: This is a toy demo, not medical advice and not suitable
    for clinical use. Thresholds and logic are oversimplified.
    """
    yesterday = _fake_yesterday_state()
    coach = ChronicCareCoach(profile=yesterday.profile)
    coach.run_day(yesterday)
