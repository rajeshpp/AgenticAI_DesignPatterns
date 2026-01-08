🩺 AI Clinical Note Writer with Safety Critic

Agentic AI POC – Generate → Critique → Refine

📌 Overview

Doctors spend significant time writing clinical notes.
While AI can generate notes quickly, unreviewed AI output is unsafe in healthcare due to hallucinations, missing clinical checks, and compliance risks.

This project demonstrates an Agentic AI system that:

Generates clinical notes

Critiques them for medical safety

Refines them for compliance and clarity

Provides auditability, confidence scoring, and human approval

This is not a chatbot — it is a clinical accountability system.

🧠 Core Idea

“Doctor’s Second Brain for Notes & Compliance”

Instead of trusting a single AI output, the system forces the AI to:

Generate

Critique itself

Fix its own mistakes

Expose what was corrected

🧩 Agentic Architecture (Critic Pattern)
Doctor Input
   ↓
Input Adapter Agent
   ↓
Generator Agent
   ↓
Critic Agent (Medical Safety Reviewer)
   ↓
Refiner Agent
   ↓
Final Note + Critic Report + Confidence Score

Agents
Agent	Responsibility
Input Agent	Normalizes UI/API input into graph state
Generator Agent	Creates SOAP-style clinical notes
Critic Agent	Flags missing tests, red flags, unsafe language
Refiner Agent	Fixes issues and aligns to best practices
🚀 Why This Is Unique

✅ Prevents hallucinations via self-review
✅ Makes AI decisions explainable
✅ Produces an audit trail
✅ Supports human-in-the-loop approval
✅ Designed for regulated environments

This pattern is applicable to:

Healthcare QA

Legal review

Financial compliance

Responsible AI systems

🛠️ Tech Stack

Python 3.10+

LangGraph (Agent orchestration)

LangChain

OpenAI (via langchain-openai)

Pydantic

LangGraph Studio (Agentic UI)

📁 Project Structure
ai-clinical-note-writer/
│
├── README.md
├── requirements.txt
├── langgraph.json
├── .env
│
├── app/
│   ├── main.py
│   ├── graph.py
│   ├── agents/
│   │   ├── input_agent.py
│   │   ├── generator_agent.py
│   │   ├── critic_agent.py
│   │   └── refiner_agent.py
│   ├── models/
│   │   └── schemas.py
│   └── llm/
│       └── openai_client.py
│
└── examples/
    └── sample_input.txt

⚙️ Setup Instructions
1️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Configure OpenAI Key

Create .env:

OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx


⚠️ LangGraph Studio does not auto-load .env
Export the key manually when using Studio.

▶️ Run via Python (CLI)
python -m app.main

Output Includes:

Generated note

Critic findings

Confidence score

Audit trail

🎛️ Run with Agentic UI (LangGraph Studio)
1️⃣ Start Studio
langgraph dev

2️⃣ Open Browser UI

Select clinical_note_graph

Enter input:

{
  "doctor_input": "Patient has chest pain, ECG borderline, sent home."
}

3️⃣ Observe:

Step-by-step agent execution

State transitions

Critic reasoning

Refined output

This UI allows replayable, inspectable AI decisions

🧪 Example Scenario

Input

Patient has chest pain, ECG borderline, sent home.


Critic Flags

❌ Missing troponin test

❌ No cardiac risk stratification

Refiner Fixes

Adds justification

Inserts follow-up instructions

Improves safety language

📊 POC Outputs

✔ Final refined clinical note
✔ Critic safety report
✔ Confidence score
✔ “What was corrected” audit trail

🧠 Key Design Principles

Agentic AI > Prompt chaining

Deterministic state flow

Explicit safety checks

Human remains final authority

Transparency over automation

🔒 Important Disclaimer

This project is a technical POC only.
It is not a certified medical device and must not be used for real patient care without clinical validation.