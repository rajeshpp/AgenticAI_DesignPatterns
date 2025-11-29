from typing import Dict, Any


def build_case_summary(patient_case: Dict[str, Any]) -> str:
    """
    Turn structured case dict into a canonical case summary string.
    """
    parts = []

    age = patient_case.get("age")
    sex = patient_case.get("sex")
    if age and sex:
        parts.append(f"{age}-year-old {sex}")
    elif age:
        parts.append(f"{age}-year-old")
    elif sex:
        parts.append(sex)

    if patient_case.get("chief_complaint"):
        parts.append(f"with chief complaint: {patient_case['chief_complaint']}.")

    if patient_case.get("symptoms"):
        parts.append(f"Symptoms: {patient_case['symptoms']}.")

    if patient_case.get("vitals"):
        parts.append(f"Vitals: {patient_case['vitals']}.")

    if patient_case.get("labs"):
        parts.append(f"Labs: {patient_case['labs']}.")

    if patient_case.get("history"):
        parts.append(f"History: {patient_case['history']}.")

    if patient_case.get("notes"):
        parts.append(f"Additional notes: {patient_case['notes']}.")

    return " ".join(parts)
