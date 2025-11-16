# AgenticAI ReAct Tutoring (Python)

A small, self-contained Python example demonstrating an **AgenticAI ReAct** pattern applied to **personalized tutoring** (education domain).

## What is implemented
- A small ReAct-style agent that:
  - Uses an LLM adapter (mock implementation included)
  - Executes tools (knowledge_search, generate_exercise, evaluate_code)
  - Iterates in a Think -> Act -> Observe loop until it produces a final answer
- Tools are local functions (easy to replace with real services)
- A `MockLLMAdapter` included so you can try it without calling external APIs
- Example tutoring session showing how the pipeline works

## Project Structure
See the top of this README for the tree. Key files:
- `agentic_react/agent.py` — the ReAct loop
- `agentic_react/tools.py` — tool implementations
- `agentic_react/llm_adapters.py` — pluggable LLM adapters (Mock included)
- `examples/tutor_session.py` — runnable demo
- `tests/test_tools.py` — minimal unit tests

## Requirements
Install dependencies:
```bash
python -m pip install -r requirements.txt
