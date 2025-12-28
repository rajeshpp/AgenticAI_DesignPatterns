# 🧠 AI-Driven Clinical Decision Support  
## Planner–Executor Agentic Architecture (POC)

This repository demonstrates an **Agentic AI–based Clinical Decision Support System (CDSS)** designed for **complex multi-comorbidity cases**, such as:

- Diabetes + Cardiac conditions  
- Diabetes + Renal disease  
- Cardiac + Renal overlap  

The system follows a **Planner → Executor → Verifier** pattern to reflect how experienced clinicians reason, while keeping **humans firmly in the loop**.

---

## 🎯 Problem Statement

Clinical decision-making becomes difficult when:

- Patients present with multiple interacting symptoms  
- Conditions influence each other  
- Clinical guidelines conflict  
- Medications carry renal or cardiac risks  

Single-prompt LLMs or static rule engines struggle with this level of complexity.

---

## 💡 Solution Overview

This POC implements a **multi-agent, modular reasoning system**.

### 🧭 Planner Agent
- Analyzes patient context (conditions, symptoms, labs, medications)
- Decomposes the case into structured reasoning tasks:
  - Diagnostic hypotheses
  - Medication safety checks
  - Guideline mapping
  - Risk assessment

### ⚙️ Executor Agents (Specialized)
- **Diagnosis Agent** – Differential diagnosis and red-flag detection  
- **Drug Interaction Agent** – Contraindications and medication safety  
- **Guidelines Agent** – Mapping findings to clinical protocols  

### 🛡️ Verifier / Critic Agent
- Validates safety and consistency
- Resolves guideline conflicts
- Ensures explainability and decision-support boundaries

> **Plan globally. Execute locally. Verify critically.**

---

## 🧠 Why Agentic AI?

This architecture is intentionally **agentic**, not monolithic:

- Global reasoning is separated from specialized execution  
- Medical decision-making is modular by nature  
- Safety and explainability are first-class requirements  
- Each agent has a clear, auditable responsibility  

The result is **reduced cognitive load** without replacing clinicians.

---

## 🏗️ Architecture Pattern

```
Patient Context
↓
Planner Agent
↓
┌────────────────┬──────────────────┬──────────────────┐
│ Diagnosis │ Drug Safety │ Guidelines │
│ Agent │ Agent │ Agent │
└────────────────┴──────────────────┴──────────────────┘
↓
Verifier / Safety Agent
↓
Explainable Clinical Decision Support
```


---

## 📊 Outcomes

- Faster, structured clinical reasoning  
- Reduced medication-related risk  
- Explicit guideline alignment  
- Transparent, explainable outputs  
- Human-in-the-loop by design  

⚠️ **This system provides decision support only.  
Final medical decisions must be made by qualified clinicians.**

---

## 🧪 Demo Capabilities

- Synthetic patient data (safe for demos)
- Planner–Executor reasoning flow
- Optional live agent traces (CrewAI UI)
- Offline deterministic mock mode

---

## 🛠️ Tech Stack

- Python  
- CrewAI (Agent Orchestration)  
- Large Language Model (online or mock mode)  
- Planner–Executor–Verifier design pattern  

---

## 🔒 Safety & Responsibility

- No autonomous diagnosis  
- No prescription generation  
- Read-only decision support  
- Explicit safety verification layer  
- Designed for explainability and auditability  

---

## 🌍 Applicability Beyond Healthcare

The same pattern applies to:

- Financial risk analysis  
- Insurance underwriting  
- Compliance & regulatory workflows  
- Supply chain optimization  
- Enterprise decision automation  

Anywhere **complex reasoning > simple retrieval**, this architecture scales.

---

## 🚀 Next Steps

Potential extensions:

- FHIR-based EHR ingestion  
- Confidence scoring per recommendation  
- Human approval workflows  
- Streamlit or web UI  
- LangGraph implementation for comparison  

---