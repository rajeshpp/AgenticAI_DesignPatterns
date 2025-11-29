from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import Enum
from typing import Callable, List, Optional
import random
import statistics


# ========= Domain Models =========

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class RoutineWindow:
    """Represents a period of the day with an expected routine."""
    name: str
    start: time
    end: time
    is_high_risk: bool = False  # e.g. night-time bathroom visit window
    max_minutes_without_movement: int = 90
    ideal_systolic_bp_range: tuple[int, int] = (100, 140)
    ideal_diastolic_bp_range: tuple[int, int] = (60, 90)


@dataclass
class ElderProfile:
    name: str
    age: int
    routine_windows: List[RoutineWindow] = field(default_factory=list)


@dataclass
class SensorReading:
    """
    Simplified multi-sensor reading.
    In real life this might come from multiple devices, MQTT, etc.
    """
    timestamp: datetime
    has_movement: bool
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    used_kitchen_appliance: bool = False
    fall_detected: bool = False


@dataclass
class Alert:
    timestamp: datetime
    level: AlertLevel
    message: str
    details: dict
    context_window: Optional[RoutineWindow] = None


# ========= PLAN MODULE =========

class Planner:
    """
    PLAN:
    - Understand daily routine from ElderProfile
    - Given a timestamp, identify the current routine window and risk level
    """

    def __init__(self, profile: ElderProfile):
        self.profile = profile

    def get_current_window(self, ts: datetime) -> Optional[RoutineWindow]:
        now_t = ts.time()
        for w in self.profile.routine_windows:
            if w.start <= now_t < w.end:
                return w
        return None

    def is_risk_time(self, ts: datetime) -> bool:
        window = self.get_current_window(ts)
        return bool(window and window.is_high_risk)


# ========= ACT MODULE =========

class Actor:
    """
    ACT:
    - Monitor readings
    - Detect anomalies (falls, high BP, missed meals, no movement)
    - Send notifications / give instructions
    """

    def __init__(
        self,
        planner: Planner,
        notify_family: Callable[[Alert], None],
        instruct_elder: Callable[[Alert], None],
        movement_grace_period_minutes: int = 120,
    ):
        self.planner = planner
        self.notify_family = notify_family
        self.instruct_elder = instruct_elder

        # state for missed-movement / missed-meal logic
        self.last_movement_time: Optional[datetime] = None
        self.last_kitchen_use_time: Optional[datetime] = None
        self.movement_grace_period = timedelta(minutes=movement_grace_period_minutes)

    def act_on_reading(self, reading: SensorReading) -> List[Alert]:
        alerts: List[Alert] = []
        context_window = self.planner.get_current_window(reading.timestamp)

        # Update basic state
        if reading.has_movement:
            self.last_movement_time = reading.timestamp
        if reading.used_kitchen_appliance:
            self.last_kitchen_use_time = reading.timestamp

        # 1) Fall detection (immediate critical)
        if reading.fall_detected:
            alerts.append(self._raise_alert(
                level=AlertLevel.CRITICAL,
                message="Possible fall detected!",
                reading=reading,
                context_window=context_window,
                details={"type": "fall"}
            ))

        # 2) High blood pressure
        if reading.systolic_bp and reading.diastolic_bp and context_window:
            sys_low, sys_high = context_window.ideal_systolic_bp_range
            dia_low, dia_high = context_window.ideal_diastolic_bp_range
            if reading.systolic_bp > sys_high or reading.diastolic_bp > dia_high:
                level = AlertLevel.WARNING
                if self.planner.is_risk_time(reading.timestamp):
                    level = AlertLevel.CRITICAL

                alerts.append(self._raise_alert(
                    level=level,
                    message="Blood pressure above expected range.",
                    reading=reading,
                    context_window=context_window,
                    details={
                        "type": "high_bp",
                        "systolic": reading.systolic_bp,
                        "diastolic": reading.diastolic_bp,
                        "expected_sys": (sys_low, sys_high),
                        "expected_dia": (dia_low, dia_high),
                    }
                ))

        # 3) Prolonged no movement
        if self.last_movement_time and context_window:
            since_move = reading.timestamp - self.last_movement_time
            max_allowed = timedelta(
                minutes=min(
                    context_window.max_minutes_without_movement,
                    self.movement_grace_period.total_seconds() // 60,
                )
            )
            if since_move > max_allowed:
                alerts.append(self._raise_alert(
                    level=AlertLevel.WARNING,
                    message="Unusual lack of movement detected.",
                    reading=reading,
                    context_window=context_window,
                    details={
                        "type": "no_movement",
                        "minutes_since_movement": since_move.total_seconds() / 60,
                    }
                ))

        # 4) Missed meals (simplified: no kitchen use in lunch/dinner windows)
        if context_window and "meal" in context_window.name.lower():
            if (
                self.last_kitchen_use_time is None
                or self.last_kitchen_use_time < datetime.combine(
                    reading.timestamp.date(), context_window.start
                )
            ):
                # nearing end of meal window, but no kitchen usage
                time_left = datetime.combine(
                    reading.timestamp.date(), context_window.end
                ) - reading.timestamp

                if time_left < timedelta(minutes=15):
                    alerts.append(self._raise_alert(
                        level=AlertLevel.INFO,
                        message="Possible missed meal. No kitchen usage detected.",
                        reading=reading,
                        context_window=context_window,
                        details={"type": "missed_meal"}
                    ))

        return alerts

    def _raise_alert(
        self,
        level: AlertLevel,
        message: str,
        reading: SensorReading,
        context_window: Optional[RoutineWindow],
        details: dict,
    ) -> Alert:
        alert = Alert(
            timestamp=reading.timestamp,
            level=level,
            message=message,
            details=details,
            context_window=context_window,
        )

        # Notify “family”
        self.notify_family(alert)

        # Give “instructions” to elder (in real life: voice assistant, etc.)
        self.instruct_elder(alert)

        return alert


