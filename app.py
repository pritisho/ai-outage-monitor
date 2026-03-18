import streamlit as st
import os
from outage_logic import get_last_n_outages, get_incident_count, get_availability_score

st.set_page_config(page_title="AI Outage Monitor", layout="wide")

st.title("AI Provider Reliability Dashboard")
st.write("Monitor current status, recent outages, and availability metrics for OpenAI and Claude.")

providers = ["OpenAI", "Claude"]

st.header("Current Provider Status")

col1, col2 = st.columns(2)

for i, provider in enumerate(providers):
    file_path = f"documents/{provider.lower()}_status.txt"

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            status_text = f.read()
    else:
        status_text = "Current status: Unknown"

    with (col1 if i == 0 else col2):
        st.subheader(provider)
        if "Operational" in status_text:
            st.success(status_text)
        elif "Unknown" in status_text:
            st.warning(status_text)
        else:
            st.error(status_text)

st.header("Availability Metrics")

metric_col1, metric_col2 = st.columns(2)

with metric_col1:
    st.metric("OpenAI Incident Count", get_incident_count("OpenAI"))
    st.metric("OpenAI Availability Score", get_availability_score("OpenAI"))

with metric_col2:
    st.metric("Claude Incident Count", get_incident_count("Claude"))
    st.metric("Claude Availability Score", get_availability_score("Claude"))

st.header("Last 5 Outages")

for provider in providers:
    st.subheader(provider)
    outages = get_last_n_outages(provider, 5)

    if outages.empty:
        st.info(f"No outage history available for {provider}.")
    else:
        st.dataframe(outages, use_container_width=True)