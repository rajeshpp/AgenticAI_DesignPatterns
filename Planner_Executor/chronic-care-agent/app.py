import streamlit as st
import json

from agents.planner import create_care_plan
from agents.wearable_monitor import analyze_wearable_data
from agents.medication_agent import check_medication_adherence
from agents.lifestyle_agent import lifestyle_recommendation
from agents.alert_agent import escalate
from agents.critic import critic_review

st.set_page_config(page_title="Chronic Care Agentic POC", layout="wide")
st.title("🧠 Personalized Chronic Disease Management (Agentic POC)")

# Load data
patient = json.load(open("data/patient_profile.json"))
wearable = json.load(open("data/wearable_data.json"))
med_log = json.load(open("data/medication_log.json"))

# Planner Agent
st.header("📋 Planner Agent")
care_plan = create_care_plan(patient)
st.text_area("30-Day Care Plan", care_plan, height=220)

# Executor Agents
st.header("⚙️ Executor Agents")

bp_alerts = analyze_wearable_data(wearable)
med_status = check_medication_adherence(med_log)
lifestyle_tip = lifestyle_recommendation("BP slightly elevated over last 3 days")

st.subheader("⌚ Wearable Monitoring")
st.write(bp_alerts or "No BP alerts")

st.subheader("💊 Medication Adherence")
st.write(med_status)

st.subheader("🏃 Lifestyle Coaching")
st.write(lifestyle_tip)

# Alert & Escalation
st.header("🚨 Alert & Escalation")
alert_decision = escalate(bp_alerts)
st.json(alert_decision)

# Critic Agent
st.header("🛡️ Critic Agent (Safety Check)")
critic_issues = critic_review(
    care_plan,
    [med_status, lifestyle_tip]
)

if critic_issues:
    st.error(critic_issues)
else:
    st.success("No safety or compliance issues detected")