# ========= REFLECT MODULE =========

@dataclass
class IncidentFeedback:
    alert: Alert
    was_useful: bool  # True if family confirmed it was a valid alert


class Reflector:
    """
    REFLECT:
    - Log incidents
    - Learn from feedback to adjust sensitivity and reduce false positives
    """

    def __init__(self, actor: Actor):
        self.actor = actor
        self.feedback_history: List[IncidentFeedback] = []

    def record_feedback(self, feedback: IncidentFeedback) -> None:
        self.feedback_history.append(feedback)
        self._maybe_adjust_sensitivity()

    def _maybe_adjust_sensitivity(self) -> None:
        # Simple heuristic:
        # If last N alerts are mostly false positives, relax sensitivity a bit.
        N = 10
        if len(self.feedback_history) < N:
            return

        recent = self.feedback_history[-N:]
        false_positive_rate = sum(
            1 for fb in recent if not fb.was_useful
        ) / N

        # Example adaptation: adjust movement grace period
        if false_positive_rate > 0.7:
            # too many false positives -> relax movement sensitivity
            old = self.actor.movement_grace_period
            self.actor.movement_grace_period += timedelta(minutes=15)
            print(
                f"[REFLECT] High false-positive rate ({false_positive_rate:.0%}). "
                f"Increasing movement grace from {old} to {self.actor.movement_grace_period}."
            )
        elif false_positive_rate < 0.2:
            # very few false positives -> can be more sensitive
            old = self.actor.movement_grace_period
            self.actor.movement_grace_period = max(
                timedelta(minutes=30),
                self.actor.movement_grace_period - timedelta(minutes=15),
            )
            print(
                f"[REFLECT] Low false-positive rate ({false_positive_rate:.0%}). "
                f"Decreasing movement grace from {old} to {self.actor.movement_grace_period}."
            )


# ========= Orchestrating Agent =========

