from typing import List, Dict, Any, TypedDict


class MedInteractionState(TypedDict, total=False):
    medications: List[str]
    comorbidities: List[str]

    normalized_meds: List[str]
    normalized_comorbidities: List[str]

    interaction_candidates: List[Dict[str, Any]]
    interaction_explanations: List[Dict[str, Any]]

    result: Dict[str, Any]
