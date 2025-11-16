"""
Example usage: a tutoring session for recursion with the ReAct agent.
This prints a clean ReAct transcript (Think → Action → Observation) and then the Final Answer.
"""

from agentic_react.llm_adapters import MockLLMAdapter
from agentic_react.agent import ReActAgent
from agentic_react import tools
import json

def main():
    # Register tools
    tools_registry = {
        "knowledge_search": lambda topic, level: tools.knowledge_search(topic, level),
        "generate_exercise": lambda topic, difficulty: tools.generate_exercise(topic, difficulty),
        "evaluate_code": lambda code, tests: tools.evaluate_code(code, tests),
    }

    llm = MockLLMAdapter()
    agent = ReActAgent(llm, tools_registry)

    student_profile = {"name": "Aisha", "level": "beginner", "weakness": "recursion"}
    question = "I don't understand recursion. Can you explain and give me an easy exercise I can try?"

    result = agent.run(student_profile, question)

    # Print a clean ReAct transcript
    print("\n=== ReAct Transcript (Think → Action → Observation) ===\n")
    for idx, step in enumerate(result["transcript"], start=1):
        print(f"Step {idx}:")
        if step.get("think"):
            print("  THINK:", step["think"])
        if step.get("action"):
            print("  ACTION:", step["action"]["tool"], "|", json.dumps(step["action"]["payload"], ensure_ascii=False))
        if step.get("observation") is not None:
            obs = step["observation"]
            # Pretty print dict observations if possible
            if isinstance(obs, dict):
                print("  OBSERVATION:", json.dumps(obs, ensure_ascii=False))
            else:
                print("  OBSERVATION:", obs)
        print()

    # Then final answer
    print("=== Final Answer ===\n")
    print(result["final_answer"])
    print("\n=== End ===\n")

if __name__ == "__main__":
    main()
