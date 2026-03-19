import requests
import time
import os

PROVIDERS = {
    "OpenAI": "https://status.openai.com/api/v2/status.json",
    "Claude": "https://status.anthropic.com/api/v2/status.json"
}

def check_status(url):
    start = time.time()
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        status = data["status"]["description"]
    except:
        status = "Unknown"
    latency = round(time.time() - start, 3)
    return status, latency

def save_status(provider, status, latency):
    os.makedirs("documents", exist_ok=True)
    with open(f"documents/{provider.lower()}_status.txt", "w") as f:
        f.write(f"Status: {status}\nLatency: {latency}")

def main():
    for provider, url in PROVIDERS.items():
        status, latency = check_status(url)
        save_status(provider, status, latency)
        print(provider, status, latency)

if __name__ == "__main__":
    main()
