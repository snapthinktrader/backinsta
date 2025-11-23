"""
Post a specific reel to Instagram only
"""

import os
import sys
import time
import tempfile
import logging
import requests
import base64
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.mongodb_setup import get_connection

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ACCESS_TOKEN = os.getenv('REACT_APP_ACCESS_TOKEN')
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv('REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID')

def post_to_instagram(video_data, caption, headline):
    """Post video to Instagram as Reel"""
    try:
        logger.info("📤 Posting to Instagram via tmpfiles.org...")
        
        video_size = len(video_data)
        logger.info(f"📁 Video size: {video_size / (1024*1024):.2f} MB")
        
        # Upload to tmpfiles.org
        logger.info("📤 Uploading video to tmpfiles.org...")
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_video.write(video_data)
        temp_video.close()
        
        try:
            with open(temp_video.name, 'rb') as f:
                files = {'file': ('reel.mp4', f, 'video/mp4')}
                upload_response = requests.post(
                    'https://tmpfiles.org/api/v1/upload',
                    files=files,
                    timeout=120
                )
            
            if upload_response.status_code != 200:
                logger.error(f"❌ tmpfiles upload failed: {upload_response.text}")
                os.unlink(temp_video.name)
                return {"success": False, "error": f"tmpfiles upload failed"}
            
            result = upload_response.json()
            if result.get('status') != 'success':
                logger.error(f"❌ tmpfiles upload error: {result}")
                os.unlink(temp_video.name)
                return {"success": False, "error": f"tmpfiles error"}
            
            tmpfiles_url = result['data']['url']
            video_url = tmpfiles_url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
            logger.info(f"✅ Video uploaded: {video_url}")
            
        finally:
            if os.path.exists(temp_video.name):
                os.unlink(temp_video.name)
        
        # Create Instagram media container
        create_url = f"https://graph.facebook.com/v21.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
        create_payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": True,
            "access_token": ACCESS_TOKEN
        }
        
        logger.info("📹 Creating Instagram media container...")
        create_response = requests.post(create_url, data=create_payload, timeout=60)
        
        if create_response.status_code != 200:
            logger.error(f"❌ Failed to create media container: {create_response.text}")
            return {"success": False, "error": "Container creation failed"}
        
        media_id = create_response.json().get("id")
        logger.info(f"✅ Media container created: {media_id}")
        
        # Wait for processing
        logger.info("⏳ Waiting for Instagram to process video (30s)...")
        time.sleep(30)
        
        # Publish
        publish_url = f"https://graph.facebook.com/v21.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish"
        publish_payload = {
            "creation_id": media_id,
            "access_token": ACCESS_TOKEN
        }
        
        logger.info("📱 Publishing to Instagram...")
        publish_response = requests.post(publish_url, data=publish_payload, timeout=60)
        
        if publish_response.status_code != 200:
            error_data = publish_response.json()
            logger.error(f"❌ Failed to publish: {error_data}")
            return {"success": False, "error": str(error_data)}
        
        post_id = publish_response.json().get("id")
        logger.info(f"✅ Posted to Instagram: {post_id}")
        
        return {"success": True, "post_id": post_id}
        
    except Exception as e:
        logger.error(f"❌ Instagram posting error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# Get the reel
conn = get_connection()
cur = conn.cursor()
cur.execute("""
    SELECT id, headline, caption, video_data 
    FROM reels 
    WHERE id = 'f11cec2c-718d-468b-96b8-c02972936745'
""")

reel = cur.fetchone()
if not reel:
    print("❌ Reel not found")
    sys.exit(1)

reel_id, headline, caption, video_data = reel

print(f"\n📱 Posting to Instagram:")
print(f"   Headline: {headline[:50]}...")
print(f"   Size: {len(video_data) / (1024*1024):.2f} MB")

result = post_to_instagram(video_data, caption, headline)

if result["success"]:
    print(f"\n✅ SUCCESS! Instagram Post ID: {result['post_id']}")
    
    # Update database
    cur.execute("""
        UPDATE reels 
        SET instagram_post_id = %s 
        WHERE id = %s
    """, (result['post_id'], reel_id))
    conn.commit()
    print("✅ Database updated")
else:
    print(f"\n❌ FAILED: {result['error']}")

cur.close()
conn.close()
