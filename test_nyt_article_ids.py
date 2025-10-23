#!/usr/bin/env python3
"""
Test NYT API article ID generation
Verify that all new articles from NYT API get article_id assigned
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import from server
from server import NewsToInstagramPipeline

def test_nyt_article_ids():
    """Test that NYT articles get article_id assigned"""
    
    print("🧪 Testing NYT Article ID Generation")
    print("=" * 60)
    
    # Initialize pipeline
    pipeline = NewsToInstagramPipeline()
    
    # Fetch fresh articles from NYT API
    print("\n📰 Fetching articles from NYT API...")
    articles = pipeline.fetch_latest_news(section='technology', limit=5)
    
    print(f"\n✅ Fetched {len(articles)} articles")
    print("=" * 60)
    
    # Check each article
    all_have_ids = True
    for i, article in enumerate(articles, 1):
        print(f"\n📄 Article {i}:")
        print(f"   Title: {article.get('title', 'N/A')[:60]}...")
        print(f"   URL: {article.get('url', 'N/A')[:50]}...")
        
        # Check if article_id exists
        if 'article_id' in article:
            print(f"   ✅ article_id: {article['article_id']}")
        else:
            print(f"   ❌ NO article_id found!")
            all_have_ids = False
    
    print("\n" + "=" * 60)
    if all_have_ids:
        print("✅ SUCCESS: All articles have article_id!")
    else:
        print("❌ FAILURE: Some articles missing article_id")
    
    print("=" * 60)
    
    return all_have_ids


if __name__ == '__main__':
    success = test_nyt_article_ids()
    sys.exit(0 if success else 1)
