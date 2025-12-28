from langfuse import observe

@observe(name="insurance_agent")
def insurance_agent(state):
    return {
        "coverage_check": "Medications & follow-ups covered under government scheme"
    }
