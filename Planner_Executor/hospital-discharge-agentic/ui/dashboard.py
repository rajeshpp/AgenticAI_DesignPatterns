import streamlit as st
import requests

st.set_page_config(layout="wide")
st.title("🏥 Agentic Hospital Discharge Dashboard")

if st.button("Run Discharge Planning"):
    response = requests.post("http://localhost:8000/discharge")

    if response.status_code != 200:
        st.error("Backend error")
        st.code(response.text)
    else:
        data = response.json()

        st.subheader("Discharge Plan")
        st.write(data.get("discharge_plan"))

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Medication Plan")
            st.write(data.get("medication_plan"))

            st.subheader("Appointments")
            st.write(data.get("appointments"))

        with col2:
            st.subheader("Patient Education")
            st.write(data.get("education_material"))

            st.subheader("Insurance")
            st.write(data.get("coverage_check"))

        st.subheader("Verifier Status")
        status = data.get("status")
        if status == "APPROVED":
            st.success(status)
        else:
            st.error(status)
