#!/usr/bin/env python3
"""
YouTube Shorts API integration
Posts video Reels as YouTube Shorts
"""

import os
import pickle
import logging
import base64
import json
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    logger.warning("⚠️ Google API libraries not installed. YouTube Shorts disabled.")

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

class YouTubeShortsUploader:
    """Upload videos to YouTube Shorts"""
    
    def __init__(self, credentials_file: str = 'youtube_credentials.json'):
        """
        Initialize YouTube API client
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
        """
        self.credentials_file = credentials_file
        self.token_file = 'youtube_token.pickle'
        self.youtube = None
        
        if YOUTUBE_AVAILABLE:
            self._authenticate()
    
    def _authenticate(self):
        """Authenticate with YouTube API"""
        creds = None
        
        # Check for base64-encoded credentials from environment (for Render deployment)
        credentials_base64 = os.getenv('YOUTUBE_CREDENTIALS_BASE64')
        token_base64 = os.getenv('YOUTUBE_TOKEN_BASE64')
        
        # Decode and save credentials if provided via environment
        if credentials_base64 and not os.path.exists(self.credentials_file):
            try:
                logger.info("📦 Decoding YouTube credentials from environment variable...")
                credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
                with open(self.credentials_file, 'w') as f:
                    f.write(credentials_json)
                logger.info("✅ YouTube credentials file created from environment")
            except Exception as e:
                logger.error(f"❌ Failed to decode YouTube credentials: {e}")
        
        # Decode and save token if provided via environment
        if token_base64 and not os.path.exists(self.token_file):
            try:
                logger.info("📦 Decoding YouTube token from environment variable...")
                token_data = base64.b64decode(token_base64)
                with open(self.token_file, 'wb') as f:
                    f.write(token_data)
                logger.info("✅ YouTube token file created from environment")
            except Exception as e:
                logger.error(f"❌ Failed to decode YouTube token: {e}")
        
        # Load token if exists
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as pe:
                logger.warning(f"⚠️ Failed to unpickle {self.token_file}: {pe}. Removing corrupt token file.")
                try:
                    os.remove(self.token_file)
                except Exception:
                    pass
                creds = None
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("🔄 Refreshing YouTube API token...")
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    logger.error(f"❌ YouTube credentials file not found: {self.credentials_file}")
                    logger.info("💡 To enable YouTube Shorts:")
                    logger.info("   1. Go to https://console.cloud.google.com/")
                    logger.info("   2. Create a project and enable YouTube Data API v3")
                    logger.info("   3. Create OAuth 2.0 credentials (Desktop app)")
                    logger.info("   4. Download as 'youtube_credentials.json'")
                    return
                
                logger.info("🔐 Authenticating with YouTube API...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token for future use
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build YouTube API client
        self.youtube = build('youtube', 'v3', credentials=creds)
        logger.info("✅ YouTube API authenticated")
    
    def upload_short(self, video_path: str, title: str, description: str = "", 
                     tags: list = None, category_id: str = "25",
                     thumbnail_path: str = None) -> Optional[Dict]:
        """
        Upload video as YouTube Short
        
        Args:
            video_path: Path to video file
            title: Video title (max 100 chars)
            description: Video description (include #Shorts)
            tags: List of tags
            category_id: YouTube category (25 = News & Politics)
            thumbnail_path: Optional path to custom cover image / thumbnail
            
        Returns:
            Upload result dict or None if failed
        """
        if not self.youtube:
            logger.error("❌ YouTube API not authenticated")
            return None
        
        if not os.path.exists(video_path):
            logger.error(f"❌ Video file not found: {video_path}")
            return None
        
        try:
            # Prepare video metadata
            # Add #Shorts to description for YouTube to recognize it as a Short
            if "#Shorts" not in description and "#shorts" not in description:
                description += "\n\n#Shorts"
            
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube title limit
                    'description': description,
                    'tags': tags or ['news', 'shorts', 'breaking news'],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': 'public',  # or 'unlisted' for testing
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create media upload
            media = MediaFileUpload(
                video_path,
                chunksize=-1,  # Upload in a single request
                resumable=True,
                mimetype='video/mp4'
            )
            
            logger.info(f"📤 Uploading to YouTube Shorts: {title[:50]}...")
            
            # Execute upload
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"⏳ Upload progress: {progress}%")
            
            video_id = response['id']
            video_url = f"https://youtube.com/shorts/{video_id}"
            
            logger.info(f"✅ YouTube Short uploaded successfully!")
            logger.info(f"🎬 Video ID: {video_id}")
            logger.info(f"🔗 URL: {video_url}")

            # Upload custom thumbnail if provided
            if thumbnail_path and os.path.exists(thumbnail_path):
                try:
                    actual_thumb = thumbnail_path
                    # YouTube API has a strict 2MB limit on thumbnail uploads
                    if os.path.getsize(actual_thumb) > 2 * 1024 * 1024:
                        jpg_alt = os.path.splitext(actual_thumb)[0] + "_yt.jpg"
                        if not os.path.exists(jpg_alt):
                            from PIL import Image
                            im = Image.open(actual_thumb).convert("RGB")
                            im.save(jpg_alt, format="JPEG", quality=95)
                        actual_thumb = jpg_alt

                    mime = "image/jpeg" if actual_thumb.lower().endswith((".jpg", ".jpeg")) else "image/png"
                    logger.info(f"🖼️ Setting custom thumbnail on YouTube Short ({actual_thumb}, {os.path.getsize(actual_thumb)/1024/1024:.2f} MB)...")
                    thumb_media = MediaFileUpload(actual_thumb, mimetype=mime)
                    self.youtube.thumbnails().set(videoId=video_id, media_body=thumb_media).execute()
                    logger.info("✅ Custom YouTube thumbnail attached successfully!")
                except Exception as te:
                    logger.warning(f"⚠️ Could not attach YouTube thumbnail: {te}")
            
            return {
                'success': True,
                'video_id': video_id,
                'video_url': video_url,
                'title': title
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to upload YouTube Short: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def create_short_from_article(self, article: Dict, video_path: str, ai_analysis: str = None, thumbnail_path: str = None) -> Optional[Dict]:
        """
        Create and upload YouTube Short from article
        
        Args:
            article: Article dictionary
            video_path: Path to video file
            ai_analysis: AI-generated analysis/commentary (optional)
            thumbnail_path: Optional path to custom cover image / thumbnail
            
        Returns:
            Upload result or None
        """
        # Create title (YouTube prefers shorter titles for Shorts)
        title = article.get('title', 'Breaking News')
        if len(title) > 80:
            title = title[:77] + "..."
        
        # Create description with AI analysis (like Instagram caption)
        section = article.get('section', 'news')
        
        description = ""
        
        # Add AI analysis if provided
        if ai_analysis:
            description += f"{ai_analysis}\n\n"
        else:
            # Fallback to abstract if no AI analysis
            abstract = article.get('abstract', '')
            if abstract:
                description += f"{abstract[:200]}\n\n"
        
        # Generate direct article URL on Forexyy
        slug = ""
        url = article.get('url', '')
        if url:
            slug = url.split('/')[-1].replace('.html', '')
        if not slug and title:
            import re
            slug = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
        
        forexyy_url = f"https://forexyy.com/article/{slug}" if slug else "https://forexyy.com"
        
        # Add branding, direct link and hashtags
        description += f"🎧 Listen to full AI audio commentary & read story:\n🔗 {forexyy_url}\n\n"
        description += f"🌐 forexyy.com - AI-Powered News Analysis\n\n"
        description += f"#Shorts #News #BreakingNews #{section.replace(' ', '')} #Forexyy"
        
        # Tags
        tags = [
            'news',
            'shorts',
            'breaking news',
            section,
            'forexyy',
            'daily news'
        ]
        
        return self.upload_short(
            video_path=video_path,
            title=title,
            description=description,
            tags=tags,
            category_id='25',  # News & Politics
            thumbnail_path=thumbnail_path
        )


# Environment variable to enable/disable YouTube Shorts
USE_YOUTUBE_SHORTS = os.getenv('USE_YOUTUBE_SHORTS', 'false').lower() == 'true'
