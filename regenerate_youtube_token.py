#!/usr/bin/env python3
"""
Script to regenerate YouTube token when it expires or gets revoked
Run this when you get "invalid_grant: Token has been expired or revoked" error
"""

import os
import pickle
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def regenerate_youtube_token():
    """Delete old token and trigger re-authentication"""
    
    token_file = 'youtube_token.pickle'
    credentials_file = 'youtube_credentials.json'
    
    # Check if credentials file exists
    if not os.path.exists(credentials_file):
        logger.error(f"❌ YouTube credentials file not found: {credentials_file}")
        logger.info("💡 Please ensure 'youtube_credentials.json' exists in this directory")
        logger.info("   You can download it from Google Cloud Console")
        return False
    
    # Remove old token if exists
    if os.path.exists(token_file):
        logger.info(f"🗑️  Removing old token file: {token_file}")
        os.remove(token_file)
        logger.info("✅ Old token removed")
    else:
        logger.info(f"ℹ️  No existing token file found")
    
    # Import and initialize YouTubeShortsUploader (will trigger authentication)
    try:
        logger.info("🔐 Starting YouTube authentication flow...")
        logger.info("📝 A browser window will open for you to authorize the app")
        logger.info("   Please sign in with: forexyynewsletter@gmail.com")
        
        from youtube_shorts import YouTubeShortsUploader
        uploader = YouTubeShortsUploader()
        
        if uploader.youtube:
            logger.info("✅ YouTube authentication successful!")
            logger.info(f"💾 New token saved to: {token_file}")
            logger.info("✅ Token is ready for uploading YouTube Shorts")
            return True
        else:
            logger.error("❌ YouTube authentication failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during authentication: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("YouTube Token Regeneration Tool")
    print("="*60 + "\n")
    
    success = regenerate_youtube_token()
    
    print("\n" + "="*60)
    if success:
        print("✅ SUCCESS! YouTube token has been regenerated")
        print("\nYou can now run your poster script:")
        print("  python3 scheduled_poster.py")
        print("  python3 cockroach_poster.py")
    else:
        print("❌ FAILED! Please check the errors above")
        print("\nTroubleshooting:")
        print("  1. Ensure 'youtube_credentials.json' exists")
        print("  2. Check your Google Cloud Console OAuth settings")
        print("  3. Verify test user is added: forexyynewsletter@gmail.com")
    print("="*60 + "\n")
