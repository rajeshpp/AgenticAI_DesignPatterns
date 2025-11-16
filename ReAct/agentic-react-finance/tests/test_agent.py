import json
from agent import ReActAgent


def test_agent_runs_with_sample():
    with open("examples/sample_portfolio.json") as f:
        portfolio = json.load(f)
    agent = ReActAgent(days=5)
    res = agent.run(portfolio)
    assert "recommendation" in res and isinstance(res["recommendation"], dict)