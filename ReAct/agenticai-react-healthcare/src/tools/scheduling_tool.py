class SchedulingTool:
    def schedule_followup(self, patient_id: str, when: str) -> dict:
        # Mock; integrate with calendar/booking service in production
        return {"status": "scheduled", "patient_id": patient_id, "when": when}