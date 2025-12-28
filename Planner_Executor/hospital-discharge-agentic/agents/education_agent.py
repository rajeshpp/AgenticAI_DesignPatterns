def education_agent(state):
    patient = state["patient"]

    language = patient.get("language", "English")
    literacy = patient.get("literacy_level", "medium")

    return {
        "education_material": (
            f"Simple {language} instructions with visuals "
            f"(literacy level: {literacy})"
        )
    }
