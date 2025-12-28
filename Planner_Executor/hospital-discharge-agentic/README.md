# Hospital Discharge Planning – Agentic AI POC

This repository contains a production-style Agentic AI proof of concept that demonstrates how the Planner–Executor–Verifier design pattern can be applied to hospital discharge planning and readmission prevention.

The solution uses LangGraph for agent orchestration, Streamlit for a live dashboard demo, and Langfuse for full observability and tracing.

---

PROBLEM STATEMENT

Hospitals face high readmission rates due to:
- Poor discharge coordination
- Missed medications
- Missed follow-up appointments
- Low patient understanding
- Insurance and coverage gaps

These workflows involve multiple systems and stakeholders and cannot be reliably handled by a single monolithic AI prompt.

---

SOLUTION OVERVIEW

This system implements a Planner–Executor–Verifier agentic architecture.

Planner Agent:
- Creates a personalized discharge plan
- Defines medications, follow-ups, education needs, and insurance checks

Executor Agents (run in parallel):
- Medication Reconciliation Agent
- Appointment Scheduling Agent
- Patient Education Agent (language and literacy aware)
- Insurance and Coverage Agent

Verifier Agent:
- Validates discharge completeness
- Ensures compliance and readiness
- Acts as a safety and audit checkpoint

---

DEMO 1: STREAMLIT AGENTIC DASHBOARD

The Streamlit UI allows you to:
- Trigger the discharge workflow with one click
- View outputs from each agent
- See the final discharge summary
- Check verifier approval status

This makes agentic workflows explainable and demo-ready.

---

DEMO 2: LANGFUSE OBSERVABILITY

Langfuse is integrated for end-to-end observability:
- One root trace per discharge workflow
- Individual traces for each agent
- Visibility into inputs, outputs, latency, and errors

This is critical for healthcare, regulated environments, and enterprise AI systems.

---

TECH STACK

Agent Orchestration: LangGraph  
Backend API: FastAPI  
Dashboard UI: Streamlit  
Observability: Langfuse  
LLM: OpenAI or Azure OpenAI  

---

PROJECT STRUCTURE

hospital-discharge-agentic/
agents/
  planner.py
  medication_agent.py
  appointment_agent.py
  education_agent.py
  insurance_agent.py
  verifier_agent.py

graph/
  state.py
  discharge_graph.py

observability/
  langfuse_client.py

api/
  main.py

ui/
  dashboard.py

data/
  patient_sample.json

requirements.txt
README.md

---

SETUP INSTRUCTIONS

1. Create and activate virtual environment

python -m venv venv

Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

---

2. Install dependencies

pip install -r requirements.txt
pip install langfuse

---

3. Environment variables

Create a .env file in the project root with the following:

OPENAI_API_KEY=your_openai_key

LANGFUSE_PUBLIC_KEY=pk_xxxx
LANGFUSE_SECRET_KEY=sk_xxxx
LANGFUSE_BASE_URL=https://cloud.langfuse.com

---

RUNNING THE APPLICATION

Start backend:

uvicorn api.main:app --reload

Backend URL:
http://127.0.0.1:8000

---

Start Streamlit UI (new terminal, same venv):

streamlit run ui/dashboard.py

UI URL:
http://localhost:8501

---

RUN THE WORKFLOW

1. Open the Streamlit UI
2. Click "Run Discharge Planning"
3. Observe planner, executors, verifier outputs
4. View traces in Langfuse

---

LANGFUSE TRACE STRUCTURE

hospital_discharge_workflow
- planner_agent
- medication_agent
- appointment_agent
- education_agent
- insurance_agent
- verifier_agent

Each trace contains inputs, outputs, latency, and errors.

---

KEY DESIGN LEARNINGS

- Agentic AI is about orchestration, not prompts
- State ownership must be explicit
- Parallel agents require merge semantics
- Verification is essential in regulated domains
- Observability is mandatory for production AI

---

FUTURE ENHANCEMENTS

- Readmission risk scoring agent
- Human-in-the-loop approval
- FHIR-based EHR integration
- Cost and latency dashboards
- Docker Compose support

---

This project is intended for architects, AI engineers, and teams building production-grade agentic systems.
