# src/agents/reflect.py
from typing import Dict

from models.domain import TaskStatus, TaskType, NursePreferences
from models.state import AgentState


class ReflectAgent:
    def reflect(self, state: AgentState) -> AgentState:
        tasks = state["tasks"]
        completed = [t for t in tasks if t.status == TaskStatus.COMPLETED]
        overdue = [t for t in tasks if t.status == TaskStatus.OVERDUE]

        total = len(tasks)
        completion_rate = len(completed) / total if total else 0
        overdue_rate = len(overdue) / total if total else 0

        duration_by_type = {
            TaskType.CHECK_VITALS: 5,
            TaskType.MEDICATION: 7,
            TaskType.DOCUMENTATION: 4,
            TaskType.ESCALATION: 10,
        }

        time_spent_by_nurse: Dict[str, int] = {}
        doc_time_by_nurse: Dict[str, int] = {}
        for t in completed:
            mins = duration_by_type.get(t.task_type, 5)
            time_spent_by_nurse[t.nurse_id] = time_spent_by_nurse.get(t.nurse_id, 0) + mins
            if t.task_type == TaskType.DOCUMENTATION:
                doc_time_by_nurse[t.nurse_id] = doc_time_by_nurse.get(t.nurse_id, 0) + mins

        for nurse_id, total_time in time_spent_by_nurse.items():
            doc_time = doc_time_by_nurse.get(nurse_id, 0)
            share = doc_time / total_time if total_time else 0
            prefs = state["nurse_prefs"].setdefault(
                nurse_id, NursePreferences(nurse_id=nurse_id)
            )
            if share > 0.25:
                prefs.documentation_weight = max(0.5, prefs.documentation_weight - 0.1)

        summary = (
            f"Shift {state['shift_id']} summary: "
            f"completion_rate={completion_rate:.2f}, "
            f"overdue_rate={overdue_rate:.2f}. "
            f"Updated prefs for {len(state['nurse_prefs'])} nurses."
        )
        state["events"].append("ReflectAgent: " + summary)
        return state
