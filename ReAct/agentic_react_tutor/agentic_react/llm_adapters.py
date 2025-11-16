"""
A tiny adapter interface so you can plug in any LLM provider later.
This file contains:
- BaseLLMAdapter: interface
- MockLLMAdapter: simple deterministic "LLM" for local testing that simulates
  a short ReAct conversation that progresses based on the agent history.
"""

from abc import ABC, abstractmethod

class BaseLLMAdapter(ABC):
    @abstractmethod
    def complete(self, prompt: str, max_tokens: int = 256) -> str:
        """Return model completion text based on prompt."""
        pass

class MockLLMAdapter(BaseLLMAdapter):
    """
    A minimal mock "LLM" that follows a ReAct-like response pattern for the tutoring example.
    It inspects the prompt (which includes the conversation history) and returns:
      - an ACTION line when an action is still needed, or
      - a FINAL_ANSWER line once an observation exists.
    This prevents infinite repetition in the ReAct loop during tests/demos.
    """
    def complete(self, prompt: str, max_tokens: int = 256) -> str:
        # If we've already executed generate_exercise and the agent has observed it,
        # return a FINAL_ANSWER so the loop stops and presents the exercise/explanation.
        if "OBSERVATION from generate_exercise" in prompt:
            # Provide a friendly final answer including the exercise and a prompt for the student
            return (
                "THINK: I have the exercise ready and example solution from the tool. "
                "FINAL_ANSWER: Here's a short explanation and an easy exercise you can try.\n\n"
                "Explanation: Recursion is when a function calls itself to solve a smaller instance.\n"
                "Exercise: Write a recursive function `sum_to(n)` returning 1+2+...+n.\n"
                "Sample solution (for teacher):\n"
                "def sum_to(n):\n"
                "    if n <= 0:\n"
                "        return 0\n"
                "    return n + sum_to(n-1)\n\n"
                "Ask the student to implement it and submit their code for evaluation."
            )
        # If prompt requests generate_exercise (but no observation yet), ask the tool to run
        if "generate_exercise" in prompt and "OBSERVATION from generate_exercise" not in prompt:
            # Use JSON-style payload (double quotes) so agent parser can parse it robustly.
            return (
                "THINK: student needs a simple recursion exercise. "
                "ACTION: generate_exercise | {\"topic\":\"recursion\",\"difficulty\":\"easy\"}"
            )
        # If evaluation is being requested (simulated)
        if "evaluate_code" in prompt or "check solution" in prompt or "evaluate" in prompt:
            return (
                "THINK: run evaluator on provided code. "
                "ACTION: evaluate_code | {\"code\":\"<student_code>\", \"tests\":[\"sum_to(5) == 15\"]}"
            )
        # Default: propose a knowledge search (explanation)
        return (
            "THINK: student needs a gentle explanation. "
            "ACTION: knowledge_search | {\"topic\":\"recursion\",\"level\":\"beginner\"}"
        )
