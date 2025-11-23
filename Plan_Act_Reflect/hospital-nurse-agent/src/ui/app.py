# src/ui/app.py
import os
import sys

# Ensure project `src` directory is on sys.path so absolute imports like
# `infra.init_state` work when running `streamlit run src/ui/app.py`.
_HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import streamlit as st
from datetime import timedelta

from infra.init_state import initial_state
from agents.orchestration import run_plan_act_cycle, run_reflect_cycle
from models.services import ConsoleNotificationService
from models.domain import TaskStatus
from models.state import AgentState


st.set_page_config(
    page_title="Hospital Workflow Optimization Agent",
    layout="wide",
)

# Lightweight styling to make UI colorful and smoother
st.markdown(
        """
        <style>
            .task-card {border-radius:10px; padding:12px; margin-bottom:8px; background: linear-gradient(90deg,#ffffff,#f7fbff); box-shadow: 0 1px 3px rgba(0,0,0,0.06);}
            .priority {font-weight:700; color:#0057b8}
            .status-completed{color:green}
            .status-overdue{color:#d90429}
            .status-inprogress{color:#f59e0b}
        </style>
        """,
        unsafe_allow_html=True,
)

if "state" not in st.session_state:
    st.session_state.state = initial_state()

state: AgentState = st.session_state.state

# Local notification helper used by UI actions
_ui_notifier = ConsoleNotificationService()

st.title("🏥 Nurse Assistant – Workflow Optimization Agent")

# Top-level metrics
cols = st.columns(4)
with cols[0]:
    st.metric("Patients", len(state["patients"]))
with cols[1]:
    st.metric("Pending Tasks", sum(1 for t in state["tasks"] if t.status == TaskStatus.PENDING))
with cols[2]:
    st.metric("In-Progress", sum(1 for t in state["tasks"] if t.status == TaskStatus.IN_PROGRESS))
with cols[3]:
    critical_count = sum(1 for e in state["events"] if ("CRITICAL" in e) or ("escalated" in e.lower()))
    st.metric("Critical Alerts", critical_count)

# --- Controls for Plan / Act / Reflect ---
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Plan & Prioritize Tasks"):
        state = run_plan_act_cycle(state)
        st.session_state.state = state
with col2:
    if st.button("Run Act Phase Only"):
        # In this POC, plan+act are coupled;
        # but you can make a separate act-only call if needed.
        state = run_plan_act_cycle(state)
        st.session_state.state = state
with col3:
    if st.button("Run Reflect (End of Shift)"):
        state = run_reflect_cycle(state)
        st.session_state.state = state

st.markdown("---")

left, right = st.columns([2, 1])

# LEFT: Task Queue
with left:
    st.subheader("📋 Task Queue (Prioritized)")

    tasks = state["tasks"]
    if not tasks:
        st.info("No tasks yet. Click **Plan & Prioritize Tasks**.")
    else:
        for t in tasks:
            patient = state["patients"].get(t.patient_id) if t.patient_id else None
            room = patient.room if patient else "N/A"
            # Card-like container
            st.markdown(f"<div class='task-card'>", unsafe_allow_html=True)
            st.markdown(f"**{t.task_type.value.upper()}** — {t.description}")
            st.caption(
                f"Room {room} • Due: {t.due_at} • "
                f"Priority: <span class='priority'>{t.priority:.2f}</span> • Status: {t.status.value}")

            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                if st.button("✅ Mark Done", key=f"done_{t.id}"):
                    t.status = TaskStatus.COMPLETED
                    state["events"].append(f"User: completed task {t.id} for patient {t.patient_id}")
                    st.session_state.state = state
            with c2:
                if st.button("⏰ Snooze +10m", key=f"snooze_{t.id}"):
                    t.due_at = t.due_at + timedelta(minutes=10)
                    state["events"].append(f"User: snoozed task {t.id} by 10m")
                    st.session_state.state = state
            with c3:
                if st.button("⚠️ Mark Overdue", key=f"overdue_{t.id}"):
                    t.status = TaskStatus.OVERDUE
                    # Add a clear escalation event so alert detection picks this up
                    esc_msg = (
                        f"User Escalation: task {t.id} marked OVERDUE -> ESCALATION for patient {t.patient_id}"
                    )
                    state["events"].append(esc_msg)
                    # Also notify via console notification service (demo only)
                    _ui_notifier.send(
                        to_role="rapid_response_team",
                        message=(f"Escalation: patient {t.patient_id} (task {t.id}) marked overdue by user."),
                    )
                    st.session_state.state = state

            st.markdown("</div>", unsafe_allow_html=True)

# RIGHT: Alerts & Reflection
with right:
    st.subheader("🚨 Patient Alerts")
    critical_alerts = [
        e for e in state["events"]
        if ("CRITICAL" in e) or ("escalated" in e.lower()) or ("escalat" in e.lower())
    ]
    if not critical_alerts:
        st.success("No critical alerts.")
    else:
        for alert in critical_alerts[-5:]:
            st.error(alert)

    st.subheader("📊 Shift Reflection")
    reflection_events = [
        e for e in state["events"] if "Shift" in e and "summary" in e
    ]
    if reflection_events:
        st.write(reflection_events[-1])
    else:
        st.caption("No reflection run yet.")

st.subheader("🧠 Agent Events Log")
for e in reversed(state["events"][-20:]):
    st.text(e)
