#!/usr/bin/env python3
"""
Test script to verify reel generation and posting across:
1. Instagram Graph API
2. Facebook Page (forexyy.com)
3. YouTube Shorts
and ensure MongoDB records are updated cleanly.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add root directory to sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, '.env'))

from server import NewsToInstagramPipeline
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TestTriplePost")

def main():
    logger.info("=" * 60)
    logger.info("🚀 STARTING LOCALHOST TRIPLE-CROSS POSTING TEST")
    logger.info("=" * 60)

    pipeline = NewsToInstagramPipeline()

    logger.info("📰 Fetching 1 fresh article to test reel generation and posting...")
    articles = pipeline.fetch_latest_news(section='business', limit=3)
    
    selected_article = None
    for a in articles:
        img_url = pipeline.get_article_image_url(a)
        if img_url:
            selected_article = a
            break
            
    if not selected_article:
        logger.warning("⚠️ No article with image found in NYT response, creating sample test article...")
        selected_article = {
            'title': 'Global Market Rally Continues as Tech and Crypto Surge',
            'abstract': 'Markets gained momentum today as technology earnings and economic indicators beat forecasts.',
            'url': f"https://www.nytimes.com/test-article-{int(datetime.utcnow().timestamp())}.html",
            'section': 'business',
            'image_url': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1080&q=80',
            'published_date': datetime.utcnow()
        }

    logger.info(f" Selected Article: {selected_article.get('title')}")
    logger.info(f"🔗 Article URL: {selected_article.get('url')}")
    
    logger.info("\n🎬 Running pipeline post_article_to_instagram...")
    success = pipeline.post_article_to_instagram(selected_article)
    
    logger.info("\n" + "=" * 60)
    logger.info(f"RESULT: Overall Pipeline Post Success = {success}")
    logger.info("=" * 60)
    
    # Verify database state
    if pipeline.db and pipeline.db.collection is not None:
        saved = pipeline.db.collection.find_one({'article_url': selected_article.get('url')})
        logger.info(f"📊 Database Document State: {saved}")

if __name__ == '__main__':
    main()
