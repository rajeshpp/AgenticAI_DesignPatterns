# 🧠 Personalized Chronic Disease Management – Agentic AI POC

This repository demonstrates a Planner–Executor–Critic
agentic architecture for remote chronic disease management
(e.g., hypertension, asthma, diabetes).

Unlike traditional chatbots, this system:
- Plans care over weeks or months
- Acts daily on patient signals
- Continuously checks for safety and drift

This is a runnable, production-aligned POC.

---

## 🎯 Use Case

Personalized Chronic Disease Management (Remote Care)

Chronic conditions require:
- Continuous monitoring
- Timely interventions
- Safety-first recommendations
- Clinician escalation when needed

This POC focuses on hypertension but is extensible.

---

## 🧩 Agentic Architecture

### Why Agentic?

Plan globally, act locally.

Chronic care needs long-term planning
with short-term execution.

### Core Agents

### 🧠 Planner Agent
- Creates a 30-day care plan
- Uses patient profile and clinician goals
- Defines monitoring and escalation rules

### ⚙️ Executor Agents
- Wearable Data Monitoring Agent
- Medication Adherence Agent
- Lifestyle Coaching Agent
- Alert and Escalation Agent

### 🛡️ Critic Agent
- Reviews planner and executor outputs
- Detects unsafe recommendations
- Flags drift or policy violations

---

## 🔄 High-Level Flow

Patient data flows through agents
in a continuous loop:

Patient Signals  
↓  
Planner Agent  
↓  
Executor Agents  
↓  
Critic Agent  
↓  
Alerts / Coaching / Escalation

---

## 🛠️ Tech Stack

- Python
- Streamlit (UI and orchestration)
- OpenAI API (LLM-powered agents)
- Planner–Executor–Critic pattern

---

## 📁 Project Structure

chronic-care-agent  
├── app.py  
├── agents  
│   ├── planner.py  
│   ├── wearable_monitor.py  
│   ├── medication_agent.py  
│   ├── lifestyle_agent.py  
│   ├── alert_agent.py  
│   └── critic.py  
├── utils  
│   ├── llm.py  
│   └── rules.py  
├── data  
│   ├── patient_profile.json  
│   ├── wearable_data.json  
│   └── medication_log.json  
├── requirements.txt  
├── .env  
└── README.md  

---

## 🚀 Getting Started

### 1. Clone the repository

git clone https://github.com/your-repo/chronic-care-agent.git  
cd chronic-care-agent  

### 2. Install dependencies

pip install -r requirements.txt  

### 3. Configure OpenAI API key

Create a file named `.env` in the root:

OPENAI_API_KEY=sk-your-api-key-here  

### 4. Run the app

streamlit run app.py  

---

## 🖥️ What You’ll See

- Generated 30-day care plan
- Wearable data analysis
- Medication adherence status
- Lifestyle coaching suggestions
- Alert escalation decisions
- Critic agent safety checks

---

## ⚕️ Safety and Guardrails

This POC includes:
- Low-temperature LLM calls
- Explicit system prompts
- Rule-based thresholds
- Critic agent oversight

Disclaimer:
This project is for educational and
architectural demonstration only.
It is not a medical device.

---

## 🔮 Extensibility

This architecture can evolve into:
- LangGraph-based workflows
- CrewAI or OpenAI Swarm agents
- FHIR-compliant integrations
- Clinician-in-the-loop systems
- Multi-patient orchestration
- Temporal memory and trends

---

## 📚 Topics Covered

- Agentic AI
- Planner–Executor design
- Safety-first AI systems
- AI for regulated domains
- Continuous decision systems

---

## 👤 Author

Built as part of an Agentic Design Patterns
and AgentKit learning series.

If you are exploring AI agents beyond
chatbots, this project is a reference.

---

## 💬 Feedback

Ideas, discussions, and contributions
are welcome. Open an issue or start
a conversation.
