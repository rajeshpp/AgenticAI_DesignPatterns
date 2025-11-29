# src/orchestration/prompts.py

BASE_SYSTEM_PROMPT = """
You are an AI assistant helping licensed clinicians think through differential diagnoses.
You are NOT providing a final diagnosis, treatment recommendations, or advice for patients.

Rules:
- Assume your user is a clinician or clinical trainee.
- Never claim certainty. Use cautious language.
- Never give management or drug dosing advice.
- Always include: "This is NOT a final diagnosis. Check with the responsible clinician."
"""

EXTRACT_KEY_FINDINGS_USER = """
Patient case:
{case_summary}

Let's reason this out step-by-step:
1. List key positive findings.
2. List key negative or missing findings that seem clinically relevant.
3. Briefly describe overall acuity/severity.

End with: "Reminder: This is NOT a final diagnosis. Check with the responsible clinician."
"""

GENERATE_CANDIDATES_USER = """
Patient case:
{case_summary}

Key findings:
{key_findings}

Task:
1. Propose 3–5 possible differential diagnoses.
2. For each, provide:
   - name
   - rationale (1–2 sentences)
   - likelihood: "High", "Moderate", or "Low".

Return a single JSON object with this structure:

{{
  "diagnoses": [
    {{
      "name": "Diagnosis name",
      "rationale": "Short rationale",
      "likelihood": "High"
    }}
  ]
}}

Do not include any additional text outside the JSON.

Reminder: This is NOT a final diagnosis. Check with the responsible clinician.
"""

EVIDENCE_FOR_AGAINST_USER = """
Patient case:
{case_summary}

Candidate diagnoses:
{candidate_diagnoses}

Task:
For each diagnosis, create:
- name
- features_supporting: list of strings
- features_against_or_missing: list of strings
- potential_red_flags: list of strings

Return a single JSON object with this structure:

{{
  "evidence": [
    {{
      "name": "Diagnosis name",
      "features_supporting": [],
      "features_against_or_missing": [],
      "potential_red_flags": []
    }}
  ]
}}

Do not include any additional text outside the JSON.

Reminder: This is NOT a final diagnosis. Check with the responsible clinician.
"""

SUGGEST_INVESTIGATIONS_USER = """
Patient case:
{case_summary}

Top differentials:
{candidate_diagnoses}

Task:
Suggest up to 5 next-best investigations (e.g., labs, imaging, bedside tests)
that would help distinguish between these diagnoses. For each test include:
- name
- why_it_helps (1–2 sentences)

Do NOT suggest treatments or drug doses.

Return a single JSON object with this structure:

{{
  "investigations": [
    {{
      "name": "Test name",
      "why_it_helps": "Short explanation"
    }}
  ]
}}

Do not include any additional text outside the JSON.

Reminder: This is NOT a final diagnosis. Check with the responsible clinician.
"""
