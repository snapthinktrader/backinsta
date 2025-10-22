#!/usr/bin/env python3
"""
Test script to post a single news article to Instagram
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

from backinsta.server import NewsToInstagramPipeline
from backinsta.config import Config

def main():
    print("=" * 70)
    print("📰 Test: Post News Article to Instagram")
    print("=" * 70)
    print()
    
    # Print config
    Config.print_config()
    
    # Validate config
    errors = Config.validate()
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"   - {error}")
        return 1
    
    print("\n✅ Configuration valid")
    print()
    
    # Create pipeline
    pipeline = NewsToInstagramPipeline()
    
    # Fetch latest articles
    print("📡 Fetching latest news articles...")
    articles = pipeline.fetch_latest_news(section='business', limit=5)
    
    if not articles:
        print("❌ No articles found")
        return 1
    
    print(f"✅ Found {len(articles)} articles\n")
    
    # Display first article
    article = articles[0]
    print("=" * 70)
    print("📄 Article to post:")
    print("=" * 70)
    print(f"Title: {article.get('title', 'N/A')}")
    print(f"Section: {article.get('section', 'N/A')}")
    print(f"Abstract: {article.get('abstract', 'N/A')[:100]}...")
    
    # Get image URL
    image_url = pipeline.get_article_image_url(article)
    print(f"\n📸 Image URL: {image_url[:80] if image_url else 'None'}...")
    
    if not image_url:
        print("❌ No image found for article")
        return 1
    
    # Generate caption
    caption = pipeline.create_instagram_caption(article)
    print(f"\n📝 Caption preview:\n{caption[:200]}...\n")
    
    # Ask for confirmation
    response = input("🤔 Post this article to Instagram? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("❌ Posting cancelled")
        return 0
    
    print("\n🚀 Posting to Instagram...\n")
    
    # Post to Instagram
    success = pipeline.post_article_to_instagram(article)
    
    if success:
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Article posted to Instagram")
        print("=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print("❌ FAILED to post article")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    sys.exit(main())
