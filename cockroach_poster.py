"""
CockroachDB Poster - Simplified posting from database
Fetches pre-generated reels from CockroachDB and posts to Instagram/YouTube
"""

import os
import sys
import time
import tempfile
import logging
import requests
import base64
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.cockroach_setup import get_pending_reel, mark_reel_posted, mark_reel_failed, get_stats

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Instagram Configuration
ACCESS_TOKEN = os.getenv('REACT_APP_ACCESS_TOKEN')
INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv('REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID')

class CockroachDBPoster:
    """Post pre-generated reels from CockroachDB to Instagram and YouTube"""
    
    def __init__(self):
        # Initialize YouTube uploader
        try:
            from youtube_shorts import YouTubeShortsUploader
            self.youtube_uploader = YouTubeShortsUploader()
            logger.info("✅ YouTube uploader initialized")
        except Exception as e:
            logger.warning(f"⚠️  YouTube uploader not available: {e}")
            self.youtube_uploader = None
    
    def post_to_instagram(self, video_data, caption, headline):
        """
        Post video to Instagram from binary data using tmpfiles.org hosting
        
        Args:
            video_data: Video file as bytes
            caption: Post caption
            headline: Video headline (for logging)
            
        Returns:
            dict: Result with success status and post_id or error
        """
        try:
            logger.info("📤 Posting to Instagram via tmpfiles.org...")
            
            video_size = len(video_data)
            logger.info(f"📁 Video size: {video_size / (1024*1024):.2f} MB")
            
            # Step 1: Upload video to tmpfiles.org
            logger.info("📤 Uploading video to tmpfiles.org...")
            
            # Create temp file for upload
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
                    return {"success": False, "error": f"tmpfiles upload failed: {upload_response.text}"}
                
                result = upload_response.json()
                if result.get('status') != 'success':
                    logger.error(f"❌ tmpfiles upload error: {result}")
                    os.unlink(temp_video.name)
                    return {"success": False, "error": f"tmpfiles error: {result}"}
                
                # tmpfiles.org returns URL like "https://tmpfiles.org/123456"
                # We need to convert to direct download URL: "https://tmpfiles.org/dl/123456"
                tmpfiles_url = result['data']['url']
                video_url = tmpfiles_url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
                logger.info(f"✅ Video uploaded to tmpfiles: {video_url}")
                
            finally:
                # Cleanup temp file
                if os.path.exists(temp_video.name):
                    os.unlink(temp_video.name)
            
            # Step 2: Create Instagram media container
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
                return {"success": False, "error": f"Container creation failed: {create_response.text}"}
            
            media_id = create_response.json().get("id")
            logger.info(f"✅ Media container created: {media_id}")
            
            # Step 3: Check if media is ready (smart polling instead of fixed wait)
            logger.info("⏳ Checking if media is ready for publishing...")
            max_attempts = 24  # 24 attempts * 5 seconds = 2 minutes max
            for attempt in range(1, max_attempts + 1):
                # Check media status
                status_url = f"https://graph.facebook.com/v21.0/{media_id}"
                status_params = {
                    "fields": "status_code,status",
                    "access_token": ACCESS_TOKEN
                }
                
                status_response = requests.get(status_url, params=status_params, timeout=30)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status_code = status_data.get("status_code")
                    
                    # Status codes:
                    # FINISHED = ready to publish
                    # IN_PROGRESS = still processing
                    # ERROR = processing failed
                    if status_code == "FINISHED":
                        logger.info(f"✅ Media ready after {attempt * 5}s")
                        break
                    elif status_code == "ERROR":
                        logger.error(f"❌ Media processing failed: {status_data}")
                        return {"success": False, "error": f"Media processing error: {status_data}"}
                    else:
                        logger.info(f"⏳ Attempt {attempt}/{max_attempts}: Status = {status_code}, waiting 5s...")
                        time.sleep(5)
                else:
                    # If we can't check status, fall back to waiting
                    logger.warning(f"⚠️ Can't check status (attempt {attempt}), waiting 5s...")
                    time.sleep(5)
            else:
                # Max attempts reached
                logger.warning(f"⚠️ Media not ready after {max_attempts * 5}s, attempting to publish anyway...")
            
            # Step 4: Publish the media
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
                
                # Check if rate limited
                error_code = error_data.get('error', {}).get('code')
                if error_code == 4:
                    logger.warning("⚠️  Instagram rate limited")
                    return {"success": False, "error": "Rate limited", "rate_limited": True}
                
                return {"success": False, "error": publish_response.text}
            
            post_id = publish_response.json().get("id")
            logger.info(f"✅ Posted to Instagram: {post_id}")
            
            return {"success": True, "post_id": post_id}
            
        except Exception as e:
            logger.error(f"❌ Instagram posting error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def post_to_youtube(self, video_data, headline, caption):
        """
        Post video to YouTube Shorts from binary data
        
        Args:
            video_data: Video file as bytes
            headline: Video title
            caption: Video description
            
        Returns:
            dict: Result with success status and video_id or error
        """
        try:
            if not self.youtube_uploader:
                logger.warning("⚠️  YouTube uploader not available")
                return {"success": False, "error": "YouTube uploader not initialized"}
            
            logger.info("📤 Posting to YouTube Shorts...")
            
            # Save video to temp file
            temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_video.write(video_data)
            temp_video.close()
            
            logger.info(f"📁 Video saved to temp file: {temp_video.name}")
            
            # Upload to YouTube
            result = self.youtube_uploader.upload_short(
                video_path=temp_video.name,
                title=headline[:100],  # YouTube title limit
                description=caption[:5000]  # YouTube description limit
            )
            
            # Cleanup
            os.unlink(temp_video.name)
            
            if result.get("success"):
                video_id = result.get("video_id")
                logger.info(f"✅ Posted to YouTube: {video_id}")
                return {"success": True, "video_id": video_id}
            else:
                logger.error(f"❌ YouTube upload failed: {result.get('error')}")
                return {"success": False, "error": result.get("error")}
            
        except Exception as e:
            logger.error(f"❌ YouTube posting error: {e}")
            return {"success": False, "error": str(e)}
    
    def post_next_reel(self):
        """
        Fetch the next pending reel and post to Instagram/YouTube
        
        Returns:
            bool: True if posted successfully, False otherwise
        """
        try:
            # Get pending reel
            logger.info("🔍 Fetching pending reel from database...")
            reel = get_pending_reel()
            
            if not reel:
                logger.warning("⚠️  No pending reels in database")
                return False
            
            reel_id = reel['id']
            headline = reel['headline']
            caption = reel['caption']
            video_data = reel['video_data']
            
            logger.info(f"✅ Found reel: {headline[:50]}...")
            logger.info(f"   ID: {reel_id}")
            logger.info(f"   Size: {len(video_data) / (1024*1024):.2f} MB")
            logger.info(f"   Duration: {reel.get('duration', 'unknown')}s")
            
            # Post to Instagram
            instagram_result = self.post_to_instagram(video_data, caption, headline)
            instagram_success = instagram_result.get("success", False)
            instagram_post_id = instagram_result.get("post_id")
            
            # Post to YouTube
            youtube_result = self.post_to_youtube(video_data, headline, caption)
            youtube_success = youtube_result.get("success", False)
            youtube_video_id = youtube_result.get("video_id")
            
            # Check if at least one succeeded
            if instagram_success or youtube_success:
                logger.info("✅ Posted successfully to at least one platform")
                
                # Mark as posted
                mark_reel_posted(
                    reel_id=reel_id,
                    instagram_post_id=instagram_post_id if instagram_success else None,
                    youtube_video_id=youtube_video_id if youtube_success else None
                )
                
                # Log results
                if instagram_success:
                    logger.info(f"   ✅ Instagram: {instagram_post_id}")
                else:
                    logger.warning(f"   ⚠️  Instagram: {instagram_result.get('error', 'Failed')}")
                
                if youtube_success:
                    logger.info(f"   ✅ YouTube: {youtube_video_id}")
                else:
                    logger.warning(f"   ⚠️  YouTube: {youtube_result.get('error', 'Failed')}")
                
                return True
            else:
                # Both failed
                logger.error("❌ Both platforms failed")
                error_msg = f"Instagram: {instagram_result.get('error', 'Unknown')}, YouTube: {youtube_result.get('error', 'Unknown')}"
                mark_reel_failed(reel_id, error_msg)
                return False
            
        except Exception as e:
            logger.error(f"❌ Error posting reel: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main entry point for testing"""
    print("\n" + "="*60)
    print("📤 COCKROACHDB POSTER - TEST MODE")
    print("="*60)
    
    # Show stats
    try:
        stats = get_stats()
        print(f"\n📊 Database Stats:")
        print(f"   Total reels: {stats['total']}")
        print(f"   Pending: {stats['pending']}")
        print(f"   Posted: {stats['posted']}")
        print(f"   Failed: {stats['failed']}")
    except Exception as e:
        print(f"⚠️  Could not get stats: {e}")
    
    # Confirm
    response = input("\n📤 Post next pending reel? (y/n): ")
    if response.lower() != 'y':
        print("❌ Cancelled")
        return
    
    # Post
    poster = CockroachDBPoster()
    success = poster.post_next_reel()
    
    if success:
        print("\n✅ SUCCESS! Reel posted")
    else:
        print("\n❌ FAILED to post reel")
    
    # Show updated stats
    try:
        stats = get_stats()
        print(f"\n📊 Updated Stats:")
        print(f"   Pending: {stats['pending']}")
        print(f"   Posted: {stats['posted']}")
        print(f"   Failed: {stats['failed']}")
    except:
        pass

if __name__ == "__main__":
    main()
