from langgraph.graph import StateGraph
from graph.state import DischargeState

from agents.planner import planner_agent
from agents.medication_agent import medication_agent
from agents.appointment_agent import appointment_agent
from agents.education_agent import education_agent
from agents.insurance_agent import insurance_agent
from agents.verifier_agent import verifier_agent

def build_graph():
    graph = StateGraph(DischargeState)

    graph.add_node("planner", planner_agent)
    graph.add_node("meds", medication_agent)
    graph.add_node("appointments", appointment_agent)
    graph.add_node("education", education_agent)
    graph.add_node("insurance", insurance_agent)
    graph.add_node("verifier", verifier_agent)

    graph.set_entry_point("planner")

    graph.add_edge("planner", "meds")
    graph.add_edge("planner", "appointments")
    graph.add_edge("planner", "education")
    graph.add_edge("planner", "insurance")

    graph.add_edge("meds", "verifier")
    graph.add_edge("appointments", "verifier")
    graph.add_edge("education", "verifier")
    graph.add_edge("insurance", "verifier")

    return graph.compile()
