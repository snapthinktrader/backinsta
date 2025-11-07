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
        """Authenticate with YouTube API - handles token refresh automatically"""
        creds = None
        needs_new_token = False
        
        # Check for base64-encoded credentials from environment (for Render deployment)
        credentials_base64 = os.getenv('YOUTUBE_CREDENTIALS_BASE64')
        token_base64 = os.getenv('YOUTUBE_TOKEN_BASE64')
        
        # Decode and save credentials if provided via environment
        if credentials_base64:
            try:
                if not os.path.exists(self.credentials_file):
                    logger.info("📦 Decoding YouTube credentials from environment variable...")
                    credentials_json = base64.b64decode(credentials_base64).decode('utf-8')
                    with open(self.credentials_file, 'w') as f:
                        f.write(credentials_json)
                    logger.info("✅ YouTube credentials file created from environment")
            except Exception as e:
                logger.error(f"❌ Failed to decode YouTube credentials: {e}")
        
        # Always reload token from environment if available (keeps it fresh)
        if token_base64:
            try:
                logger.info("📦 Loading YouTube token from environment variable...")
                token_data = base64.b64decode(token_base64)
                with open(self.token_file, 'wb') as f:
                    f.write(token_data)
                logger.info("✅ YouTube token loaded from environment")
            except Exception as e:
                logger.error(f"❌ Failed to decode YouTube token: {e}")
                needs_new_token = True
        
        # Load token if exists and not corrupted
        if os.path.exists(self.token_file) and not needs_new_token:
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                logger.info("📂 Loaded existing YouTube token")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load token file: {e}")
                needs_new_token = True
                creds = None
        
        # Validate and refresh credentials automatically
        if creds and not needs_new_token:
            try:
                # Check if token is valid
                if not creds.valid:
                    if creds.expired and creds.refresh_token:
                        logger.info("🔄 Token expired, refreshing automatically...")
                        creds.refresh(Request())
                        logger.info("✅ Token refreshed successfully")
                        # Save the refreshed token
                        with open(self.token_file, 'wb') as token:
                            pickle.dump(creds, token)
                        logger.info("💾 Refreshed token saved")
                    else:
                        logger.warning("⚠️ Token invalid and cannot be refreshed")
                        needs_new_token = True
                        creds = None
                else:
                    logger.info("✅ YouTube token is valid")
            except Exception as refresh_error:
                # Token refresh failed (revoked, expired, or network issue)
                error_msg = str(refresh_error)
                if 'invalid_grant' in error_msg.lower():
                    logger.warning(f"⚠️ Token has been revoked or expired: {refresh_error}")
                    logger.info("🔄 Token needs re-authentication (likely revoked by user or expired)")
                else:
                    logger.warning(f"⚠️ Token refresh failed: {refresh_error}")
                
                # Delete the invalid token
                if os.path.exists(self.token_file):
                    os.remove(self.token_file)
                    logger.info("🗑️ Removed invalid token file")
                
                needs_new_token = True
                creds = None
        
        # If credentials still not valid, need to authenticate
        if not creds or needs_new_token:
            if not os.path.exists(self.credentials_file):
                logger.error(f"❌ YouTube credentials file not found: {self.credentials_file}")
                logger.info("💡 To enable YouTube Shorts:")
                logger.info("   1. Go to https://console.cloud.google.com/")
                logger.info("   2. Create a project and enable YouTube Data API v3")
                logger.info("   3. Create OAuth 2.0 credentials (Desktop app)")
                logger.info("   4. Download as 'youtube_credentials.json'")
                logger.info("   5. Run: python3 regenerate_youtube_token.py")
                return
            
            logger.info("🔐 Starting OAuth authentication flow...")
            logger.info("📝 A browser window will open for authorization")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
                logger.info("✅ Authentication successful")
            except Exception as auth_error:
                logger.error(f"❌ Authentication failed: {auth_error}")
                return
            
            # Save token for future use
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                logger.info("💾 New token saved successfully")
                
                # If in environment mode, remind to update env vars
                if os.getenv('YOUTUBE_TOKEN_BASE64'):
                    logger.warning("⚠️ IMPORTANT: Update your YOUTUBE_TOKEN_BASE64 environment variable!")
                    logger.info("   Run: ./encode_youtube_token.sh")
            except Exception as save_error:
                logger.error(f"❌ Failed to save token: {save_error}")
        
        # Build YouTube API client
        if creds:
            try:
                self.youtube = build('youtube', 'v3', credentials=creds)
                logger.info("✅ YouTube API client ready")
            except Exception as e:
                logger.error(f"❌ Failed to build YouTube API client: {e}")
                self.youtube = None
        else:
            logger.error("❌ No valid credentials available")
            self.youtube = None
    
    def upload_short(self, video_path: str, title: str, description: str = "", 
                     tags: list = None, category_id: str = "25") -> Optional[Dict]:
        """
        Upload video as YouTube Short
        
        Args:
            video_path: Path to video file
            title: Video title (max 100 chars)
            description: Video description (include #Shorts)
            tags: List of tags
            category_id: YouTube category (25 = News & Politics)
            
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
    
    def create_short_from_article(self, article: Dict, video_path: str, ai_analysis: str = None) -> Optional[Dict]:
        """
        Create and upload YouTube Short from article
        
        Args:
            article: Article dictionary
            video_path: Path to video file
            ai_analysis: AI-generated analysis/commentary (optional)
            
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
        
        # Add branding and hashtags
        description += f"🌐 forexyy.com - Your Daily News Source\n\n"
        description += f"#Shorts #News #BreakingNews #{section.replace(' ', '')}"
        
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
            category_id='25'  # News & Politics
        )


# Environment variable to enable/disable YouTube Shorts
USE_YOUTUBE_SHORTS = os.getenv('USE_YOUTUBE_SHORTS', 'false').lower() == 'true'
