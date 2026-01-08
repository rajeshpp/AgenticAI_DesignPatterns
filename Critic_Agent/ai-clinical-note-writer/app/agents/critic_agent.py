from app.llm.openai_client import get_llm
from app.models.schemas import CriticFinding, CriticReport

llm = get_llm()


def critic_agent(state):
    generated_note = state.get("generated_note", "")
    prompt = f"""
You are a medical safety reviewer.

Analyze the clinical note below and identify:
- Missing investigations
- Clinical red flags
- Risk stratification gaps
- Unsafe discharge decisions

Clinical Note:
{generated_note}
"""

    response = llm.invoke(prompt)
    findings = []

    # Simple deterministic safety rules (POC logic)
    if "chest pain" in generated_note.lower():
        findings.append(CriticFinding(
            issue="Troponin test not documented for chest pain evaluation",
            severity="high"
        ))

        findings.append(CriticFinding(
            issue="No cardiac risk stratification mentioned",
            severity="high"
        ))

    critic_report = CriticReport(
        findings=findings,
        summary="Safety gaps identified in generated note",
        confidence_score=0.65
    )

    return {
    "doctor_input": state["doctor_input"],
    "generated_note": generated_note,
    "critic_report": critic_report,
    "audit_trail": state["audit_trail"] + ["Critic safety review completed"]
}

