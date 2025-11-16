from .utils.types import PatientData

class Environment:
    """Environment holds external context and mediates tool calls in a test-friendly way."""
    def __init__(self, vitals_tool, guidelines_tool, scheduling_tool):
        self.vitals_tool = vitals_tool
        self.guidelines_tool = guidelines_tool
        self.scheduling_tool = scheduling_tool

    def get_vitals(self, patient_id: str) -> dict:
        return self.vitals_tool.fetch_vitals(patient_id)

    def consult_guidelines(self, findings: dict) -> str:
        return self.guidelines_tool.lookup(findings)

    def book_followup(self, patient_id: str, when: str) -> dict:
        return self.scheduling_tool.schedule_followup(patient_id, when)