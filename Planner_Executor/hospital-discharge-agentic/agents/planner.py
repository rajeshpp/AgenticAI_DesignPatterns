from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")

def planner_agent(state):
    patient = state["patient"]

    prompt = f"""
    Create a personalized hospital discharge plan for:
    {patient}

    Include:
    - Medication plan
    - Follow-up schedule
    - Patient education needs
    - Insurance considerations
    """

    response = llm.invoke(prompt)

    return {
        "discharge_plan": response.content
    }
