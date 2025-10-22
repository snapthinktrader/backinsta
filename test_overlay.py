#!/usr/bin/env python3
"""
Test script to verify text overlay spacing
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

from backinsta.server import NewsToInstagramPipeline

def main():
    print("🎨 Testing Text Overlay with Proper Spacing")
    print("=" * 70)
    
    pipeline = NewsToInstagramPipeline()
    
    # Fetch one article
    articles = pipeline.fetch_latest_news(section='business', limit=1)
    
    if not articles:
        print("❌ No articles found")
        return 1
    
    article = articles[0]
    print(f"\n📰 Article: {article.get('title')}")
    
    # Get image
    image_url = pipeline.get_article_image_url(article)
    if not image_url:
        print("❌ No image found")
        return 1
    
    print(f"📸 Image URL: {image_url[:80]}...")
    
    # Create overlay
    print("\n🎨 Creating text overlay with proper spacing...")
    result = pipeline.add_text_to_image(
        image_url,
        article.get('title'),
        article.get('section', 'News')
    )
    
    if result:
        print(f"✅ Overlay created successfully!")
        print(f"🔗 Hosted at: {result}")
        print("\n📋 Spacing should now be:")
        print("   ├─ Section tag at top")
        print("   ├─ Title below section (with spacing)")
        print("   └─ FOREXYY.COM branding at bottom (well separated)")
    else:
        print("❌ Failed to create overlay")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
