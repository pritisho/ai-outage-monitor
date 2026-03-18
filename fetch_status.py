import requests
import os

PROVIDERS = {
    "OpenAI": "https://status.openai.com/api/v2/status.json",
    "Claude": "https://status.anthropic.com/api/v2/status.json"
}

def check_status(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data["status"]["description"]
    except Exception as e:
        return f"Unknown ({str(e)})"

def save_status(provider, status):
    os.makedirs("documents", exist_ok=True)
    file_path = f"documents/{provider.lower()}_status.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"Current status: {status}")

def main():
    for provider, url in PROVIDERS.items():
        status = check_status(url)
        save_status(provider, status)
        print(f"{provider} status updated: {status}")

if __name__ == "__main__":
    main()