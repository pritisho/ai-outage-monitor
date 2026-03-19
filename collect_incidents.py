import requests
import json
import os
from datetime import datetime

PROVIDERS = {
    "OpenAI": "https://status.openai.com/api/v2/incidents.json",
    "Claude": "https://status.anthropic.com/api/v2/incidents.json"
}

def calculate_times(incident):

    updates = incident.get("incident_updates", [])

    start_time = None
    end_time = None

    if updates:
        # First update = start
        start_time = updates[0].get("created_at")

        # Find resolved update
        for u in updates:
            if u.get("status") == "resolved":
                end_time = u.get("created_at")

    # Fallback if missing
    if not start_time:
        start_time = incident.get("created_at")

    if not end_time:
        end_time = incident.get("resolved_at")

    return start_time, end_time


def calculate_downtime(start, end):
    try:
        if not start or not end:
            return None

        s = datetime.fromisoformat(start.replace("Z", ""))
        e = datetime.fromisoformat(end.replace("Z", ""))

        return round((e - s).total_seconds() / 60, 2)
    except:
        return None


def fetch_incidents(provider, url):
    incidents = []

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        for inc in data["incidents"][:5]:

            start, end = calculate_times(inc)
            downtime = calculate_downtime(start, end)

            incidents.append({
                "provider": provider,
                "name": inc.get("name"),
                "impact": inc.get("impact"),
                "start_time": start,
                "end_time": end,
                "downtime_minutes": downtime
            })

    except Exception as e:
        incidents.append({
            "provider": provider,
            "name": str(e),
            "impact": "error"
        })

    return incidents


def main():
    all_data = []

    for provider, url in PROVIDERS.items():
        all_data.extend(fetch_incidents(provider, url))

    os.makedirs("history", exist_ok=True)

    with open("history/outage_history.json", "w") as f:
        json.dump(all_data, f, indent=2)

    print("Outage data updated successfully")


if __name__ == "__main__":
    main()
