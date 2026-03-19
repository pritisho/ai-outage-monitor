import streamlit as st
import json
import os
import sys
from datetime import datetime
from openai import OpenAI

# ---------- FIX PATH (important for Streamlit) ----------
sys.path.insert(0, os.path.dirname(__file__))

# ---------- OPENAI CLIENT ----------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="AI Outage Monitor", layout="wide")

st.title("AI Reliability Dashboard")

# ---------- READ STATUS FILE ----------
def read_status(provider):
    try:
        with open(f"documents/{provider.lower()}_status.txt") as f:
            return f.read()
    except:
        return "Status: Unknown\nLatency: Unknown"

# ---------- LOAD INCIDENT DATA ----------
def load_incidents():
    try:
        with open("history/outage_history.json") as f:
            return json.load(f)
    except:
        return []

# ---------- FILTER INCIDENTS ----------
def get_outages(provider, data):
    return [x for x in data if x.get("provider") == provider]

def get_last_two(provider, data):
    return get_outages(provider, data)[:2]

# ---------- AVAILABILITY ----------
def availability(status_text, incidents):
    if "Operational" in status_text:
        return "100%"
    if len(incidents) == 0:
        return "100%"
    return f"{round(100 - len(incidents) * 0.5, 2)}%"

# ---------- PARSE LATENCY ----------
def extract_latency(status_text):
    try:
        for line in status_text.split("\n"):
            if "Latency" in line:
                return line.split(":")[1].strip()
    except:
        return "Unknown"
    return "Unknown"

# ---------- LLM ANSWER ----------
def generate_answer(question, status_text, incidents):

    prompt = f"""
You are a Site Reliability Engineer.

Answer clearly:

1. Is there a current outage?
2. If yes → explain the issue
3. If no → list last 2 outages with details
4. Mention impact (major/minor)
5. Mention downtime

STATUS:
{status_text}

INCIDENTS:
{incidents}

QUESTION:
{question}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error from AI: {str(e)}"

# ---------- LOAD DATA ----------
openai_status = read_status("OpenAI")
claude_status = read_status("Claude")

data = load_incidents()

openai_incidents = get_outages("OpenAI", data)
claude_incidents = get_outages("Claude", data)

# ---------- STATUS DISPLAY ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("OpenAI")
    st.text(openai_status)
    st.metric("Latency (sec)", extract_latency(openai_status))

with col2:
    st.subheader("Claude")
    st.text(claude_status)
    st.metric("Latency (sec)", extract_latency(claude_status))

# ---------- ALERTS ----------
if "Operational" not in openai_status:
    st.error("🚨 OpenAI Outage Detected")

if "Operational" not in claude_status:
    st.error("🚨 Claude Outage Detected")

# ---------- AVAILABILITY ----------
st.header("Availability")

c1, c2 = st.columns(2)

with c1:
    st.metric("OpenAI Availability", availability(openai_status, openai_incidents))

with c2:
    st.metric("Claude Availability", availability(claude_status, claude_incidents))

# ---------- OUTAGE DETAILS ----------
st.header("Last 2 Outages")

for provider in ["OpenAI", "Claude"]:
    st.subheader(provider)

    outages = get_last_two(provider, data)

    if not outages:
        st.write("No recent outages found")
    else:
        for o in outages:
            st.write({
                "Name": o.get("name"),
                "Impact": o.get("impact"),
                "Start Time": o.get("start_time"),
                "End Time": o.get("end_time"),
                "Downtime (minutes)": o.get("downtime_minutes")
            })

# ---------- AI QUESTION ----------
st.header("Ask AI")

question = st.text_input("Ask about outages")

if question:
    combined_status = f"""
OpenAI:
{openai_status}

Claude:
{claude_status}
"""

    answer = generate_answer(question, combined_status, data)

    st.subheader("AI Answer")
    st.write(answer)
