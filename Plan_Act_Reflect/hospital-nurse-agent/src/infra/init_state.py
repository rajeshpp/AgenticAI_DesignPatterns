# src/infra/init_state.py
from datetime import datetime, timedelta
from typing import Dict, List

from models.domain import Patient, VitalReading, NursePreferences, Task
from models.state import AgentState


def initial_state() -> AgentState:
    now = datetime.utcnow()
    # Add a few synthetic patients for visibility in the demo
    patients: Dict[str, Patient] = {
        "P1": Patient(id="P1", name="John Doe", room="204", risk_score=0.7),
        "P2": Patient(id="P2", name="Jane Smith", room="210", risk_score=0.4),
        "P3": Patient(id="P3", name="Carlos Ruiz", room="215", risk_score=0.9),
        "P4": Patient(id="P4", name="Aiko Tanaka", room="222", risk_score=0.2),
    }

    # Vitals include some elevated/critical readings so the app shows alerts and tasks
    vitals: List[VitalReading] = [
        # slightly abnormal for P1 -> will create a task
        VitalReading("P1", now - timedelta(minutes=10), heart_rate=115, spo2=90,
                     systolic_bp=88, diastolic_bp=60),
        # normal for P2
        VitalReading("P2", now - timedelta(minutes=5), heart_rate=92, spo2=95,
                     systolic_bp=120, diastolic_bp=80),
        # critical for P3 -> should trigger escalation alert
        VitalReading("P3", now - timedelta(minutes=2), heart_rate=130, spo2=82,
                     systolic_bp=72, diastolic_bp=48),
        # low-risk patient P4
        VitalReading("P4", now - timedelta(minutes=15), heart_rate=78, spo2=98,
                     systolic_bp=118, diastolic_bp=76),
    ]

    tasks: List[Task] = []  # start empty; Planner will generate

    nurse_prefs: Dict[str, NursePreferences] = {
        "N1": NursePreferences(nurse_id="N1"),
    }

    state: AgentState = {
        "patients": patients,
        "vitals": vitals,
        "tasks": tasks,
        "nurse_prefs": nurse_prefs,
        "events": ["System: Initialized demo state."],
        "shift_id": "SHIFT-001",
    }
    return state
