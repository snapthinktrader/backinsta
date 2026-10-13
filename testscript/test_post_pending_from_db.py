#!/usr/bin/env python3
"""
Test script: Check for pending pre-generated reels in MongoDB (qpost.reels)
and cross-post the pre-rendered reel across Instagram, YouTube Shorts, and Facebook Page.
"""

import os
import sys
import logging

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT_DIR, '.env'))

from server import NewsToInstagramPipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestPendingReelPost")

def main():
    logger.info("=" * 60)
    logger.info("🧪 TESTING POSTING PRE-GENERATED REEL FROM MONGODB")
    logger.info("=" * 60)

    pipeline = NewsToInstagramPipeline()

    logger.info("🔍 Checking for pending pre-generated reels in qpost.reels...")
    pending_reel = pipeline.get_pending_reel_from_mongodb()

    if not pending_reel:
        logger.warning("⚠️ No pending reel found in MongoDB currently.")
        logger.info("💡 Once the GitHub Actions workflow finishes, pending reels will be available.")
        return False

    headline = pending_reel.get("headline", "No headline")
    logger.info(f"✅ Found pending reel: {headline}")
    logger.info(f"   Section: {pending_reel.get('section')}")
    logger.info(f"   Duration: {pending_reel.get('duration')}s")
    logger.info(f"   File size: {pending_reel.get('file_size', 0) / (1024*1024):.2f} MB")

    logger.info("\n🚀 Posting pre-generated reel across all platforms...")
    success = pipeline.post_pending_reel_from_mongodb(pending_reel)

    logger.info("\n" + "=" * 60)
    logger.info(f"RESULT: Post Pending Reel Success = {success}")
    logger.info("=" * 60)
    return success

if __name__ == '__main__':
    main()
