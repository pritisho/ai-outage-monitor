import streamlit as st
import json
from outage_logic import get_last_two, get_outages, availability
from llm_engine import generate_answer

st.set_page_config(page_title="AI Outage Monitor", layout="wide")

st.title("AI Reliability Dashboard")

def read_status(provider):
    try:
        with open(f"documents/{provider.lower()}_status.txt") as f:
            return f.read()
    except:
        return "Unknown"

openai_status = read_status("OpenAI")
claude_status = read_status("Claude")

# STATUS DISPLAY
col1, col2 = st.columns(2)

with col1:
    st.subheader("OpenAI")
    st.text(openai_status)

with col2:
    st.subheader("Claude")
    st.text(claude_status)

# LOAD INCIDENT DATA
with open("history/outage_history.json") as f:
    data = json.load(f)

openai_incidents = get_outages("OpenAI")
claude_incidents = get_outages("Claude")

# ALERTS
if "Operational" not in openai_status:
    st.error("🚨 OpenAI Outage Detected")

if "Operational" not in claude_status:
    st.error("🚨 Claude Outage Detected")

# METRICS
st.header("Availability")

c1, c2 = st.columns(2)

with c1:
    st.metric("OpenAI Availability", availability(openai_status, openai_incidents))

with c2:
    st.metric("Claude Availability", availability(claude_status, claude_incidents))

# OUTAGE DETAILS
st.header("Last 2 Outages")

for provider in ["OpenAI", "Claude"]:

    st.subheader(provider)

    outages = get_last_two(provider)

    for o in outages:
        st.write({
            "Name": o["name"],
            "Impact": o.get("impact"),
            "Start": o.get("start_time"),
            "End": o.get("end_time"),
            "Downtime (min)": o.get("downtime_minutes")
        })

# AI QUESTION
st.header("Ask AI")

question = st.text_input("Ask about outages")

if question:
    combined = f"""
OpenAI:
{openai_status}

Claude:
{claude_status}
"""

    answer = generate_answer(question, combined, data)

    st.subheader("Answer")
    st.write(answer)
