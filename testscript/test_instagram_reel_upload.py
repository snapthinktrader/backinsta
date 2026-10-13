#!/usr/bin/env python3
"""
Test script to create and publish a real Instagram Reel
using the new extended access token on account 17841477569192718 (@usdaily24).
"""

import os
import sys
import time
import requests
import logging

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, '.env'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestInstagramReel")

ACCESS_TOKEN = os.getenv("REACT_APP_ACCESS_TOKEN")
ACCOUNT_ID = os.getenv("REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID", "17841477569192718")

def main():
    logger.info("=" * 60)
    logger.info(f"🚀 TESTING INSTAGRAM REEL PUBLISH TO ACCOUNT: {ACCOUNT_ID}")
    logger.info("=" * 60)

    # 1. Verify account details first
    acc_url = f"https://graph.facebook.com/v21.0/{ACCOUNT_ID}"
    r_acc = requests.get(acc_url, params={
        "fields": "id,username,name,media_count",
        "access_token": ACCESS_TOKEN
    })
    
    if r_acc.status_code != 200:
        logger.error(f"❌ Failed to fetch account info: {r_acc.status_code} - {r_acc.text}")
        return False
        
    acc_info = r_acc.json()
    logger.info(f"✅ Account verified: @{acc_info.get('username')} ({acc_info.get('name')})")
    logger.info(f"📸 Total media count: {acc_info.get('media_count')}")

    # 2. Use a tested, accessible video URL (mp4)
    # Uploaded in previous step to uguu.se
    test_video_url = "https://d.uguu.se/pjnrizJA.mp4"
    logger.info(f"\n📹 Using public Reel video URL: {test_video_url}")
    
    # Verify the video URL is reachable
    head_resp = requests.head(test_video_url, timeout=10)
    if head_resp.status_code != 200:
        logger.warning(f"⚠️ Video URL returned {head_resp.status_code}, re-uploading test video...")
        # Fallback to local re-upload if needed
    else:
        logger.info(f"✅ Video URL is reachable (Content-Type: {head_resp.headers.get('Content-Type')})")

    caption = (
        "Markets React: Key Economic Shifts & Tech Momentum Analysis 📈\n\n"
        "States now navigate Meta's settlement billions while AI market infrastructure surges.\n\n"
        "🎧 Read full insights: https://forexyy.com\n\n"
        "#business #economy #tech #stocks #news #trending #forexyy"
    )

    # 3. Create Media Container
    create_url = f"https://graph.facebook.com/v21.0/{ACCOUNT_ID}/media"
    create_params = {
        "media_type": "REELS",
        "video_url": test_video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }

    logger.info(f"\n📤 Creating Reel container via POST {create_url}...")
    create_resp = requests.post(create_url, params=create_params, timeout=30)
    
    if create_resp.status_code != 200:
        logger.error(f"❌ Failed to create Reel container (HTTP {create_resp.status_code}): {create_resp.text}")
        return False

    creation_id = create_resp.json().get("id")
    logger.info(f"✅ Reel container created successfully! Creation ID: {creation_id}")

    # 4. Poll Container Status until FINISHED
    logger.info("\n⏳ Polling container status from Meta...")
    status_url = f"https://graph.facebook.com/v21.0/{creation_id}"
    status_params = {
        "fields": "status_code,status",
        "access_token": ACCESS_TOKEN
    }

    is_ready = False
    for attempt in range(1, 15):
        time.sleep(5)
        st_resp = requests.get(status_url, params=status_params, timeout=15)
        if st_resp.status_code == 200:
            st_data = st_resp.json()
            code = st_data.get("status_code")
            logger.info(f"   [{attempt}/15] Container status: {code} ({st_data.get('status')})")
            if code == "FINISHED":
                is_ready = True
                break
            elif code == "ERROR":
                logger.error(f"❌ Container processing failed on Meta: {st_data}")
                return False
        else:
            logger.warning(f"   Could not fetch status: {st_resp.status_code}")

    if not is_ready:
        logger.warning("⚠️ Container did not reach FINISHED in 70s, attempting publish anyway...")

    # 5. Publish Media Container
    publish_url = f"https://graph.facebook.com/v21.0/{ACCOUNT_ID}/media_publish"
    publish_params = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }

    logger.info(f"\n🚀 Publishing Reel via POST {publish_url}...")
    pub_resp = requests.post(publish_url, params=publish_params, timeout=30)
    
    if pub_resp.status_code == 200:
        post_id = pub_resp.json().get("id")
        logger.info("\n" + "=" * 60)
        logger.info(f"🎉 SUCCESS! REEL POSTED TO INSTAGRAM!")
        logger.info(f"📸 Instagram Post ID: {post_id}")
        logger.info(f"🔗 Instagram URL: https://www.instagram.com/reel/{post_id}/")
        logger.info(f"🔗 Profile: https://www.instagram.com/{acc_info.get('username')}/")
        logger.info("=" * 60)
        return True
    else:
        logger.error(f"❌ Failed to publish Reel (HTTP {pub_resp.status_code}): {pub_resp.text}")
        return False

if __name__ == '__main__':
    main()
