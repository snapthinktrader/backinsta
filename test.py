#!/usr/bin/env python3
"""
Test script for BackInsta
Tests article fetching and Instagram posting functionality
"""

import sys
import logging
from config import Config
from server import NewsToInstagramPipeline

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_configuration():
    """Test configuration validation"""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: Configuration Validation")
    logger.info("="*60)
    
    Config.print_config()
    
    errors = Config.validate()
    if errors:
        logger.error("❌ Configuration errors:")
        for error in errors:
            logger.error(f"   - {error}")
        return False
    else:
        logger.info("✅ Configuration valid")
        return True


def test_fetch_articles(section='technology'):
    """Test fetching articles from Webstory backend"""
    logger.info("\n" + "="*60)
    logger.info(f"TEST 2: Fetch Articles from '{section}' Section")
    logger.info("="*60)
    
    try:
        pipeline = NewsToInstagramPipeline()
        articles = pipeline.fetch_latest_news(section=section, limit=5)
        
        if not articles:
            logger.error(f"❌ No articles fetched from section: {section}")
            return False
        
        logger.info(f"✅ Successfully fetched {len(articles)} articles")
        logger.info("\nArticle Preview:")
        
        for i, article in enumerate(articles[:3], 1):
            logger.info(f"\n{i}. {article.get('title', 'No Title')}")
            logger.info(f"   Section: {article.get('section', 'Unknown')}")
            logger.info(f"   URL: {article.get('url', 'No URL')[:60]}...")
            
            multimedia = article.get('multimedia', [])
            logger.info(f"   Images: {len(multimedia)}")
            
            if multimedia:
                logger.info(f"   First Image: {multimedia[0].get('url', 'No URL')[:60]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fetching articles: {e}")
        return False


def test_caption_generation():
    """Test caption generation from article data"""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: Caption Generation")
    logger.info("="*60)
    
    try:
        pipeline = NewsToInstagramPipeline()
        
        # Create sample article
        sample_article = {
            'title': 'Revolutionary AI System Transforms Healthcare Diagnosis',
            'abstract': 'Researchers have developed a groundbreaking artificial intelligence system that can detect multiple diseases with unprecedented accuracy, potentially revolutionizing the healthcare industry.',
            'section': 'Technology',
            'url': 'https://example.com/article/ai-healthcare-breakthrough'
        }
        
        caption = pipeline.create_instagram_caption(sample_article)
        
        logger.info("Generated Caption:")
        logger.info("-" * 60)
        logger.info(caption)
        logger.info("-" * 60)
        logger.info(f"Caption Length: {len(caption)} characters")
        
        if len(caption) > Config.MAX_CAPTION_LENGTH:
            logger.warning(f"⚠️ Caption exceeds max length ({Config.MAX_CAPTION_LENGTH})")
        else:
            logger.info("✅ Caption within length limits")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error generating caption: {e}")
        return False


def test_image_extraction():
    """Test extracting images from articles"""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: Image Extraction")
    logger.info("="*60)
    
    try:
        pipeline = NewsToInstagramPipeline()
        articles = pipeline.fetch_latest_news(section='home', limit=5)
        
        if not articles:
            logger.error("❌ No articles to test image extraction")
            return False
        
        images_found = 0
        for article in articles:
            image_url = pipeline.get_article_image_url(article)
            if image_url:
                images_found += 1
                logger.info(f"✅ Image found: {article.get('title', 'Unknown')[:50]}")
                logger.info(f"   URL: {image_url[:60]}...")
        
        logger.info(f"\n📊 Images found: {images_found}/{len(articles)}")
        
        if images_found > 0:
            logger.info("✅ Image extraction working")
            return True
        else:
            logger.warning("⚠️ No images found in articles")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error extracting images: {e}")
        return False


def test_dry_run_posting():
    """Test posting pipeline (dry run - no actual Instagram post)"""
    logger.info("\n" + "="*60)
    logger.info("TEST 5: Dry Run Posting Pipeline")
    logger.info("="*60)
    
    try:
        pipeline = NewsToInstagramPipeline()
        articles = pipeline.fetch_latest_news(section='technology', limit=3)
        
        if not articles:
            logger.error("❌ No articles to test posting")
            return False
        
        logger.info(f"Testing with {len(articles)} articles...")
        
        for i, article in enumerate(articles, 1):
            logger.info(f"\n--- Article {i} ---")
            logger.info(f"Title: {article.get('title', 'Unknown')[:60]}")
            
            # Test image extraction
            image_url = pipeline.get_article_image_url(article)
            if image_url:
                logger.info(f"✅ Image available: {image_url[:50]}...")
            else:
                logger.warning("⚠️ No image available")
                continue
            
            # Test caption generation
            caption = pipeline.create_instagram_caption(article)
            logger.info(f"✅ Caption generated ({len(caption)} chars)")
            logger.info(f"Preview: {caption[:100]}...")
            
            logger.info("✅ Article ready for posting")
        
        logger.info("\n✅ Dry run complete - articles processed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in dry run: {e}")
        return False


def test_live_posting():
    """Test actual posting to Instagram (USE WITH CAUTION)"""
    logger.info("\n" + "="*60)
    logger.info("TEST 6: LIVE Instagram Posting")
    logger.info("="*60)
    logger.warning("⚠️ This will make an actual Instagram post!")
    
    confirm = input("\nType 'YES' to proceed with live posting: ")
    
    if confirm != 'YES':
        logger.info("❌ Live posting cancelled")
        return False
    
    try:
        pipeline = NewsToInstagramPipeline()
        
        # Post just one article as a test
        logger.info("🚀 Running live posting test with 1 article...")
        pipeline.run_posting_cycle(section='technology', max_posts=1)
        
        logger.info("✅ Live posting test complete")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error in live posting: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("\n🚀 BackInsta Test Suite")
    logger.info("="*60)
    
    tests = [
        ("Configuration", test_configuration),
        ("Fetch Articles", lambda: test_fetch_articles('technology')),
        ("Caption Generation", test_caption_generation),
        ("Image Extraction", test_image_extraction),
        ("Dry Run Posting", test_dry_run_posting),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' failed with exception: {e}")
            results[test_name] = False
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info("="*60)
    logger.info(f"Results: {passed}/{total} tests passed")
    logger.info("="*60)
    
    # Offer live posting test
    if passed == total:
        logger.info("\n✅ All tests passed! Ready for live posting.")
        logger.info("\nRun live posting test?")
        test_live_posting()
    else:
        logger.warning("\n⚠️ Some tests failed. Fix issues before live posting.")
        sys.exit(1)


if __name__ == '__main__':
    main()
