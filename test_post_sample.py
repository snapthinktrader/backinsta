#!/usr/bin/env python3
"""
Test script: Post a sample article to Instagram (no Webstory dependency)
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

# Sample article data
SAMPLE_ARTICLE = {
    'title': 'AI Revolution: How Machine Learning is Transforming Healthcare',
    'abstract': 'Breakthrough developments in artificial intelligence are revolutionizing patient care and medical diagnostics. Researchers report significant improvements in early disease detection.',
    'section': 'technology',
    'url': 'https://example.com/ai-healthcare-revolution',
    'byline': 'Tech News Team',
    'source': 'Tech Daily',
    'publishedDate': '2025-10-21',
    'multimedia': [
        {
            'url': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=1200',
            'format': 'superJumbo',
            'type': 'image'
        }
    ]
}

def main():
    """Test posting a sample article"""
    logger.info("🧪 BackInsta Test - Posting Sample Article to Instagram")
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
    
    # Show sample article details
    logger.info("📋 Sample Article Details:")
    logger.info(f"Title: {SAMPLE_ARTICLE['title']}")
    logger.info(f"Section: {SAMPLE_ARTICLE['section']}")
    logger.info(f"Has Image: {'✓' if SAMPLE_ARTICLE.get('multimedia') else '✗'}")
    
    # Generate caption
    caption = pipeline.create_instagram_caption(SAMPLE_ARTICLE)
    logger.info("\n📝 Generated Caption:")
    logger.info("-" * 60)
    logger.info(caption)
    logger.info("-" * 60)
    
    # Post to Instagram
    logger.info("\n" + "=" * 60)
    logger.info("🚀 Posting to Instagram...")
    logger.info("=" * 60 + "\n")
    
    success = pipeline.post_article_to_instagram(SAMPLE_ARTICLE)
    
    if success:
        logger.info("\n" + "=" * 60)
        logger.info("✅ SUCCESS! Article posted to Instagram!")
        logger.info("=" * 60)
        logger.info("🎉 Check your Instagram feed to see the post!")
        logger.info("\n💡 Next steps:")
        logger.info("   1. Verify the post on Instagram")
        logger.info("   2. Check backinsta/check_linked_instagrams.py to see linked accounts")
        logger.info("   3. Run: python3 backinsta/server.py for automated posting")
        return True
    else:
        logger.error("\n❌ Failed to post article")
        logger.info("\n💡 Troubleshooting:")
        logger.info("   1. Verify REACT_APP_ACCESS_TOKEN is valid")
        logger.info("   2. Check REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID is correct")
        logger.info("   3. Ensure image URL is publicly accessible")
        logger.info("   4. Check Instagram API rate limits")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
