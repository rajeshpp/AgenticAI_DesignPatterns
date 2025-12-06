from typing import List, Dict, Any

# POC normalization dictionaries
MED_NORMALIZATION = {
    "warfarin": "warfarin",
    "coumadin": "warfarin",
    "amiodarone": "amiodarone",
    "metformin": "metformin",
    "ibuprofen": "ibuprofen",
    "advil": "ibuprofen",
    "motrin": "ibuprofen",
}

COMORBIDITY_NORMALIZATION = {
    "ckd": "ckd",
    "ckd stage 3": "ckd_stage_3",
    "chronic kidney disease stage 3": "ckd_stage_3",
    "heart failure": "hf",
    "hf": "hf",
    "diabetes": "dm",
    "dm": "dm",
}

# Very small POC interaction rules
INTERACTION_RULES: List[Dict[str, Any]] = [
    {
        "id": "warfarin_amiodarone",
        "drug_a": "warfarin",
        "drug_b": "amiodarone",
        "base_severity": "major",
        "notes": "Amiodarone inhibits warfarin metabolism (CYP2C9 / CYP3A4).",
    },
    {
        "id": "nsaid_ckd",
        "drug_a": "ibuprofen",
        "drug_b": "ckd_stage_3",
        "base_severity": "moderate",
        "notes": "NSAIDs can worsen renal function, especially in CKD.",
    },
]
