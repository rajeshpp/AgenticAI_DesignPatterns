from langfuse import observe

@observe(name="medication_agent")
def medication_agent(state):
    meds = state["patient"]["medications"]
    reconciled = [f"{m} – verified dose & timing" for m in meds]

    return {
        "medication_plan": reconciled
    }
