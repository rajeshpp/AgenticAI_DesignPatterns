def input_agent(state):
    """
    Adapter node to normalize external input
    (LangGraph Studio, API, CLI) into graph state
    """
    return {
        "doctor_input": state.get("doctor_input", ""),
        "audit_trail": ["Doctor input received"]
    }
