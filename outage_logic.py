import json
import pandas as pd

HISTORY_FILE = "history/outage_history.json"

def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame()

def get_provider_outages(provider):
    df = load_history()
    if df.empty:
        return pd.DataFrame()

    filtered = df[df["provider"] == provider].copy()

    if "created_at" in filtered.columns:
        filtered = filtered.sort_values(by="created_at", ascending=False)

    return filtered

def get_last_n_outages(provider, n=5):
    df = get_provider_outages(provider)
    return df.head(n)

def get_incident_count(provider):
    df = get_provider_outages(provider)
    return len(df)

def get_availability_score(provider):
    df = get_provider_outages(provider)

    if len(df) == 0:
        return "100%"

    count = len(df)

    if count == 1:
        return "99.9%"
    if count <= 3:
        return "99.5%"
    if count <= 5:
        return "99.0%"
    return "98.0%"