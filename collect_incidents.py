import requests
import json
import os
from datetime import datetime

PROVIDERS = {
    "OpenAI": "https://status.openai.com/api/v2/incidents.json",
    "Claude": "https://status.anthropic.com/api/v2/incidents.json"
}

def calculate_downtime(start, end):
    try:
        start_time = datetime.fromisoformat(start.replace("Z", ""))
        end_time = datetime.fromisoformat(end.replace("Z", "")) if end else datetime.utcnow()
        downtime = (end_time - start_time).total_seconds() / 60
        return round(downtime, 2)
    except:
        return 0

def fetch_incidents(provider, url):
    incidents = []

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        for inc in data["incidents"][:5]:

            downtime = calculate_downtime(
                inc.get("created_at"),
                inc.get("resolved_at")
            )

            incidents.append({
                "provider": provider,
                "name": inc.get("name"),
                "status": inc.get("status"),
                "start_time": inc.get("created_at"),
                "end_time": inc.get("resolved_at"),
                "impact": inc.get("impact"),
                "downtime_minutes": downtime
            })

    except Exception as e:
        incidents.append({
            "provider": provider,
            "name": str(e),
            "status": "error"
        })

    return incidents

def main():
    all_data = []

    for provider, url in PROVIDERS.items():
        all_data.extend(fetch_incidents(provider, url))

    os.makedirs("history", exist_ok=True)

    with open("history/outage_history.json", "w") as f:
        json.dump(all_data, f, indent=2)

    print("Outage data updated")

if __name__ == "__main__":
    main()
