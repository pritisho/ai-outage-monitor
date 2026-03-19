import json

def load_data():
    try:
        with open("history/outage_history.json") as f:
            return json.load(f)
    except:
        return []

def get_outages(provider):
    data = load_data()
    return [x for x in data if x["provider"] == provider]

def get_last_two(provider):
    return get_outages(provider)[:2]

def availability(status_text, incidents):

    if "Operational" in status_text:
        return "100%"

    # fallback calculation
    count = len(incidents)

    if count == 0:
        return "100%"

    return f"{round(100 - count * 0.5,2)}%"
