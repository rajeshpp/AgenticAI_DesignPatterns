"""
Tool implementations for the ReAct agent.
- knowledge_search: returns short explanation + example(s)
- generate_exercise: returns an exercise and sample solution
- evaluate_code: attempts to run student code against tests (sandboxed-ish)
"""

from typing import Dict, Any, Tuple, List
import ast
import multiprocessing
import time

def knowledge_search(topic: str, level: str) -> Dict[str, Any]:
    """
    Return an explanation and a simple example for the given topic and level.
    This is a simple knowledge base — replace or extend with real KB or web search.
    """
    if topic.lower() == "recursion":
        explanation = (
            "Recursion is when a function calls itself to solve a smaller instance "
            "of the same problem. Base case and progress toward it are required."
        )
        example = (
            "Example (factorial):\n"
            "def factorial(n):\n"
            "    if n <= 1:\n"
            "        return 1\n"
            "    return n * factorial(n-1)\n"
        )
        tip = "Tip: ensure the base case prevents infinite recursion (e.g., n <= 1)."
        return {"topic": topic, "level": level, "explanation": explanation, "example": example, "tip": tip}
    # default fallback
    return {"topic": topic, "level": level, "explanation": f"Short intro to {topic}.", "example": "", "tip": ""}

def generate_exercise(topic: str, difficulty: str) -> Dict[str, Any]:
    """
    Produce an exercise and sample solution. Difficulty could be 'easy', 'medium', 'hard'.
    """
    if topic.lower() == "recursion":
        if difficulty == "easy":
            exercise = "Write a recursive function `sum_to(n)` that returns the sum 1+2+...+n."
            solution = (
                "def sum_to(n):\n"
                "    if n <= 0:\n"
                "        return 0\n"
                "    return n + sum_to(n-1)\n"
            )
            tests = ["sum_to(5) == 15", "sum_to(0) == 0"]
        else:
            exercise = "Implement recursive fibonacci or factorial variation."
            solution = "def fib(n):\n    if n <= 1: return n\n    return fib(n-1) + fib(n-2)\n"
            tests = ["fib(5) == 5"]
        return {"exercise": exercise, "solution": solution, "tests": tests, "difficulty": difficulty}
    return {"exercise": f"Practice {topic}.", "solution": "", "tests": []}

# --- A small sandboxed evaluator ---
def _exec_worker(code: str, test_code: str, queue):
    """
    Run given code + test expression in a constrained environment and put result in queue.
    This runs in a separate process for timeout and interruption safety.
    """
    try:
        # Prepare a minimal namespace
        ns = {}
        # compile and exec student code
        exec(compile(code, "<student_code>", "exec"), {"__builtins__": {}}, ns)
        # evaluate tests sequentially; tests expressed as Python expressions that use functions defined above
        results = []
        for t in test_code:
            # eval in same ns but allow minimal builtins for arithmetic
            res = eval(t, {"__builtins__": {}}, ns)
            results.append(bool(res))
        queue.put({"ok": all(results), "results": results})
    except Exception as e:
        queue.put({"ok": False, "error": str(e)})

def evaluate_code(code: str, tests: List[str], timeout: float = 2.0) -> Dict[str, Any]:
    """
    Evaluate student code against tests in a separate process to reduce risk.
    NOTE: This is not fully secure sandboxing — for production, use a dedicated sandbox environment.
    """
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=_exec_worker, args=(code, tests, q))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        return {"ok": False, "error": "Timeout or long-running code (terminated)."}
    if q.empty():
        return {"ok": False, "error": "No result returned from worker."}
    return q.get()
