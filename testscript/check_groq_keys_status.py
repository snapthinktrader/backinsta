#!/usr/bin/env python3
"""
Test script to check the validity of all Groq API keys found across the system.
Queries the official Groq API endpoint https://api.groq.com/openai/v1/models.
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

def get_keys_to_test():
    keys = []
    # Load from GROQ_API_KEYS / GROQ_API_KEY environment variables
    env_keys = os.getenv("GROQ_API_KEYS", "")
    if env_keys:
        for idx, k in enumerate(env_keys.split(",")):
            k = k.strip()
            if k:
                keys.append((k, f"Key {idx+1} (from GROQ_API_KEYS)"))
    single = os.getenv("GROQ_API_KEY")
    if single and single not in [k[0] for k in keys]:
        keys.insert(0, (single.strip(), "Primary Key (from GROQ_API_KEY)"))
    return keys

def check_keys():
    keys_to_test = get_keys_to_test()
    print(f"============================================================")
    print(f"Verifying {len(keys_to_test)} Groq API Keys against api.groq.com")
    print(f"============================================================\n")

    active_count = 0
    inactive_count = 0

    for idx, (key, label) in enumerate(keys_to_test, 1):
        url = "https://api.groq.com/openai/v1/models"
        headers = {"Authorization": f"Bearer {key}"}
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            masked = key[:10] + "..." + key[-6:]
            if resp.status_code == 200:
                models = resp.json().get("data", [])
                print(f"[{idx:02d}] ✅ ACTIVE   | {label:32} | {masked} | Status: 200 OK ({len(models)} models available)")
                active_count += 1
            elif resp.status_code == 401:
                print(f"[{idx:02d}] ❌ INVALID  | {label:32} | {masked} | Status: 401 Unauthorized")
                inactive_count += 1
            elif resp.status_code == 429:
                print(f"[{idx:02d}] ⚠️ RATE LMT | {label:32} | {masked} | Status: 429 Rate Limit Exceeded")
                active_count += 1
            else:
                print(f"[{idx:02d}] ⚠️ ERROR    | {label:32} | {masked} | Status: {resp.status_code}")
                inactive_count += 1
        except Exception as e:
            print(f"[{idx:02d}] ❌ TIMEOUT  | {label:32} | {masked} | Error: {e}")
            inactive_count += 1

    print(f"\n============================================================")
    print(f"Summary: {active_count} Active / {inactive_count} Inactive out of {len(keys_to_test)} keys")
    print(f"============================================================")

if __name__ == "__main__":
    check_keys()
