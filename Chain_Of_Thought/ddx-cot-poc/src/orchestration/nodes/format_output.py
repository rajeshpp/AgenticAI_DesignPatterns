# src/orchestration/nodes/format_output.py

from src.orchestration.state import DDxState

DISCLAIMER_TEXT = (
    "This output is for differential diagnosis exploration only and is NOT a "
    "final diagnosis, treatment plan, or medical advice. All decisions must be "
    "made by the responsible clinician. This is NOT a final diagnosis. "
    "Check with the responsible clinician."
)


def run(state: DDxState) -> DDxState:
    """
    Final node: Combine everything into a clean response object.
    """
    new_state = dict(state)

    final_output = {
        "disclaimer": DISCLAIMER_TEXT,
        "case_summary": new_state.get("case_summary", ""),
        "key_findings": new_state.get("key_findings", ""),
        "diagnoses": new_state.get("candidate_diagnoses", []),
        "evidence": new_state.get("evidence_matrix", []),
        "investigations": new_state.get("suggested_investigations", []),
    }

    new_state["final_output"] = final_output
    return new_state  # type: ignore[return-value]
