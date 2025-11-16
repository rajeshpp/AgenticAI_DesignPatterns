# AgenticAI ReAct Customer Support (Python)

A demonstration project showing an AgenticAI **ReAct** design pattern for a customer-support flow: the agent reasons, decides to call a tool (order status), calls it, observes results, and responds to the user.

This is intentionally small, easy to run locally, and ready to integrate with a real LLM (OpenAI) or run with the fallback local rule-based agent.

## Features
- FastAPI server exposing a `/chat` endpoint for chat-style interactions.
- ReAct agent loop (Reason → Action → Observe → Repeat → Final Answer).
- Mock `order_service` tool (can be swapped with real API).
- Optional OpenAI integration (if `OPENAI_API_KEY` is provided). When available, uses Chat Completions + function-calling to ask the model what action to take.
- Fallback deterministic agent when OpenAI key is not set.

## Requirements
Python 3.10+ recommended.

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # windows: .venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

Then POST to `http://localhost:8000/chat` with JSON body:

```json
{"user_id": "user123", "message": "My order 12345 hasn't arrived"}
```