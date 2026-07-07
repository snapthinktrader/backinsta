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

def upload_to_catbox(file_path):
    """Upload file to catbox.moe"""
    try:
        logger.info(f"📤 Uploading to Catbox: {file_path}...")
        with open(file_path, 'rb') as f:
            files = {'fileToUpload': ('video.mp4', f, 'video/mp4')}
            data = {'reqtype': 'fileupload'}
            response = requests.post(
                'https://catbox.moe/user/api.php',
                files=files,
                data=data,
                timeout=60
            )
            if response.status_code == 200:
                url = response.text.strip()
                if url.startswith('http'):
                    logger.info(f"✅ Catbox upload successful: {url}")
                    return url
                else:
                    logger.warning(f"⚠️ Catbox returned unexpected response: {url}")
            else:
                logger.warning(f"⚠️ Catbox upload failed (HTTP {response.status_code}): {response.text}")
    except Exception as e:
        logger.warning(f"⚠️ Catbox upload exception: {e}")
    return None

def upload_to_tmpfiles(file_path):
    """Upload file to tmpfiles.org"""
    try:
        logger.info(f"📤 Uploading to tmpfiles.org: {file_path}...")
        with open(file_path, 'rb') as f:
            files = {'file': ('reel.mp4', f, 'video/mp4')}
            response = requests.post(
                'https://tmpfiles.org/api/v1/upload',
                files=files,
                timeout=120
            )
            if response.status_code == 200:
                res_data = response.json()
                if res_data.get('status') == 'success':
                    url = res_data['data']['url']
                    direct_url = url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
                    logger.info(f"✅ tmpfiles.org upload successful: {direct_url}")
                    return direct_url
                else:
                    logger.warning(f"⚠️ tmpfiles.org returned status error: {res_data}")
            else:
                logger.warning(f"⚠️ tmpfiles.org upload failed (HTTP {response.status_code}): {response.text}")
    except Exception as e:
        logger.warning(f"⚠️ tmpfiles.org upload exception: {e}")
    return None

def upload_to_uguu(file_path):
    """Upload file to uguu.se"""
    try:
        logger.info(f"📤 Uploading to uguu.se: {file_path}...")
        with open(file_path, 'rb') as f:
            files = {'files[]': ('reel.mp4', f, 'video/mp4')}
            response = requests.post(
                'https://uguu.se/upload.php',
                files=files,
                timeout=120
            )
            if response.status_code == 200:
                try:
                    res_data = response.json()
                    if 'files' in res_data and len(res_data['files']) > 0:
                        url = res_data['files'][0]['url']
                        logger.info(f"✅ uguu.se upload successful: {url}")
                        return url
                except Exception:
                    url = response.text.strip()
                    if url.startswith('http'):
                        logger.info(f"✅ uguu.se upload successful (plain): {url}")
                        return url
                logger.warning(f"⚠️ uguu.se returned unexpected response format: {response.text}")
            else:
                logger.warning(f"⚠️ uguu.se upload failed (HTTP {response.status_code}): {response.text}")
    except Exception as e:
        logger.warning(f"⚠️ uguu.se upload exception: {e}")
    return None

def post_to_instagram(video_data, caption, headline):
    """Post video to Instagram as Reel"""
    try:
        logger.info("📤 Posting to Instagram with fallback hosting...")
        
        video_size = len(video_data)
        logger.info(f"📁 Video size: {video_size / (1024*1024):.2f} MB")
        
        # Create temp file for upload
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_video.write(video_data)
        temp_video.close()
        
        video_url = None
        
        # Try multiple hosting services with fallback
        hosting_services = [
            {
                'name': 'catbox.moe',
                'upload_fn': upload_to_catbox
            },
            {
                'name': 'tmpfiles.org',
                'upload_fn': upload_to_tmpfiles
            },
            {
                'name': 'uguu.se',
                'upload_fn': upload_to_uguu
            }
        ]
        
        try:
            for service in hosting_services:
                try:
                    logger.info(f"📤 Trying {service['name']}...")
                    video_url = service['upload_fn'](temp_video.name)
                    if video_url:
                        logger.info(f"✅ Video uploaded to {service['name']}: {video_url}")
                        break
                    else:
                        logger.warning(f"⚠️ {service['name']} upload returned None, trying next service...")
                except Exception as e:
                    logger.warning(f"⚠️ {service['name']} error: {e}, trying next service...")
                    continue
            
            if not video_url:
                logger.error("❌ All video hosting services failed")
                return {"success": False, "error": "All video hosting services failed"}
                
        finally:
            # Cleanup temp file
            if os.path.exists(temp_video.name):
                try:
                    os.unlink(temp_video.name)
                except Exception as cleanup_error:
                    logger.warning(f"⚠️ Error cleaning up temp video file: {cleanup_error}")
        
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
