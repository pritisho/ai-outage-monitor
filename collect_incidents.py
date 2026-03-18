import requests
import json
import os

PROVIDERS = {
    "OpenAI": "https://status.openai.com/api/v2/incidents.json",
    "Claude": "https://status.anthropic.com/api/v2/incidents.json"
}

def fetch_incidents(provider, url, limit=5):
    incidents_list = []

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        for incident in data.get("incidents", [])[:limit]:
            incidents_list.append({
                "provider": provider,
                "name": incident.get("name", "Unknown incident"),
                "status": incident.get("status", "unknown"),
                "created_at": incident.get("created_at", ""),
                "updated_at": incident.get("updated_at", ""),
                "resolved_at": incident.get("resolved_at", ""),
                "impact": incident.get("impact", "unknown")
            })

    except Exception as e:
        incidents_list.append({
            "provider": provider,
            "name": f"Could not fetch incidents: {str(e)}",
            "status": "error",
            "created_at": "",
            "updated_at": "",
            "resolved_at": "",
            "impact": "unknown"
        })

    return incidents_list

def main():
    all_incidents = []

    for provider, url in PROVIDERS.items():
        incidents = fetch_incidents(provider, url, limit=5)
        all_incidents.extend(incidents)

    os.makedirs("history", exist_ok=True)

    with open("history/outage_history.json", "w", encoding="utf-8") as f:
        json.dump(all_incidents, f, indent=2)

    print("Outage history updated successfully.")

if __name__ == "__main__":
    main()