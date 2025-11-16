# 🚀 AgenticAI ReAct — DevOps Diagnostic Automation (Python)

This project demonstrates how to use the **AgenticAI ReAct (Reason + Act)** design pattern to automate DevOps diagnostics.
It follows a real-world scenario:

> **“Server slow → check CPU metrics → analyze → detect errors → notify team → provide final root-cause summary.”**

The agent alternates between **thinking** and **acting**, calling tools such as CPU metrics, log fetchers, and notifiers, just like a production-grade AIOps workflow.

---

## 🧠 What is ReAct?

ReAct = **Reasoning + Acting**

Your agent produces:

1. **Thought** → internal reasoning
2. **Action** → tool call
3. **Observation** → tool output
4. **Reflection** → next step

This pattern makes LLM agents:

* interpretable,
* controllable,
* safe,
* and suitable for operational workflows.

---

## 💼 Use Case: DevOps Diagnostics

### Scenario

A user reports **“Server slow”**.
The agent automatically:

1. Fetches CPU metrics
2. If CPU is high → alerts the team
3. If CPU is normal → fetches logs
4. Detects errors and notifies the team
5. Returns a **root cause summary**

---

## 🏗️ Project Structure

```
agenticai-react-devops/
├─ README.md
├─ requirements.txt
├─ .env.example
├─ run.sh
├─ react_agent.py
├─ agent_core.py
├─ tools/
│  ├─ cpu_api.py
│  ├─ logs_api.py
│  └─ notifier.py
└─ utils/
   ├─ memory.py
   └─ pretty.py
```

---

## 🔧 Tools Implemented

| Tool                 | Purpose                                   |
| -------------------- | ----------------------------------------- |
| **CPU Metrics Tool** | Simulates Prometheus/CloudWatch CPU usage |
| **Logs Tool**        | Returns error logs and message samples    |
| **Notifier Tool**    | Simulates Slack/PagerDuty alerts          |

All tools return structured JSON-like Python objects.

---

## 📌 Key Features

* 🧠 **ReAct-style agent loop**
* 🪝 **Pluggable tools** (easy to integrate real APIs)
* 📘 **Memory transcript** (for agent reasoning history)
* 📊 **Pretty console logs** (powered by `rich`)
* ⚡ **Deterministic demo** (can be extended with LLM reasoning)
* 🛠️ **Notifier integration** — includes alert messages when CPU is high or logs contain errors

---

## ▶️ Running the POC

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Run the demo

```
python react_agent.py
```

### 3. Example Output (shortened)

```
Thought: I should check CPU usage first...
Action: get_cpu_metrics(last_5m)
Observation: { 'cpu_avg': 92 }

Action: notify(ALERT: High CPU 92% detected ...)
[notifier] alert -> ALERT: High CPU 92% detected ...

=== FINAL ANALYSIS ===
High CPU observed (92%). Possible cause: CPU-bound process.
```

---

## 🧩 How It Works (Architecture)

```
[User Input]
      ↓
 [ReAct Agent]
      ↓
 ┌───────────────┬───────────────────────────┬───────────────────┐
 | Reason (Thought) → Decide Action           |                   |
 | Act (Tool Call) → Observe Result           |   Tools Layer     |
 | Reflect → Choose Next Step                 |                   |
 └───────────────┴───────────────────────────┴───────────────────┘
      ↓
  Final Diagnosis
```

---

## 🔮 Extending the POC

You can easily expand this into a production-grade Agentic AI setup:

### 🚀 Drop in a real LLM

Replace `think()` in `agent_core.py` with:

* OpenAI GPT-4o-mini
* Anthropic Claude
* Local Llama models via Ollama

### 📈 Connect real DevOps APIs

Integrate:

* Prometheus CPU metrics
* CloudWatch Logs
* ElasticSearch queries
* Kubernetes pod logs
* PagerDuty/Splunk alerts

### ⚙️ Use pydantic models

Add strict input/output validation for tool schemas.

---

## 🙌 Why This Matters

This project embodies the future of **AIOps**:

> **Agents that think, act, and diagnose operational issues automatically — not just return text.**

It’s a perfect starting point for:

* DevOps engineers
* SREs
* AI engineers building agentic systems
* Anyone exploring real-world ReAct architecture