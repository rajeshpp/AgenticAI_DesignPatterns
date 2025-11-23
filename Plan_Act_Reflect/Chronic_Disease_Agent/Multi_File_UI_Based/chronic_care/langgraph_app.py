# langgraph_app.py
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import List, Optional

from langgraph.graph import StateGraph, START, END  # type: ignore

from chronic_care.orchestrator import ChronicCareCoach, default_coach
from chronic_care.models import (
    Action,
    DailyPlan,
    GlucoseReading,
    PatientDayState,
    Reflection,
)


# ---------- Graph State (what flows between nodes) ----------

@dataclass
class CoachState:
    """
    LangGraph state schema.

    This is what you will see in the LangGraph UI as state flowing across:
    PLAN → ACT → REFLECT
    """
    patient_state: PatientDayState
    live_readings: List[GlucoseReading] = field(default_factory=list)

    plan: Optional[DailyPlan] = None
    actions: List[Action] = field(default_factory=list)
    reflection: Optional[Reflection] = None

    def with_updates(
        self,
        *,
        plan: Optional[DailyPlan] | None = None,
        actions: Optional[List[Action]] | None = None,
        reflection: Optional[Reflection] | None = None,
        patient_state: Optional[PatientDayState] | None = None,
    ) -> "CoachState":
        """Immutable-ish helper, returns a new updated state."""
        return replace(
            self,
            plan=self.plan if plan is None else plan,
            actions=self.actions if actions is None else actions,
            reflection=self.reflection if reflection is None else reflection,
            patient_state=self.patient_state if patient_state is None else patient_state,
        )


# ---------- Node implementations (PLAN / ACT / REFLECT) ----------

def _build_coach(state: CoachState) -> ChronicCareCoach:
    """
    Construct a coach from the current profile in state.

    In a more advanced setup, you'd keep the coach in state or persist
    it between runs, but for this POC we re-create it per node.
    """
    return default_coach(profile=state.patient_state.profile)


def plan_node(state: CoachState) -> dict:
    """
    PLAN node.

    Takes yesterday's PatientDayState and produces a DailyPlan.
    """
    coach = _build_coach(state)
    plan = coach.plan_day(state.patient_state)
    # Return partial state update, LangGraph merges this.
    return {"plan": plan}


def act_node(state: CoachState) -> dict:
    """
    ACT node.

    Uses the DailyPlan + live glucose readings to generate actions.
    For the POC, we assume live_readings is already populated in state.
    """
    if state.plan is None:
        # In a robust app, you'd raise or branch; here we just no-op.
        return {}

    coach = _build_coach(state)
    actions = coach.act_on_readings(state.plan, state.live_readings)
    return {"actions": actions}


def reflect_node(state: CoachState) -> dict:
    """
    REFLECT node.

    Uses yesterday's PatientDayState + the plan to analyze what worked
    and update the personalization profile.
    """
    if state.plan is None:
        return {}

    coach = _build_coach(state)
    reflection = coach.reflect_on_day(state.patient_state, state.plan)

    # Update the profile inside patient_state using reflection.updated_profile
    updated_patient_state = replace(
        state.patient_state,
        profile=reflection.updated_profile,
    )

    return {
        "reflection": reflection,
        "patient_state": updated_patient_state,
    }


# ---------- Build the LangGraph graph ----------

def build_graph() -> "StateGraph[CoachState]":
    builder: StateGraph[CoachState] = StateGraph(CoachState)

    builder.add_node("plan", plan_node)
    builder.add_node("act", act_node)
    builder.add_node("reflect", reflect_node)

    builder.add_edge(START, "plan")
    builder.add_edge("plan", "act")
    builder.add_edge("act", "reflect")
    builder.add_edge("reflect", END)

    return builder


# Compile the graph once at import time.
builder = build_graph()
graph = builder.compile()


# Convenience function for programmatic use (e.g. tests, notebooks)
def run_once(initial_state: CoachState) -> CoachState:
    """
    Run PLAN → ACT → REFLECT once and return final state.
    """
    result_dict = graph.invoke(initial_state)
    # LangGraph returns a dict matching our state schema; we convert back.
    return CoachState(**result_dict)
