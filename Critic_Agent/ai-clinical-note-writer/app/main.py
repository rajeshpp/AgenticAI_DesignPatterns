from dotenv import load_dotenv
load_dotenv()

from app.graph import build_graph
from app.models.schemas import FinalOutput


def run_poc():
    app = build_graph()

    doctor_input = "Patient has chest pain, ECG borderline, sent home."

    result = app.invoke({
        "doctor_input": doctor_input
    })

    final_output = FinalOutput(
        final_note=result["final_note"],
        critic_report=result["critic_report"],
        audit_trail=result["audit_trail"]
    )

    print("\n===== FINAL CLINICAL NOTE =====\n")
    print(final_output.final_note)

    print("\n===== CRITIC REPORT =====\n")
    for f in final_output.critic_report.findings:
        print(f"- {f.issue} (Severity: {f.severity})")

    print(f"\nConfidence Score: {final_output.critic_report.confidence_score}")

    print("\n===== AUDIT TRAIL =====\n")
    for step in final_output.audit_trail:
        print("-", step)


if __name__ == "__main__":
    run_poc()
