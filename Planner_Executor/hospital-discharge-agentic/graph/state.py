from typing import TypedDict, Annotated, List, Dict, Any
import operator

class DischargeState(TypedDict, total=False):
    # Shared immutable input
    patient: Dict[str, Any]

    # Planner output
    discharge_plan: str

    # Parallel executor outputs (MERGE SAFELY)
    medication_plan: Annotated[List[str], operator.add]
    appointments: Annotated[List[Dict[str, Any]], operator.add]

    # Single-writer outputs
    education_material: str
    coverage_check: str

    # Verifier outputs
    status: str
    missing: List[str]
