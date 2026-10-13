#!/usr/bin/env python3
"""
Facebook Page API integration for BackInsta
Publishes Reels / Videos and Article Posts to Facebook Page (forexyy.com)
"""

import os
import logging
import requests
from typing import Optional, Dict
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GRAPH_API_VERSION = "v21.0"
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

class FacebookPageUploader:
    """Uploads videos, reels, and photos to a Facebook Page via Meta Graph API"""

    def __init__(self, page_id: Optional[str] = None, access_token: Optional[str] = None):
        self.page_id = page_id or os.getenv("FB_PAGE_ID", "1394981273691815")
        self.access_token = access_token or os.getenv("FB_PAGE_ACCESS_TOKEN") or os.getenv("REACT_APP_ACCESS_TOKEN")
        self.enabled = os.getenv("USE_FACEBOOK_PAGE", "true").lower() in ("true", "1", "yes")

        if not self.access_token:
            logger.warning("⚠️ No FB_PAGE_ACCESS_TOKEN found. Facebook Page posting disabled.")
        elif not self.page_id:
            logger.warning("⚠️ No FB_PAGE_ID configured. Facebook Page posting disabled.")
        else:
            logger.info(f"✅ FacebookPageUploader initialized for Page ID: {self.page_id}")

    def is_configured(self) -> bool:
        """Check if the uploader is enabled and configured with token and page ID"""
        return bool(self.enabled and self.page_id and self.access_token)

    def verify_connection(self) -> Dict:
        """Verify token validity and page connectivity"""
        if not self.is_configured():
            return {"success": False, "error": "Facebook Page uploader is not configured"}

        try:
            url = f"{GRAPH_BASE}/{self.page_id}"
            params = {
                "fields": "id,name,link,category,is_published",
                "access_token": self.access_token
            }
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"✅ Facebook Page connected: {data.get('name')} (ID: {data.get('id')})")
                return {"success": True, "page": data}
            else:
                err = resp.json().get("error", {}).get("message", resp.text)
                logger.error(f"❌ Facebook Page verification failed: {err}")
                return {"success": False, "error": err}
        except Exception as e:
            logger.error(f"❌ Facebook Page verification exception: {e}")
            return {"success": False, "error": str(e)}

    def upload_video_from_article(self, video_path: str, article: Dict, ai_analysis: Optional[Dict] = None) -> Dict:
        """
        Upload a video Reel to the Facebook Page

        Args:
            video_path: Local file path of the video file (.mp4)
            article: Dictionary containing article metadata (title, abstract, url)
            ai_analysis: Optional dictionary containing AI-generated caption and hashtags

        Returns:
            Dict: {'success': bool, 'post_id': str, 'video_id': str, 'facebook_url': str}
        """
        if not self.is_configured():
            return {"success": False, "error": "Facebook Page uploader not configured or disabled"}

        if not os.path.exists(video_path):
            return {"success": False, "error": f"Video file not found at: {video_path}"}

        try:
            headline = article.get("title") or (ai_analysis.get("headline") if ai_analysis else "") or "Forexyy News Update"
            caption = ""
            if ai_analysis and ai_analysis.get("caption"):
                caption = ai_analysis.get("caption")
            else:
                abstract = article.get("abstract", "")
                caption = f"{headline}\n\n{abstract}\n\nStay updated with Forexyy!"

            hashtags = "#Forexyy #News #Finance #Markets #WorldNews"
            if ai_analysis and ai_analysis.get("hashtags"):
                tags = ai_analysis.get("hashtags")
                if isinstance(tags, list):
                    hashtags = " ".join(f"#{t.lstrip('#')}" for t in tags)
                elif isinstance(tags, str):
                    hashtags = tags

            full_description = f"{caption}\n\n{hashtags}\n\nSource: {article.get('url', '')}".strip()

            logger.info(f"📤 Uploading video to Facebook Page {self.page_id}...")
            url = f"{GRAPH_BASE}/{self.page_id}/videos"
            
            data = {
                "title": headline[:250],
                "description": full_description,
                "published": "true",
                "access_token": self.access_token
            }

            file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
            logger.info(f"📦 Video file size: {file_size_mb:.2f} MB")

            with open(video_path, "rb") as video_file:
                files = {
                    "source": ("reel.mp4", video_file, "video/mp4")
                }
                resp = requests.post(url, data=data, files=files, timeout=120)

            if resp.status_code == 200:
                resp_json = resp.json()
                video_id = resp_json.get("id")
                fb_url = f"https://www.facebook.com/{self.page_id}/videos/{video_id}"
                logger.info(f"✅ Facebook Video/Reel uploaded successfully!")
                logger.info(f"📹 Facebook Video ID: {video_id}")
                logger.info(f"🔗 Facebook URL: {fb_url}")
                return {
                    "success": True,
                    "video_id": video_id,
                    "post_id": video_id,
                    "facebook_url": fb_url
                }
            else:
                err_data = resp.json()
                err_msg = err_data.get("error", {}).get("message", resp.text)
                logger.error(f"❌ Facebook video upload failed (HTTP {resp.status_code}): {err_msg}")
                return {"success": False, "error": err_msg}

        except Exception as e:
            logger.error(f"❌ Exception uploading video to Facebook: {e}")
            return {"success": False, "error": str(e)}

    def upload_photo_from_article(self, image_url_or_path: str, caption: str) -> Dict:
        """
        Upload a photo post to the Facebook Page

        Args:
            image_url_or_path: URL or local path to the image
            caption: Post caption / text
        """
        if not self.is_configured():
            return {"success": False, "error": "Facebook Page uploader not configured or disabled"}

        try:
            url = f"{GRAPH_BASE}/{self.page_id}/photos"
            data = {
                "caption": caption,
                "published": "true",
                "access_token": self.access_token
            }

            if os.path.exists(image_url_or_path):
                with open(image_url_or_path, "rb") as f:
                    files = {"source": ("image.jpg", f, "image/jpeg")}
                    resp = requests.post(url, data=data, files=files, timeout=60)
            else:
                data["url"] = image_url_or_path
                resp = requests.post(url, data=data, timeout=60)

            if resp.status_code == 200:
                resp_json = resp.json()
                post_id = resp_json.get("post_id") or resp_json.get("id")
                fb_url = f"https://www.facebook.com/{post_id}"
                logger.info(f"✅ Facebook Photo post created! ID: {post_id}")
                return {
                    "success": True,
                    "post_id": post_id,
                    "facebook_url": fb_url
                }
            else:
                err = resp.json().get("error", {}).get("message", resp.text)
                logger.error(f"❌ Facebook photo upload failed: {err}")
                return {"success": False, "error": err}

        except Exception as e:
            logger.error(f"❌ Exception uploading photo to Facebook: {e}")
            return {"success": False, "error": str(e)}

    def upload_feed_post(self, message: str, link: Optional[str] = None) -> Dict:
        """
        Publish a feed message or link post to the Facebook Page
        """
        if not self.is_configured():
            return {"success": False, "error": "Facebook Page uploader not configured or disabled"}

        try:
            url = f"{GRAPH_BASE}/{self.page_id}/feed"
            data = {
                "message": message,
                "access_token": self.access_token
            }
            if link:
                data["link"] = link

            resp = requests.post(url, data=data, timeout=30)
            if resp.status_code == 200:
                resp_json = resp.json()
                post_id = resp_json.get("id")
                fb_url = f"https://www.facebook.com/{post_id}"
                logger.info(f"✅ Facebook feed post published! ID: {post_id}")
                return {
                    "success": True,
                    "post_id": post_id,
                    "facebook_url": fb_url
                }
            else:
                err = resp.json().get("error", {}).get("message", resp.text)
                logger.error(f"❌ Facebook feed post failed: {err}")
                return {"success": False, "error": err}

        except Exception as e:
            logger.error(f"❌ Exception publishing feed post to Facebook: {e}")
            return {"success": False, "error": str(e)}
