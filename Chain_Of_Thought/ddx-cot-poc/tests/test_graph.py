from src.orchestration import build_ddx_graph


def test_graph_runs_smoke():
    graph = build_ddx_graph()
    state = {
        "patient_case": {
            "age": 65,
            "sex": "male",
            "chief_complaint": "fever and pleuritic chest pain",
        }
    }

    # Smoke test: it should not raise, and final_output should exist
    result = graph.invoke(state)
    assert "final_output" in result
    assert "disclaimer" in result["final_output"]
