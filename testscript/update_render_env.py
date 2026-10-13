#!/usr/bin/env python3
"""
Script to update environment variables on Render service srv-d672k80gjchc73e78l80
"""

import os
import json
import requests
from pathlib import Path

SERVICE_ID = "srv-d672k80gjchc73e78l80"
CONFIG_FILE = Path.home() / ".render" / "profiles" / "backinsta.yaml"

def get_api_key():
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Missing {CONFIG_FILE}")
    with open(CONFIG_FILE, "r") as f:
        for line in f:
            if "key:" in line:
                return line.split(":", 1)[1].strip()
    raise ValueError("API key not found in backinsta.yaml")

def main():
    api_key = get_api_key()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    print(f"📡 Fetching existing env-vars for {SERVICE_ID}...")
    res = requests.get(f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars", headers=headers)
    if res.status_code != 200:
        print(f"❌ Failed to fetch env vars: {res.status_code} - {res.text}")
        return

    existing_vars = res.json()
    env_dict = {item["envVar"]["key"]: item["envVar"]["value"] for item in existing_vars}
    print(f"Found {len(env_dict)} existing environment variables.")

    from dotenv import load_dotenv
    load_dotenv()

    # Values to add or update
    updates = {
        "USE_FACEBOOK_PAGE": os.getenv("USE_FACEBOOK_PAGE", "true"),
        "FB_PAGE_ID": os.getenv("FB_PAGE_ID", "1394981273691815"),
        "FB_PAGE_ACCESS_TOKEN": os.getenv("FB_PAGE_ACCESS_TOKEN", ""),
        "REACT_APP_ACCESS_TOKEN": os.getenv("REACT_APP_ACCESS_TOKEN", ""),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY", "")
    }

    env_dict.update(updates)

    # Format for PUT /env-vars
    payload = [{"key": k, "value": v} for k, v in env_dict.items()]

    print(f"\n📤 Updating {len(payload)} environment variables on Render...")
    put_res = requests.put(
        f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars",
        headers=headers,
        json=payload
    )

    if put_res.status_code == 200:
        print("✅ Environment variables updated successfully on Render!")
        for k in updates.keys():
            print(f"   - {k} synced")
    else:
        print(f"❌ Failed to update env vars: {put_res.status_code} - {put_res.text}")

if __name__ == "__main__":
    main()
