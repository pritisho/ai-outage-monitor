import streamlit as st
import requests
import os
import json
from datetime import datetime
from openai import OpenAI

# ------------------ PAGE ------------------
st.set_page_config(page_title="AI Outage Monitor", layout="wide")
st.title("AI Reliability Dashboard")

# ------------------ OPENAI ------------------
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ OPENAI_API_KEY not found. Set it in Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# ------------------ STATUS ------------------
def fetch_status():
    providers = {
        "OpenAI": "https://status.openai.com/api/v2/status.json",
        "Claude": "https://status.anthropic.com/api/v2/status.json"
    }

    results = {}

    for name, url in providers.items():
        try:
            start = datetime.now()
            r = requests.get(url, timeout=10)
            latency = (datetime.now() - start).total_seconds()

            status = r.json()["status"]["description"]

            results[name] = {
                "status": status,
                "latency": round(latency, 3)
            }

        except:
            results[name] = {
                "status": "Unknown",
                "latency": None
            }

    return results

# ------------------ INCIDENTS ------------------
def fetch_incidents():
    providers = {
        "OpenAI": "https://status.openai.com/api/v2/incidents.json",
        "Claude": "https://status.anthropic.com/api/v2/incidents.json"
    }

    all_data = []

    for provider, url in providers.items():
        try:
            r = requests.get(url, timeout=10)
            data = r.json()

            for inc in data.get("incidents", [])[:5]:

                updates = inc.get("incident_updates", [])

                timestamps = []

                for u in updates:
                    ts = u.get("created_at")
                    if ts:
                        timestamps.append(ts)

                # fallback if updates missing
                if not timestamps:
                    if inc.get("created_at"):
                        timestamps.append(inc.get("created_at"))
                    if inc.get("resolved_at"):
                        timestamps.append(inc.get("resolved_at"))

                start = min(timestamps) if timestamps else None
                end = max(timestamps) if timestamps else None

                # downtime calculation
                downtime = None
                try:
                    if start and end:
                        s = datetime.fromisoformat(start.replace("Z", ""))
                        e = datetime.fromisoformat(end.replace("Z", ""))

                        diff = (e - s).total_seconds() / 60

                        if diff > 1:
                            downtime = round(diff, 2)
                        else:
                            downtime = "Very short / instant"
                except:
                    downtime = None

                all_data.append({
                    "provider": provider,
                    "name": inc.get("name"),
                    "impact": inc.get("impact"),
                    "start_time": start,
                    "end_time": end,
                    "downtime_minutes": downtime
                })

        except Exception as e:
            all_data.append({
                "provider": provider,
                "name": str(e),
                "impact": "error"
            })

    return all_data

# ------------------ AVAILABILITY ------------------
def calculate_availability(status, incidents):
    if "Operational" in status:
        return "100%"
    if len(incidents) == 0:
        return "100%"
    return f"{round(100 - len(incidents) * 0.5, 2)}%"

# ------------------ LLM ------------------
def generate_answer(question, status_data, incidents):

    prompt = f"""
You are a Site Reliability Engineer.

Answer clearly:
1. Is there a current outage?
2. If yes → explain it
3. If no → give last 2 outages
4. Include impact and downtime
5. Be precise

STATUS:
{json.dumps(status_data, indent=2)}

INCIDENTS:
{json.dumps(incidents, indent=2)}

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
        return f"LLM Error: {str(e)}"

# ------------------ LOAD DATA ------------------
status_data = fetch_status()
incident_data = fetch_incidents()

# ------------------ UI STATUS ------------------
col1, col2 = st.columns(2)

for col, provider in zip([col1, col2], ["OpenAI", "Claude"]):
    with col:
        st.subheader(provider)
        st.write("Status:", status_data[provider]["status"])
        st.metric("Latency (sec)", status_data[provider]["latency"])

# ------------------ ALERT ------------------
for provider in ["OpenAI", "Claude"]:
    if "Operational" not in status_data[provider]["status"]:
        st.error(f"🚨 {provider} outage detected")

# ------------------ AVAILABILITY ------------------
st.header("Availability")

c1, c2 = st.columns(2)

openai_incidents = [x for x in incident_data if x["provider"] == "OpenAI"]
claude_incidents = [x for x in incident_data if x["provider"] == "Claude"]

with c1:
    st.metric("OpenAI Availability",
              calculate_availability(status_data["OpenAI"]["status"], openai_incidents))

with c2:
    st.metric("Claude Availability",
              calculate_availability(status_data["Claude"]["status"], claude_incidents))

# ------------------ OUTAGES ------------------
st.header("Last 2 Outages")

for provider in ["OpenAI", "Claude"]:
    st.subheader(provider)

    outages = [x for x in incident_data if x["provider"] == provider][:2]

    if not outages:
        st.write("No outages found")
    else:
        for o in outages:
            st.write({
                "Name": o["name"],
                "Impact": o["impact"],
                "Start Time": o["start_time"],
                "End Time": o["end_time"],
                "Downtime": o["downtime_minutes"]
            })

# ------------------ AI ------------------
st.header("Ask AI")

question = st.text_input("Ask about outages")

if question:
    answer = generate_answer(question, status_data, incident_data)
    st.subheader("AI Answer")
    st.write(answer)
