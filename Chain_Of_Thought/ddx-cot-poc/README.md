# CoT-Assisted Differential Diagnosis Explainer (POC)

This is a **POC** for a Chain-of-Thought-assisted differential diagnosis explainer
for clinicians, using:

- LangGraph for orchestration
- Langfuse for tracing
- OpenAI (via langchain-openai) for LLM calls

⚠️ **Not for clinical use.** Educational / demo only.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# NOTE: langfuse's langchain integration requires the full 'langchain' package
# to be installed. We added `langchain` to requirements.txt, but if you install
# manually you can run: pip install langchain
cp .env.example .env      # fill in your keys

# Run simple CLI example
python -m src.main

# Run FastAPI server (optional)
uvicorn src.api.server:app --reload

#Then POST to http://localhost:8000/ddx with JSON case input.

---

## 📁 `src/`

### `src/__init__.py`

```