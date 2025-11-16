# 🧠 AgenticAI ReAct — Healthcare Decision-Support Agent (Python)

This project implements a **Healthcare Decision-Support Agent** using the **AgenticAI ReAct (Reasoning + Acting)** design pattern.
The agent simulates a triage workflow for fever symptoms:

**Symptoms → Fetch Vitals → Reason → Consult Guidelines → Take Action**

It demonstrates how ReAct-based agents can make structured, explainable decisions using tools (vitals service, guidelines engine, scheduling system).

---

## 🚀 Features

* **ReAct Loop Implementation**
  Clear Reason → Act → Observe cycle with transparent logic.

* **Modular Tooling**

  * Vitals Tool
  * Clinical Guidelines Tool
  * Follow-up Scheduling Tool

* **Explainable Decision Logic**
  Generates Green / Yellow / Red severity classification.

* **Clean Architecture**
  Environment wrapper + testable tools + agent controller.

* **Unit Tests Included**
  Mocked tools for consistent test behavior.

---

## 📁 Project Structure

```
agenticai-react-healthcare/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── agent.py
│   ├── environment.py
│   ├── tools/
│   │   ├── vitals_tool.py
│   │   ├── guidelines_tool.py
│   │   ├── scheduling_tool.py
│   └── utils/
│       ├── logger.py
│       └── types.py
├── tests/
│   └── test_agent.py
└── examples/
    └── sample_input.json
```

---

## 🧩 How the Agent Works (ReAct Pattern)

### **1️⃣ Observation**

The agent receives patient symptoms.

### **2️⃣ Action**

It calls tools:

* `VitalsTool` → Fetch patient vitals
* `GuidelinesTool` → Interpret clinical risk
* `SchedulingTool` → Book follow-up (for yellow cases)

### **3️⃣ Reasoning**

The agent generates an internal explanation based on findings and classifies risk as:

* **GREEN** → Home care
* **YELLOW** → Needs clinician review within 24 hours
* **RED** → Emergency referral

### **4️⃣ Final Action**

Returns a recommended next step.

---

## 🛠 Installation

```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## ▶️ Run Example

```bash
python -m src.main
```

Sample output:

```json
{
  "patient_id": "patient_123",
  "vitals": {
    "temperature": 38.5,
    "heart_rate": 110
  },
  "level": "YELLOW",
  "guideline": "Consider urgent telehealth / clinician review within 24 hours.",
  "followup": {
    "status": "scheduled",
    "when": "24 hours"
  }
}
```

---

## 🧪 Run Tests

```bash
pytest -q
```
