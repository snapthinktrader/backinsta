#!/usr/bin/env python3
"""
Scheduled Instagram Poster
Posts news articles to Instagram every 15 minutes
"""

import os
import sys
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

from backinsta.server import NewsToInstagramPipeline
from backinsta.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def post_article():
    """Post a single article to Instagram"""
    try:
        logger.info("🔄 Starting posting cycle...")
        
        # Create pipeline
        pipeline = NewsToInstagramPipeline()
        
        # Try different sections in priority order
        sections = ['business', 'technology', 'politics', 'entertainment', 'sports', 'home']
        
        for section in sections:
            logger.info(f"📰 Trying section: {section}")
            articles = pipeline.fetch_latest_news(section=section, limit=1)
            
            if articles:
                logger.info(f"✅ Found article from {section}: {articles[0].get('title')[:60]}...")
                success = pipeline.post_article_to_instagram(articles[0])
                
                if success:
                    logger.info(f"🎉 Successfully posted article from {section} section!")
                    return True
                else:
                    logger.warning(f"⚠️ Failed to post article from {section}, trying next section...")
                    continue
            else:
                logger.warning(f"⚠️ No articles found in {section} section")
        
        logger.error("❌ Could not post article from any section")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error in posting cycle: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main scheduling loop"""
    print("=" * 70)
    print("🚀 Instagram Auto-Poster Starting...")
    print("=" * 70)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if using local testing interval
    interval_minutes = int(os.getenv('POST_INTERVAL_MINUTES', '0'))
    if interval_minutes > 0:
        print(f"⏰ Posting interval: {interval_minutes} minutes (Production)")
    else:
        print(f"⏰ Posting interval: 15 seconds (Local Testing)")
        print(f"💡 Set POST_INTERVAL_MINUTES=15 for production (15 min)")
    
    print("=" * 70)
    print()
    
    # Validate config
    errors = Config.validate()
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"   - {error}")
        return 1
    
    logger.info("✅ Configuration valid")
    
    # Post interval in seconds
    # Use environment variable or default to 15 seconds for local testing
    # For production on Render, set POST_INTERVAL_MINUTES=15 in environment
    interval_minutes = int(os.getenv('POST_INTERVAL_MINUTES', '0'))
    if interval_minutes > 0:
        POST_INTERVAL = interval_minutes * 60
        logger.info(f"⏰ Using production interval: {interval_minutes} minutes")
    else:
        POST_INTERVAL = 15  # 15 seconds for local testing
        logger.info(f"⏰ Using local testing interval: {POST_INTERVAL} seconds")
    
    # Counter for posts
    post_count = 0
    error_count = 0
    
    while True:
        try:
            cycle_start = datetime.now()
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 Cycle #{post_count + 1} started at {cycle_start.strftime('%H:%M:%S')}")
            logger.info(f"{'='*60}")
            
            # Post article
            success = post_article()
            
            if success:
                post_count += 1
                error_count = 0  # Reset error count on success
                logger.info(f"✅ Total posts so far: {post_count}")
            else:
                error_count += 1
                logger.warning(f"⚠️ Failed attempts: {error_count}")
                
                # If too many consecutive errors, wait longer
                if error_count >= 3:
                    logger.warning("⚠️ Multiple consecutive failures, extending wait time...")
                    time.sleep(300)  # Wait 5 minutes extra
                    error_count = 0
            
            # Calculate next posting time
            next_post_time = datetime.now().timestamp() + POST_INTERVAL
            next_post_datetime = datetime.fromtimestamp(next_post_time)
            
            if POST_INTERVAL >= 60:
                wait_display = f"{POST_INTERVAL // 60} minutes"
            else:
                wait_display = f"{POST_INTERVAL} seconds"
            
            logger.info(f"⏰ Next post scheduled for: {next_post_datetime.strftime('%H:%M:%S')}")
            logger.info(f"💤 Sleeping for {wait_display}...\n")
            
            # Sleep until next cycle
            time.sleep(POST_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("\n\n⚠️ Received interrupt signal")
            logger.info(f"📊 Total posts made: {post_count}")
            logger.info("👋 Shutting down gracefully...")
            break
            
        except Exception as e:
            logger.error(f"❌ Unexpected error in main loop: {e}")
            import traceback
            traceback.print_exc()
            logger.info("⏰ Waiting 5 minutes before retry...")
            time.sleep(300)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
