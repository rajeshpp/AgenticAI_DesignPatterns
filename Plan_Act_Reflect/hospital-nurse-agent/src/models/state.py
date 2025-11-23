# src/models/state.py
from typing import Dict, List, TypedDict
from .domain import Patient, VitalReading, NursePreferences, Task


class AgentState(TypedDict):
    patients: Dict[str, Patient]
    vitals: List[VitalReading]
    tasks: List[Task]
    nurse_prefs: Dict[str, NursePreferences]
    events: List[str]
    shift_id: str
