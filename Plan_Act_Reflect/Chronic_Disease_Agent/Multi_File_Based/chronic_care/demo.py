# demo.py
from __future__ import annotations

from datetime import datetime, timedelta

try:
    # Preferred when running as a package: `python -m chronic_care.demo`
    from chronic_care import ChronicCareCoach, default_coach
    from chronic_care.models import (
        ActivityLog,
        BloodPressureReading,
        GlucoseReading,
        MealLog,
        MedicationEvent,
        PatientDayState,
        PatientProfile,
        SleepLog,
        StressLog,
    )
except Exception:
    # Fallback when running the file directly inside the package folder: `python demo.py`
    # Ensure the parent directory is on sys.path so `import chronic_care` works.
    import os
    import sys

    parent = os.path.dirname(os.path.dirname(__file__))
    if parent not in sys.path:
        sys.path.insert(0, parent)

    from chronic_care import ChronicCareCoach, default_coach
    from chronic_care.models import (
        ActivityLog,
        BloodPressureReading,
        GlucoseReading,
        MealLog,
        MedicationEvent,
        PatientDayState,
        PatientProfile,
        SleepLog,
        StressLog,
    )


def build_fake_yesterday() -> PatientDayState:
    """Create a small, realistic test day."""
    day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    glucose_readings = [
        GlucoseReading(timestamp=day_start + timedelta(hours=h), value_mg_dl=v)
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
            timestamp=day_start + timedelta(hours=8),
            description="Idli + chutney",
            carbs_g=45,
            tag="breakfast",
        ),
        MealLog(
            timestamp=day_start + timedelta(hours=13),
            description="Rice + dal + sabzi",
            carbs_g=70,
            tag="lunch",
        ),
        MealLog(
            timestamp=day_start + timedelta(hours=20),
            description="Chapati + curry",
            carbs_g=60,
            tag="dinner",
        ),
    ]

    activities = [
        ActivityLog(
            timestamp=day_start + timedelta(hours=14),
            minutes=20,
            intensity="moderate",
            tag="post-meal-walk",
        ),
        # No walk after dinner → contrast in reflection
    ]

    medication_events = [
        MedicationEvent(
            timestamp=day_start + timedelta(hours=7),
            name="Metformin",
            taken=True,
        ),
        MedicationEvent(
            timestamp=day_start + timedelta(hours=19),
            name="Metformin",
            taken=False,
        ),
    ]

    bp_readings = [
        BloodPressureReading(
            timestamp=day_start + timedelta(hours=9),
            systolic=130,
            diastolic=85,
        )
    ]

    sleep = SleepLog(date=day_start - timedelta(days=1), hours=6.5)
    stress = StressLog(date=day_start - timedelta(days=1), level_1_to_5=3)

    profile = PatientProfile(
        id="patient-001",
        caregiver_contact="+91-99999-99999",
    )

    return PatientDayState(
        profile=profile,
        glucose_readings=glucose_readings,
        bp_readings=bp_readings,
        medication_events=medication_events,
        meals=meals,
        activities=activities,
        sleep=sleep,
        stress=stress,
    )


def main() -> None:
    """
    Minimal, console-based demonstration.

    Shows the agentic PLAN → ACT → REFLECT loop clearly.
    """
    yesterday_state = build_fake_yesterday()
    coach = default_coach(profile=yesterday_state.profile)

    # PLAN
    print("\n=== PLAN ===")
    plan = coach.plan_day(yesterday_state)
    print(f"Plan date: {plan.date.date()}")
    print(f"Target post-meal glucose: {plan.glucose_target_range[0]}–{plan.glucose_target_range[1]} mg/dL")
    print(f"Post-meal walk minutes: {plan.post_meal_walk_minutes}")
    print(f"Walk after meals: {', '.join(plan.walk_after_meals)}")
    for reminder in plan.medication_reminders:
        print(f"Medication reminder: {reminder}")
    for note in plan.notes:
        print(f"Note: {note}")

    # ACT (simulate a couple of real-time readings)
    print("\n=== ACT (example readings) ===")
    example_readings = [
        GlucoseReading(
            timestamp=yesterday_state.glucose_readings[0].timestamp + timedelta(days=1, hours=9),
            value_mg_dl=135,
        ),
        GlucoseReading(
            timestamp=yesterday_state.glucose_readings[0].timestamp + timedelta(days=1, hours=14, minutes=30),
            value_mg_dl=210,
        ),
    ]
    actions = coach.act_on_readings(plan, example_readings)
    for action in actions:
        print(f"[{action.severity.value.upper()}] {action.timestamp.time()} - {action.message}")

    # REFLECT
    print("\n=== REFLECT ===")
    reflection = coach.reflect_on_day(yesterday_state, plan)
    print(f"Reflection date: {reflection.date.date()}")
    if reflection.spike_reduction_pct is not None:
        print(
            f"Spike reduction from walks: {reflection.spike_reduction_pct * 100:.1f}%"
        )
    if reflection.what_worked:
        print("What worked:")
        for item in reflection.what_worked:
            print(f"  • {item}")
    if reflection.what_didnt:
        print("What didn't work:")
        for item in reflection.what_didnt:
            print(f"  • {item}")

    print("\nUpdated personalization:")
    print(f"- Post-meal walk minutes: {coach.profile.post_meal_walk_minutes}")
    print(
        f"- Expected walk effect: "
        f"{coach.profile.expected_walk_glucose_drop_pct * 100:.1f}%"
    )

    print(
        "\nDISCLAIMER: This is a toy POC for demonstration only, "
        "not medical advice or a clinical decision support tool."
    )


if __name__ == "__main__":
    main()