class HomeCareAgent:
    """
    Glues PLAN -> ACT -> REFLECT into a single agent.
    Now also prints explicit PLAN / ACT / REFLECT sections per reading.
    """

    def __init__(
        self,
        profile: ElderProfile,
        notify_family: Callable[[Alert], None],
        instruct_elder: Callable[[Alert], None],
    ):
        self.planner = Planner(profile)
        self.actor = Actor(self.planner, notify_family, instruct_elder)
        self.reflector = Reflector(self.actor)

    def handle_reading(self, reading: SensorReading) -> None:
        # === PLAN ===
        import time
        time.sleep(3)
        print("\n" + "=" * 80)
        print(f"TIME: {reading.timestamp.isoformat()}")
        print("=== PLAN: Understand routine & risk ===")
        window = self.planner.get_current_window(reading.timestamp)
        is_risk = self.planner.is_risk_time(reading.timestamp)

        if window:
            print(
                f"Current window: {window.name} | "
                f"High risk: {window.is_high_risk} | "
                f"Max minutes w/o movement: {window.max_minutes_without_movement}"
            )
        else:
            print("Current window: NONE (outside configured routine).")

        print(f"Is risk time? {is_risk}")

        # === ACT ===
        print("\n=== ACT: Process sensors & generate alerts ===")
        print(
            f"SensorReading(movement={reading.has_movement}, "
            f"BP={reading.systolic_bp}/{reading.diastolic_bp}, "
            f"kitchen_used={reading.used_kitchen_appliance}, "
            f"fall={reading.fall_detected})"
        )

        alerts = self.actor.act_on_reading(reading)

        if not alerts:
            print("No alerts generated for this reading.")

        # === REFLECT ===
        if alerts:
            print("\n=== REFLECT: Learn from incidents & adjust sensitivity ===")
        for alert in alerts:
            was_useful = self._simulate_family_feedback(alert)
            print(
                f"Feedback on alert [{alert.level.value.upper()} | {alert.details.get('type')}]: "
                f"{'USEFUL' if was_useful else 'NOT USEFUL'}"
            )
            self.reflector.record_feedback(IncidentFeedback(alert, was_useful))

        # Just to show current sensitivity
        print(
            f"Current movement grace period: {self.actor.movement_grace_period}"
        )

    @staticmethod
    def _simulate_family_feedback(alert: Alert) -> bool:
        """
        POC only: mock feedback.
        Assume critical alerts are usually useful, minor ones less so.
        """
        base_prob = {
            AlertLevel.CRITICAL: 0.9,
            AlertLevel.WARNING: 0.6,
            AlertLevel.INFO: 0.4,
        }[alert.level]
        return random.random() < base_prob



# ========= Example Notification Handlers =========

def print_family_notification(alert: Alert) -> None:
    ctx = f" ({alert.context_window.name})" if alert.context_window else ""
    print(
        f"[FAMILY NOTIFY] {alert.timestamp.isoformat()} "
        f"[{alert.level.value.upper()}]{ctx}: {alert.message} | details={alert.details}"
    )


def print_elder_instructions(alert: Alert) -> None:
    # Super simple; in reality this could be converted to spoken instructions.
    msg = {
        "fall": "Please stay still if you can and wait for help.",
        "high_bp": "Please sit down, relax, and take a few deep breaths.",
        "no_movement": "Please move around a bit if you are able.",
        "missed_meal": "It might be time to have a meal or snack.",
    }.get(alert.details.get("type"), "Please take care and follow your usual safety steps.")

    print(f"[ELDER INSTRUCTION] {msg}")


# ========= POC Simulation =========

def build_sample_profile() -> ElderProfile:
    return ElderProfile(
        name="Grandma",
        age=78,
        routine_windows=[
            RoutineWindow(
                name="Morning Routine",
                start=time(6, 0),
                end=time(9, 0),
                is_high_risk=True,  # e.g., getting out of bed
                max_minutes_without_movement=45,
            ),
            RoutineWindow(
                name="Lunch Meal Window",
                start=time(12, 0),
                end=time(13, 30),
                max_minutes_without_movement=120,
            ),
            RoutineWindow(
                name="Afternoon Rest",
                start=time(14, 0),
                end=time(16, 0),
                max_minutes_without_movement=120,
            ),
            RoutineWindow(
                name="Dinner Meal Window",
                start=time(19, 0),
                end=time(20, 30),
            ),
            RoutineWindow(
                name="Night Time",
                start=time(22, 0),
                end=time(23, 59),
                is_high_risk=True,  # bathroom trips etc.
                max_minutes_without_movement=180,
            ),
        ],
    )


def simulate_sensor_reading(base_time: datetime) -> SensorReading:
    """
    Very rough random simulator for demo purposes.
    """
    has_movement = random.random() < 0.7

    # Blood pressure: mostly normal with occasional spikes
    systolic = int(random.normalvariate(130, 10))
    diastolic = int(random.normalvariate(80, 8))

    # Small chance of serious spike
    if random.random() < 0.05:
        systolic += 40
        diastolic += 20

    used_kitchen = random.random() < 0.1

    # Tiny chance of fall
    fall = random.random() < 0.01

    return SensorReading(
        timestamp=base_time,
        has_movement=has_movement,
        systolic_bp=systolic,
        diastolic_bp=diastolic,
        used_kitchen_appliance=used_kitchen,
        fall_detected=fall,
    )


def run_poc_simulation(num_steps: int = 60) -> None:
    profile = build_sample_profile()
    agent = HomeCareAgent(profile, print_family_notification, print_elder_instructions)

    start = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
    step = timedelta(minutes=15)

    for i in range(num_steps):
        ts = start + i * step
        reading = simulate_sensor_reading(ts)
        agent.handle_reading(reading)


if __name__ == "__main__":
    run_poc_simulation(num_steps=80)
