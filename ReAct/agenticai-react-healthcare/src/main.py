import json
from .tools.vitals_tool import VitalsTool
from .tools.guidelines_tool import GuidelinesTool
from .tools.scheduling_tool import SchedulingTool
from .environment import Environment
from .agent import ReActAgent
from .utils.types import PatientData


def run_example():
    vitals_tool = VitalsTool()
    guidelines_tool = GuidelinesTool()
    scheduling_tool = SchedulingTool()

    env = Environment(vitals_tool, guidelines_tool, scheduling_tool)
    agent = ReActAgent(env)

    sample = PatientData(patient_id="patient_123", age=30, symptoms={"fever": True, "duration_days": 2})

    result = agent.act(sample)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    run_example()