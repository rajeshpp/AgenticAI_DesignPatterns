from langfuse import observe

@observe(name="appointment_agent")
def appointment_agent(state):
    return {
        "appointments": [
            {"type": "Cardiology Follow-up", "days": 7},
            {"type": "Lab Tests", "days": 14}
        ]
    }
