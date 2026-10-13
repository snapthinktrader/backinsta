#!/usr/bin/env python3
"""
Test script to check connection and permissions for Facebook Page ID 1394981273691815
using the newly provided Graph API Explorer User Token.
"""

import json
import requests

from dotenv import load_dotenv
load_dotenv()

TARGET_PAGE_ID = os.getenv("FB_PAGE_ID", "1394981273691815")
GRAPH_API_VERSION = "v21.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

NEW_USER_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN") or os.getenv("REACT_APP_ACCESS_TOKEN")

def run_tests():
    print("=" * 60)
    print(f"Testing Connection to Facebook Page ID: {TARGET_PAGE_ID}")
    print("=" * 60)

    # 1. Inspect 'me'
    print("\n1. Inspecting User Profile (/me)...")
    me_resp = requests.get(f"{GRAPH_BASE}/me", params={"access_token": NEW_USER_TOKEN}, timeout=10)
    if me_resp.status_code == 200:
        me_data = me_resp.json()
        print(f"✅ Token is VALID!")
        print(f"   Name: {me_data.get('name')}")
        print(f"   User ID: {me_data.get('id')}")
    else:
        print(f"❌ Token validation failed: {me_resp.status_code}")
        print(f"   Response: {me_resp.text}")
        return

    # 2. Inspect permissions granted
    print("\n2. Checking Granted Permissions (/me/permissions)...")
    perm_resp = requests.get(f"{GRAPH_BASE}/me/permissions", params={"access_token": NEW_USER_TOKEN}, timeout=10)
    if perm_resp.status_code == 200:
        perms = perm_resp.json().get("data", [])
        granted = [p.get("permission") for p in perms if p.get("status") == "granted"]
        print(f"   Granted ({len(granted)}): {', '.join(granted)}")
    else:
        print(f"   Could not fetch permissions: {perm_resp.status_code} - {perm_resp.text}")

    # 3. Query /me/accounts
    print("\n3. Querying Managed Pages (/me/accounts)...")
    accounts_resp = requests.get(
        f"{GRAPH_BASE}/me/accounts",
        params={
            "access_token": NEW_USER_TOKEN,
            "fields": "id,name,category,access_token,tasks,instagram_business_account{id,username}"
        },
        timeout=10
    )
    
    target_page_found = None
    target_page_token = None

    if accounts_resp.status_code == 200:
        accounts = accounts_resp.json().get("data", [])
        print(f"   Found {len(accounts)} page(s) on this account:")
        for idx, page in enumerate(accounts, 1):
            p_id = page.get("id")
            p_name = page.get("name")
            p_cat = page.get("category")
            p_tasks = page.get("tasks", [])
            ig = page.get("instagram_business_account", {})
            print(f"   [{idx}] Name: '{p_name}' | ID: {p_id} | Category: {p_cat}")
            print(f"       Tasks: {p_tasks}")
            if ig:
                print(f"       Linked Instagram: @{ig.get('username')} (ID: {ig.get('id')})")
            else:
                print(f"       Linked Instagram: None")
            
            if str(p_id) == str(TARGET_PAGE_ID):
                target_page_found = page
                target_page_token = page.get("access_token")
    else:
        print(f"❌ /me/accounts query failed: {accounts_resp.status_code} - {accounts_resp.text}")

    # 4. Direct Query on TARGET_PAGE_ID
    print(f"\n4. Querying Target Page Directly (/{TARGET_PAGE_ID})...")
    direct_fields = "id,name,category,link,is_published,verification_status,instagram_business_account{id,username}"
    
    # Try with User Token
    direct_resp = requests.get(
        f"{GRAPH_BASE}/{TARGET_PAGE_ID}",
        params={"access_token": NEW_USER_TOKEN, "fields": direct_fields},
        timeout=10
    )
    print("   [Query with User Token]:")
    if direct_resp.status_code == 200:
        print("   ✅ SUCCESS! Direct query succeeded.")
        print(f"   Page Data: {json.dumps(direct_resp.json(), indent=6)}")
    else:
        print(f"   ⚠️ Status {direct_resp.status_code}: {direct_resp.text}")

    # Try with Page Token if available
    if target_page_token:
        print("\n   [Query with Page Access Token]:")
        page_resp = requests.get(
            f"{GRAPH_BASE}/{TARGET_PAGE_ID}",
            params={"access_token": target_page_token, "fields": direct_fields},
            timeout=10
        )
        if page_resp.status_code == 200:
            print("   ✅ SUCCESS! Page Access Token query succeeded.")
            print(f"   Page Data: {json.dumps(page_resp.json(), indent=6)}")
        else:
            print(f"   ⚠️ Status {page_resp.status_code}: {page_resp.text}")

    # 5. Conclusion Summary
    print("\n" + "=" * 60)
    print("SUMMARY RESULT:")
    print("=" * 60)
    if target_page_found or direct_resp.status_code == 200:
        print(f"🎉 YES, WE CAN CONNECT TO PAGE ID {TARGET_PAGE_ID}!")
        if target_page_found:
            print(f"   - Page Name: {target_page_found.get('name')}")
            print(f"   - Managed directly by current user: YES")
            print(f"   - Page Access Token available: {'YES' if target_page_token else 'NO'}")
    else:
        print(f"❌ Could NOT connect to Page ID {TARGET_PAGE_ID}.")
        print("   Check if the ID is correct or if the user has role/admin permissions on the page.")

if __name__ == "__main__":
    run_tests()
