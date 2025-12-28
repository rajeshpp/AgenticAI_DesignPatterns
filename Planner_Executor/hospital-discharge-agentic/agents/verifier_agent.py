from langfuse import observe

@observe(name="verifier_agent")
def verifier_agent(state):
    required_keys = [
        "medication_plan",
        "appointments",
        "education_material",
        "coverage_check"
    ]

    missing = [k for k in required_keys if k not in state]

    if missing:
        return {"status": "FAILED", "missing": missing}

    return {"status": "APPROVED"}
