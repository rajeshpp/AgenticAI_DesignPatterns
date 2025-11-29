from src.orchestration.state import DDxState
from src.utils import build_case_summary


def run(state: DDxState) -> DDxState:
    new_state = dict(state)
    patient_case = new_state.get("patient_case", {})
    case_summary = build_case_summary(patient_case)
    new_state["case_summary"] = case_summary
    return new_state  # type: ignore[return-value]
