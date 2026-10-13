#!/usr/bin/env python3
"""
Test script: Post a single news article to Instagram
"""

import sys
import os
import logging

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(__file__))

from server import NewsToInstagramPipeline
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Test posting a single article"""
    logger.info("🧪 BackInsta Test - Posting News Article to Instagram")
    logger.info("=" * 60)
    
    # Validate configuration
    Config.print_config()
    errors = Config.validate()
    
    if errors:
        logger.error("\n❌ Configuration Errors:")
        for error in errors:
            logger.error(f"   - {error}")
        logger.error("\nPlease fix configuration in .env file")
        return False
    
    logger.info("✅ Configuration valid\n")
    
    # Initialize pipeline
    pipeline = NewsToInstagramPipeline()
    
    # Fetch latest articles
    logger.info("📰 Fetching latest news articles...")
    articles = pipeline.fetch_latest_news(section='technology', limit=5)
    
    if not articles:
        logger.error("❌ No articles found to post")
        return False
    
    logger.info(f"✅ Found {len(articles)} articles\n")
    
    # Show available articles
    logger.info("📋 Available articles:")
    for i, article in enumerate(articles, 1):
        title = article.get('title', 'Untitled')
        url = article.get('url', 'No URL')
        has_image = bool(pipeline.get_article_image_url(article))
        logger.info(f"{i}. {title[:60]}... {'✓' if has_image else '✗ (no image)'}")
    
    # Try to post the first article with an image
    logger.info("\n" + "=" * 60)
    logger.info("🚀 Attempting to post article to Instagram...")
    logger.info("=" * 60 + "\n")
    
    for article in articles:
        if pipeline.get_article_image_url(article):
            logger.info(f"📰 Selected article: {article.get('title', 'Unknown')[:60]}...")
            success = pipeline.post_article_to_instagram(article)
            
            if success:
                logger.info("\n" + "=" * 60)
                logger.info("✅ SUCCESS! Article posted to Instagram!")
                logger.info("=" * 60)
                logger.info("🎉 Check your Instagram feed to see the post!")
                logger.info("\n💡 To post more articles, run:")
                logger.info("   python3 backinsta/server.py")
                return True
            else:
                logger.error("\n❌ Failed to post article")
                logger.info("🔄 Trying next article...\n")
                continue
    
    logger.error("\n❌ Could not post any article. All attempts failed.")
    return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
