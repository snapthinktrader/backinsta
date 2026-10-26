#!/usr/bin/env python3
"""
Create and deploy backinsta web service on the new Render account (ajt261999@gmail.com).
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

CONFIG_FILE = Path.home() / ".render" / "profiles" / "backinsta.yaml"
ENV_FILE = Path("/Users/ajaytiwari/Desktop/Projects/backinsta/.env")

def get_api_key_and_owner():
    with open(CONFIG_FILE, "r") as f:
        data = {}
        for line in f:
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip().strip("'\"")
    key = data.get("key")
    owner_id = data.get("workspace")
    return key, owner_id

def main():
    api_key, owner_id = get_api_key_and_owner()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    print("🚀 Creating new backinsta Web Service on Render...")
    payload = {
        "type": "web_service",
        "name": "backinsta",
        "ownerId": owner_id,
        "repo": "https://github.com/snapthinktrader/backinsta",
        "branch": "main",
        "autoDeploy": "yes",
        "serviceDetails": {
            "env": "python",
            "plan": "free",
            "region": "singapore",
            "envSpecificDetails": {
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "python scheduled_poster.py"
            },
            "healthCheckPath": "/health",
            "numInstances": 1
        }
    }

    res = requests.post("https://api.render.com/v1/services", headers=headers, json=payload)
    if res.status_code not in [200, 201]:
        print(f"❌ Failed to create service: {res.status_code} - {res.text}")
        sys.exit(1)

    svc_data = res.json()
    service_id = svc_data.get("service", {}).get("id") or svc_data.get("id")
    svc_url = svc_data.get("service", {}).get("serviceDetails", {}).get("url") or svc_data.get("serviceDetails", {}).get("url")
    print(f"✅ Service created successfully!")
    print(f"   ID:  {service_id}")
    print(f"   URL: {svc_url}")

    # Load env vars from .env
    load_dotenv(ENV_FILE)
    env_keys = [
        "GROQ_MODEL", "GROQ_API_KEY", "GROQ_API_KEYS", "IMGBB_API_KEY",
        "MONGODB_URI", "NYT_API_KEY", "PORT", "POST_INTERVAL_MINUTES",
        "REACT_APP_ACCESS_TOKEN", "REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID",
        "USE_BACKGROUND_AUDIO", "USE_INSTAGRAM_REELS", "USE_VOICE_NARRATION",
        "USE_YOUTUBE_SHORTS", "YOUTUBE_CREDENTIALS_BASE64", "YOUTUBE_TOKEN_BASE64",
        "USE_FACEBOOK_PAGE", "FB_PAGE_ID", "FB_PAGE_ACCESS_TOKEN"
    ]

    env_payload = []
    for k in env_keys:
        val = os.getenv(k)
        if val is not None:
            env_payload.append({"key": k, "value": val})

    print(f"\n📤 Syncing {len(env_payload)} environment variables to {service_id}...")
    env_res = requests.put(
        f"https://api.render.com/v1/services/{service_id}/env-vars",
        headers=headers,
        json=env_payload
    )

    if env_res.status_code in [200, 201]:
        print("✅ Environment variables successfully synced on Render!")
    else:
        print(f"⚠️ Env var sync returned: {env_res.status_code} - {env_res.text}")

    # Trigger fresh deployment with env vars applied
    print(f"\n🚀 Triggering fresh deployment for {service_id}...")
    dep_res = requests.post(f"https://api.render.com/v1/services/{service_id}/deploys", headers=headers, json={"clearCache": "do_not_clear"})
    if dep_res.status_code in [200, 201]:
        dep_data = dep_res.json()
        dep_id = dep_data.get("id") or dep_data.get("deploy", {}).get("id")
        print(f"✅ Deployment triggered! Deploy ID: {dep_id}")
    else:
        print(f"ℹ️ Deployment trigger response: {dep_res.status_code}")

    print("\n🎉 BACKINSTA IS NOW PROVISIONED ON YOUR NEW RENDER ACCOUNT!")

if __name__ == "__main__":
    main()
