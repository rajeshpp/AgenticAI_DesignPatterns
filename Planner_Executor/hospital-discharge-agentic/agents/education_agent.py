from langfuse import observe

@observe(name="education_agent")
def education_agent(state):
    patient = state["patient"]

    material = (
        f"Simple {patient.get('language', 'English')} instructions "
        f"with visuals (literacy level: {patient.get('literacy_level', 'medium')})"
    )

    return {
        "education_material": material
    }
