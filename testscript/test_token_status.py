#!/usr/bin/env python3
"""
Test script to check current Instagram / Facebook Graph API Access Token status.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

ACCESS_TOKEN = os.getenv('REACT_APP_ACCESS_TOKEN') or os.getenv('FB_ACCESS_TOKEN') or os.getenv('ACCESS_TOKEN')
INSTAGRAM_ACCOUNT_ID = os.getenv('REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID', '17841474412696876')

def check_token():
    if not ACCESS_TOKEN:
        print("❌ ERROR: No ACCESS_TOKEN found in environment or .env file.")
        return

    print("🔍 Checking Facebook / Instagram Graph API Access Token status...")
    print(f"🔑 Account ID: {INSTAGRAM_ACCOUNT_ID}")
    print(f"🔑 Token preview: {ACCESS_TOKEN[:10]}...{ACCESS_TOKEN[-6:]}")

    # Query Graph API debug endpoint / me endpoint
    url = "https://graph.facebook.com/v21.0/me"
    params = {
        "access_token": ACCESS_TOKEN
    }

    try:
        res = requests.get(url, params=params, timeout=15)
        data = res.json()

        if res.status_code == 200:
            print("✅ FACEBOOK TOKEN IS VALID!")
            print(f"👤 User/Page Info: {data}")

            # Also verify Instagram Business Account access
            ig_url = f"https://graph.facebook.com/v21.0/{INSTAGRAM_ACCOUNT_ID}"
            ig_params = {
                "fields": "username,name,id,media_count",
                "access_token": ACCESS_TOKEN
            }
            ig_res = requests.get(ig_url, params=ig_params, timeout=15)
            if ig_res.status_code == 200:
                print("✅ INSTAGRAM BUSINESS ACCOUNT ACCESS VERIFIED!")
                print(f"📸 IG Account Details: {ig_res.json()}")
            else:
                print(f"⚠️ Instagram Business Account query returned HTTP {ig_res.status_code}: {ig_res.json()}")
        else:
            print("❌ TOKEN IS INVALID OR EXPIRED!")
            print(f"HTTP Status Code: {res.status_code}")
            print(f"Error Response: {data}")

            error = data.get("error", {})
            code = error.get("code")
            subcode = error.get("error_subcode")
            msg = error.get("message")

            print("\n📋 Diagnostic Summary:")
            print(f" - Error Code: {code}")
            print(f" - Error Subcode: {subcode}")
            print(f" - Message: {msg}")

            if code == 190:
                if subcode == 460:
                    print(" 💡 Reason: User changed Facebook password or session was invalidated by Facebook.")
                elif subcode == 463:
                    print(" 💡 Reason: Token has reached its 60-day expiration period.")
                else:
                    print(" 💡 Reason: Access token is invalid or session expired.")

    except Exception as e:
        print(f"⚠️ Request failed with exception: {e}")

if __name__ == "__main__":
    check_token()
