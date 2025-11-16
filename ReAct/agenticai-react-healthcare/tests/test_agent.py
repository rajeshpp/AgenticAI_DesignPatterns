from src.tools.vitals_tool import VitalsTool
from src.tools.guidelines_tool import GuidelinesTool
from src.tools.scheduling_tool import SchedulingTool
from src.environment import Environment
from src.agent import ReActAgent
from src.utils.types import PatientData


def test_agent_green_path(monkeypatch):
    # Monkeypatch vitals to a mild case
    class MildVitals(VitalsTool):
        def fetch_vitals(self, patient_id: str):
            return {"temperature": 37.2, "heart_rate": 80}

    env = Environment(MildVitals(), GuidelinesTool(), SchedulingTool())
    agent = ReActAgent(env)
    p = PatientData(patient_id="p1", age=25, symptoms={"fever": False})
    res = agent.act(p)
    assert res["level"] == "GREEN"


def test_agent_yellow_path(monkeypatch):
    class YellowVitals(VitalsTool):
        def fetch_vitals(self, patient_id: str):
            return {"temperature": 38.2, "heart_rate": 105}

    env = Environment(YellowVitals(), GuidelinesTool(), SchedulingTool())
    agent = ReActAgent(env)
    p = PatientData(patient_id="p2", age=45, symptoms={"fever": True})
    res = agent.act(p)
    assert res["level"] == "YELLOW"
    assert "followup" in res