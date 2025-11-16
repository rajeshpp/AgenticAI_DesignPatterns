"""
Very small unit tests for tools.
Run with: python -m pytest tests/test_tools.py
"""
from agentic_react.tools import generate_exercise, evaluate_code

def test_generate_exercise_recursion_easy():
    out = generate_exercise("recursion", "easy")
    assert "exercise" in out and "solution" in out
    assert "sum_to" in out["solution"]

def test_evaluate_code_ok():
    code = "def sum_to(n):\n    if n <= 0: return 0\n    return n + sum_to(n-1)\n"
    tests = ["sum_to(5) == 15"]
    res = evaluate_code(code, tests)
    assert res.get("ok") is True
