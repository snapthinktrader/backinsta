"""
Fixed Instagram poster using imgbb for video hosting
"""

import os
import base64
import requests
import tempfile

# Instagram Configuration
ACCESS_TOKEN = os.getenv('REACT_APP_ACCESS_TOKEN')
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv('REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID')
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY', 'c21e386db487b2ddcf50386f3c05503a')

def post_to_instagram_fixed(video_data, caption):
    """
    Post video to Instagram using imgbb as video host
    
    Returns:
        dict: {success: bool, post_id: str or error: str}
    """
    try:
        print("📤 Uploading video to imgbb...")
        
        # Save to temp file
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_video.write(video_data)
        temp_video.close()
        
        # Upload to imgbb
        with open(temp_video.name, 'rb') as f:
            video_b64 = base64.b64encode(f.read()).decode('utf-8')
        
        response = requests.post(
            'https://api.imgbb.com/1/upload',
            data={
                'key': IMGBB_API_KEY,
                'image': video_b64
            },
            timeout=120
        )
        
        if response.status_code != 200:
            os.unlink(temp_video.name)
            return {"success": False, "error": f"imgbb upload failed: {response.status_code}"}
        
        data = response.json()
        if not data.get('success'):
            os.unlink(temp_video.name)
            return {"success": False, "error": "imgbb upload failed"}
        
        video_url = data['data']['url']
        print(f"✅ Video uploaded: {video_url}")
        
        # Create Instagram media container
        print("📹 Creating Instagram Reel...")
        create_url = f"https://graph.facebook.com/v21.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
        create_payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": ACCESS_TOKEN
        }
        
        create_response = requests.post(create_url, data=create_payload, timeout=60)
        
        if create_response.status_code != 200:
            os.unlink(temp_video.name)
            return {"success": False, "error": f"Media creation failed: {create_response.text}"}
        
        media_id = create_response.json().get("id")
        print(f"✅ Media container: {media_id}")
        
        # Wait for processing
        print("⏳ Processing (20s)...")
        import time
        time.sleep(20)
        
        # Publish
        print("📱 Publishing...")
        publish_url = f"https://graph.facebook.com/v21.0/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish"
        publish_payload = {
            "creation_id": media_id,
            "access_token": ACCESS_TOKEN
        }
        
        publish_response = requests.post(publish_url, data=publish_payload, timeout=60)
        
        os.unlink(temp_video.name)
        
        if publish_response.status_code != 200:
            error_data = publish_response.json()
            if error_data.get('error', {}).get('code') == 4:
                return {"success": False, "error": "Rate limited", "rate_limited": True}
            return {"success": False, "error": publish_response.text}
        
        post_id = publish_response.json().get("id")
        print(f"✅ Posted: {post_id}")
        
        return {"success": True, "post_id": post_id}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}
