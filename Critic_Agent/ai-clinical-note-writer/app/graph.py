from langgraph.graph import StateGraph
from typing import TypedDict, List

from app.agents.input_agent import input_agent
from app.agents.generator_agent import generator_agent
from app.agents.critic_agent import critic_agent
from app.agents.refiner_agent import refiner_agent
from app.models.schemas import CriticReport


class AgentState(TypedDict, total=False):
    doctor_input: str
    generated_note: str
    critic_report: CriticReport
    final_note: str
    audit_trail: List[str]


def build_graph():
    graph = StateGraph(AgentState)

    # Nodes
    graph.add_node("input", input_agent)
    graph.add_node("generator", generator_agent)
    graph.add_node("critic", critic_agent)
    graph.add_node("refiner", refiner_agent)

    # Entry point
    graph.set_entry_point("input")

    # Flow
    graph.add_edge("input", "generator")
    graph.add_edge("generator", "critic")
    graph.add_edge("critic", "refiner")

    return graph.compile()
