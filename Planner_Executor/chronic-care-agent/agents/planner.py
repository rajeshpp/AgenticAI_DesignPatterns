from utils.llm import call_llm

SYSTEM_PROMPT = """
You are a clinical care planning assistant.
Rules:
- Follow hypertension clinical guidelines
- Never suggest stopping prescribed medication
- If unsure, recommend clinician review
"""

def create_care_plan(patient_profile):
    prompt = f"""
    Create a 30-day hypertension care plan.

    Patient profile:
    {patient_profile}

    Include:
    - Monitoring plan
    - Medication adherence goals
    - Lifestyle goals
    - Escalation criteria
    """

    return call_llm(prompt, SYSTEM_PROMPT)
