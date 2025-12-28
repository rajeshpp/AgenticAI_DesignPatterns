import json
from orchestration.crew import build_crew

def main():
    print("""
==================================================
AI-DRIVEN CLINICAL DECISION SUPPORT (POC)
==================================================
DISCLAIMER:
This system provides clinical decision support only.
It does NOT provide diagnoses or treatment decisions.
Final decisions must be made by a qualified clinician.
==================================================
""")

    with open("data/patient_case.json") as f:
        patient_data = json.load(f)

    crew = build_crew(patient_data)
    result = crew.kickoff()

    print("\n========== FINAL CDS OUTPUT ==========\n")
    print(result)

if __name__ == "__main__":
    main()
