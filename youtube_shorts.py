#!/usr/bin/env python3
"""
YouTube Shorts API integration
Posts video Reels as YouTube Shorts
"""

import os
import pickle
import logging
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
        
        # Load token if exists
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
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
