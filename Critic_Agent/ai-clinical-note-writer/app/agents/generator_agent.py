from app.llm.openai_client import get_llm

llm = get_llm()


def generator_agent(state):
    doctor_input = state.get("doctor_input", "")

    prompt = f"""
You are a clinical documentation assistant.

Convert the doctor input below into a SOAP-style clinical note.
Use medically correct language. Do not assume facts.

Doctor Input:
{doctor_input}
"""

    response = llm.invoke(prompt)

    return {
        "doctor_input": doctor_input,
        "generated_note": response.content,
        "audit_trail": state["audit_trail"] + ["Generated initial clinical note"]
    }

