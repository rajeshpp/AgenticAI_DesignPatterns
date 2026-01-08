from app.llm.openai_client import get_llm

llm = get_llm()


def refiner_agent(state):
    prompt = f"""
You are a senior clinical documentation expert.

Original Note:
{state['generated_note']}

Critic Findings:
{state['critic_report']}

Refine the note by:
- Addressing safety gaps
- Improving clarity
- Adding follow-up instructions
- Aligning with discharge best practices
"""

    response = llm.invoke(prompt)

    return {
    "doctor_input": state["doctor_input"],
    "generated_note": state["generated_note"],
    "critic_report": state["critic_report"],
    "final_note": response.content,
    "audit_trail": state["audit_trail"] + ["Refined note with safety corrections"]
}

