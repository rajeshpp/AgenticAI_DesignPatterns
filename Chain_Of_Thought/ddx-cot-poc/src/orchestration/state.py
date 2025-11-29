from typing import Dict, Any, List
from typing_extensions import TypedDict


class DDxState(TypedDict, total=False):
    # Input
    patient_case: Dict[str, Any]
    case_summary: str

    # Intermediate
    key_findings: str
    candidate_diagnoses: List[Dict[str, Any]]
    evidence_matrix: List[Dict[str, Any]]
    suggested_investigations: List[Dict[str, Any]]

    # Final
    final_output: Dict[str, Any]
