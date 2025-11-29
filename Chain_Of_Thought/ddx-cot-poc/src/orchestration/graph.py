# src/orchestration/graph.py

from langgraph.graph import StateGraph, END

from src.orchestration.state import DDxState
from src.orchestration.nodes import (
    normalize_input,
    extract_key_findings,
    generate_candidates,
    evidence_for_against,
    suggest_investigations,
    format_output,
)


def build_ddx_graph():
    """
    Build and compile the LangGraph workflow for the CoT-assisted
    differential diagnosis explainer.

    For this POC we do NOT use a checkpointer, to avoid having to
    supply thread_id / checkpoint_ns / checkpoint_id in config.
    """
    workflow = StateGraph(DDxState)

    # Register nodes
    workflow.add_node("normalize_input", normalize_input.run)
    workflow.add_node("extract_key_findings", extract_key_findings.run)
    workflow.add_node("generate_candidates", generate_candidates.run)
    workflow.add_node("evidence_for_against", evidence_for_against.run)
    workflow.add_node("suggest_investigations", suggest_investigations.run)
    workflow.add_node("format_output", format_output.run)

    # Entry point
    workflow.set_entry_point("normalize_input")

    # Edges (linear pipeline)
    workflow.add_edge("normalize_input", "extract_key_findings")
    workflow.add_edge("extract_key_findings", "generate_candidates")
    workflow.add_edge("generate_candidates", "evidence_for_against")
    workflow.add_edge("evidence_for_against", "suggest_investigations")
    workflow.add_edge("suggest_investigations", "format_output")
    workflow.add_edge("format_output", END)

    # No checkpointer for now
    graph = workflow.compile()
    return graph
