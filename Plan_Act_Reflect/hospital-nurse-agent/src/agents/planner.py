# src/agents/planner.py
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from models.domain import Task, TaskType, NursePreferences
from models.state import AgentState


class PlannerAgent:
    def plan(self, state: AgentState) -> AgentState:
        risk_scores = self._compute_vital_risk(state["vitals"])
        tasks = state["tasks"]
        nurse_prefs = state["nurse_prefs"]

        # Example: new “check vitals” tasks for high-risk patients
        for pid, risk in risk_scores.items():
            if risk > 0.6:
                nurse_id = "N1"
                t = Task(
                    id=str(uuid.uuid4()),
                    patient_id=pid,
                    nurse_id=nurse_id,
                    task_type=TaskType.CHECK_VITALS,
                    description=f"Check patient {pid}, elevated risk ({risk:.2f})",
                    due_at=datetime.utcnow() + timedelta(minutes=10),
                )
                t.priority = risk * 0.7 + self._time_priority_factor(t.due_at) * 0.3
                tasks.append(t)

        # Reprioritize all pending tasks
        for t in tasks:
            prefs = nurse_prefs.get(t.nurse_id)
            t.priority = self._calculate_priority(t, risk_scores, prefs)

        state["tasks"] = sorted(tasks, key=lambda t: t.priority, reverse=True)
        state["events"].append("PlannerAgent: generated & reprioritized tasks.")
        return state

    # --- helpers ---

    def _compute_vital_risk(self, vitals) -> Dict[str, float]:
        latest_by_patient: Dict[str, object] = {}
        for v in sorted(vitals, key=lambda x: x.timestamp):
            latest_by_patient[v.patient_id] = v

        risk_scores: Dict[str, float] = {}
        for pid, v in latest_by_patient.items():
            score = 0.0
            if v.spo2 < 92:
                score += 0.5
            if v.systolic_bp < 90:
                score += 0.3
            if v.heart_rate > 110:
                score += 0.2
            risk_scores[pid] = min(score, 1.0)
        return risk_scores

    def _time_priority_factor(self, due_at: datetime) -> float:
        minutes = (due_at - datetime.utcnow()).total_seconds() / 60
        if minutes <= 0:
            return 1.0
        if minutes > 120:
            return 0.1
        return max(0.1, 1.0 - minutes / 120.0)

    def _calculate_priority(
        self,
        task: Task,
        risk_scores: Dict[str, float],
        prefs: Optional[NursePreferences],
    ) -> float:
        risk = risk_scores.get(task.patient_id, 0.3 if task.patient_id else 0.1)
        time_factor = self._time_priority_factor(task.due_at)
        base = 0.5 * risk + 0.5 * time_factor

        if prefs and task.task_type == TaskType.DOCUMENTATION:
            base *= prefs.documentation_weight

        return base
