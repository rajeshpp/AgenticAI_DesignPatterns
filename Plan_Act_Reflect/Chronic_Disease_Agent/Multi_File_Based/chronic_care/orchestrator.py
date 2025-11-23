# chronic_care/orchestrator.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List

from .agents import AgentContext, PlannerAgent, ActAgent, ReflectAgent
from .models import (
    Action,
    DailyPlan,
    GlucoseReading,
    PatientDayState,
    PatientProfile,
    Reflection,
)


@dataclass
class ChronicCareCoach:
    """
    High-level orchestrator showing the PLAN → ACT → REFLECT loop explicitly.

    This encapsulates how the three agents collaborate on a daily cycle.
    """

    profile: PatientProfile
    context: AgentContext

    def __post_init__(self) -> None:
        self._planner = PlannerAgent(self.context)
        self._actor = ActAgent(self.context)
        self._reflector = ReflectAgent(self.context)

    # ---------- PLAN ----------

    def plan_day(self, yesterday_state: PatientDayState) -> DailyPlan:
        return self._planner.create_plan(yesterday_state)

    # ---------- ACT ----------

    def act_on_readings(
        self,
        plan: DailyPlan,
        readings: Iterable[GlucoseReading],
    ) -> List[Action]:
        actions: List[Action] = []

        for reading in readings:
            actions.extend(
                self._actor.handle_glucose_reading(plan, reading, self.profile)
            )

        return actions

    # ---------- REFLECT ----------

    def reflect_on_day(
        self,
        yesterday_state: PatientDayState,
        plan: DailyPlan,
    ) -> Reflection:
        reflection = self._reflector.reflect(yesterday_state, plan)
        # Update internal profile for the next cycle (closed loop)
        self.profile = reflection.updated_profile
        return reflection


def default_coach(profile: PatientProfile) -> ChronicCareCoach:
    """
    Convenience constructor with a default AgentContext (now = current time).
    """
    context = AgentContext(now=datetime.now())
    return ChronicCareCoach(profile=profile, context=context)
