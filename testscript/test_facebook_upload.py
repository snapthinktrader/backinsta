#!/usr/bin/env python3
"""
Test script for facebook_uploader.py module
Verifies connectivity and executes a test post to forexyy.com
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from facebook_uploader import FacebookPageUploader

def test_facebook_uploader():
    print("=" * 60)
    print("Testing FacebookPageUploader Module")
    print("=" * 60)

    uploader = FacebookPageUploader()
    print(f"Page ID: {uploader.page_id}")
    print(f"Configured: {uploader.is_configured()}")

    # 1. Verify Connection
    print("\n1. Verifying Connection...")
    res = uploader.verify_connection()
    if res.get("success"):
        page_info = res.get("page", {})
        print(f"✅ Connection OK! Page Name: {page_info.get('name')}")
        print(f"   Category: {page_info.get('category')}")
        print(f"   Link: {page_info.get('link')}")
    else:
        print(f"❌ Connection failed: {res.get('error')}")
        sys.exit(1)

    # 2. Test publishing feed update
    print("\n2. Testing post creation...")
    sample_article = {
        "title": "Forexyy Market Watch - Tech & Economy",
        "abstract": "Automated update test from BackInsta.",
        "url": "https://forexyy.com"
    }
    sample_ai = {
        "headline": "Forexyy Market Watch",
        "caption": "Stay ahead of global market trends with daily curated insights.",
        "hashtags": ["Forexyy", "Finance", "Markets"]
    }

    # Publish a live test post
    post_res = uploader.upload_feed_post(
        message=f"{sample_ai['headline']}\n\n{sample_ai['caption']}\n\n#Forexyy #Markets",
        link=sample_article["url"]
    )
    
    if post_res.get("success"):
        post_id = post_res.get("post_id")
        print(f"✅ Post published successfully!")
        print(f"   Post ID: {post_id}")
        print(f"   Facebook URL: {post_res.get('facebook_url')}")
    else:
        print(f"⚠️ Post creation returned: {post_res.get('error')}")

    print("\n" + "=" * 60)
    print("Facebook Page Uploader Test Finished!")
    print("=" * 60)

if __name__ == "__main__":
    test_facebook_uploader()
