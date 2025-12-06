# Medication Interaction Reasoning Assistant (POC)

> ⚠️ This is a **POC only**, with a tiny hard-coded ruleset.  
> It is **not** clinically validated and must **not** be used for real patient care.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."  # set your key

Run
python run_uvicorn.py


The API will be at http://localhost:8000.

Open docs:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

Example request (curl)
curl -X POST "http://localhost:8000/interactions" \
  -H "Content-Type: application/json" \
  -d '{
    "medications": ["Warfarin", "Amiodarone", "Metformin", "Ibuprofen"],
    "comorbidities": ["CKD Stage 3"]
  }'


The response will include:

summary_list: quick view of flagged pairs like
warfarin + amiodarone, ibuprofen + ckd_stage_3

interactions: detailed CoT-style reasoning per pair

disclaimer: safety text


---

If you want, next step I can extend this “project” with:

- A **LangFuse** integration wrapper around the LangGraph nodes, or  
- A **frontend mock** (simple React/Next or plain HTML) that calls `/interactions` and shows the CoT explanations nicely.
```