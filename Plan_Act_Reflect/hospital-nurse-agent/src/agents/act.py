# src/agents/act.py
from models.domain import TaskStatus
from models.state import AgentState
from models.services import NotificationService, EHRClient


class ActAgent:
    def __init__(self, notification_service: NotificationService,
                 ehr_client: EHRClient):
        self.notification_service = notification_service
        self.ehr_client = ehr_client

    def act(self, state: AgentState) -> AgentState:
        # Notify nurses about pending tasks
        for task in state["tasks"]:
            if task.status == TaskStatus.PENDING:
                patient = state["patients"].get(task.patient_id) if task.patient_id else None
                room = patient.room if patient else "N/A"
                self.notification_service.send(
                    to_nurse=task.nurse_id,
                    message=f"[{task.task_type.value}] {task.description} (Room {room})",
                )
                task.status = TaskStatus.IN_PROGRESS
                state["events"].append(
                    f"ActAgent: notified nurse {task.nurse_id} for task {task.id}"
                )

        # Auto-document vitals
        for v in state["vitals"]:
            self.ehr_client.write_vital(v)
        state["events"].append("ActAgent: auto-documented vitals in EHR.")

        # Escalate critical vitals
        self._maybe_escalate(state)
        return state

    def _maybe_escalate(self, state: AgentState) -> None:
        for v in state["vitals"]:
            if v.spo2 < 88 or v.systolic_bp < 80:
                patient = state["patients"][v.patient_id]
                self.notification_service.send(
                    to_role="rapid_response_team",
                    message=(
                        f"CRITICAL: Patient {patient.name} "
                        f"(Room {patient.room}) requires immediate attention."
                    ),
                )
                state["events"].append(
                    f"ActAgent: escalated patient {patient.id}."
                )
