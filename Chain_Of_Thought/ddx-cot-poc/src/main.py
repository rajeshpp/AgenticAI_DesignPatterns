from pprint import pprint

from src.orchestration import build_ddx_graph
from src.llm.llm_client import langfuse_handler


def main():
    graph = build_ddx_graph()

    patient_case = {
        "age": 65,
        "sex": "male",
        "chief_complaint": "fever and pleuritic chest pain",
        "symptoms": "fever, productive cough, pleuritic chest pain",
        "vitals": "RR 28, SpO2 90%, HR 102, BP 130/80",
        "history": "No known chronic lung disease documented.",
        "notes": "Crackles in right lower lung field on auscultation.",
    }

    initial_state = {"patient_case": patient_case}

    # If langfuse_handler is None, just pass empty callbacks
    callbacks = [langfuse_handler] if langfuse_handler is not None else []

    result_state = graph.invoke(
        initial_state,
        config={
            "callbacks": callbacks
        },
    )

    print("\n=== Final Output ===")
    pprint(result_state["final_output"])


if __name__ == "__main__":
    main()
