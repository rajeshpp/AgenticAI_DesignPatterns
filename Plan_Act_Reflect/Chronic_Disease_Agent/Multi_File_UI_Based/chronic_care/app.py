import os
import sys
from typing import Any

import streamlit as st

# Ensure we can import the package implementation in the sibling Multi_File_Based folder
here = os.path.dirname(__file__)
chronic_agent_root = os.path.dirname(os.path.dirname(here))
multi_based = os.path.join(chronic_agent_root, "Multi_File_Based")
if os.path.isdir(os.path.join(multi_based, "chronic_care")) and multi_based not in sys.path:
    sys.path.insert(0, multi_based)

from langgraph_app import graph, CoachState

try:
    # Prefer package demo helper
    from chronic_care.demo import build_fake_yesterday
except Exception:
    # Fallback - maybe there's a local demo in this folder
    from demo import build_fake_yesterday  # type: ignore


def render_plan(plan: Any) -> None:
    st.subheader("Plan")
    st.write(f"Date: {plan.date}")
    st.write(f"Target post-meal glucose: {plan.glucose_target_range[0]}–{plan.glucose_target_range[1]} mg/dL")
    st.write(f"Post-meal walk minutes: {plan.post_meal_walk_minutes}")
    st.write(f"Walk after meals: {', '.join(plan.walk_after_meals)}")
    if plan.medication_reminders:
        st.write("Medication reminders:")
        for m in plan.medication_reminders:
            st.write(f"- {m}")
    if plan.notes:
        st.write("Notes:")
        for n in plan.notes:
            st.write(f"- {n}")


def render_actions(actions: Any) -> None:
    st.subheader("Actions")
    if not actions:
        st.write("No actions generated.")
        return
    for a in actions:
        st.markdown(f"**[{a.severity.value.upper()}]** {a.timestamp} — {a.message}")


def render_reflection(reflection: Any) -> None:
    st.subheader("Reflection")
    if reflection is None:
        st.write("No reflection available.")
        return
    st.write(f"Date: {reflection.date}")
    if reflection.spike_reduction_pct is not None:
        st.write(f"Spike reduction: {reflection.spike_reduction_pct * 100:.1f}%")
    if reflection.what_worked:
        st.write("What worked:")
        for w in reflection.what_worked:
            st.write(f"- {w}")
    if reflection.what_didnt:
        st.write("What didn't work:")
        for d in reflection.what_didnt:
            st.write(f"- {d}")


def main() -> None:
    st.title("Chronic Care Coach — LangGraph UI")

    st.sidebar.header("Simulation")
    if st.sidebar.button("Run demo simulation"):
        yesterday_state = build_fake_yesterday()

        # For the POC, show the input state briefly
        st.sidebar.subheader("Input patient")
        st.sidebar.write(yesterday_state.profile)

        initial = CoachState(
            patient_state=yesterday_state,
            live_readings=yesterday_state.glucose_readings[-2:],
        )

        result = graph.invoke(initial)

        plan = result.get("plan")
        actions = result.get("actions", [])
        reflection = result.get("reflection")
        patient_state = result.get("patient_state")

        render_plan(plan)
        render_actions(actions)
        render_reflection(reflection)

        st.subheader("Updated profile")
        st.write(patient_state.profile)

    else:
        st.write("Press 'Run demo simulation' in the sidebar to execute PLAN → ACT → REFLECT.")


if __name__ == "__main__":
    main()
