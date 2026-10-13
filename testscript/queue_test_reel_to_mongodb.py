#!/usr/bin/env python3
"""
Insert the pre-generated test reel (local_test_reel.mp4) into MongoDB qpost.reels
with status='pending' to test the full pipeline.
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT_DIR, '.env'))

from pymongo import MongoClient

VIDEO_PATH = "/Users/ajaytiwari/Desktop/Projects/localreelgenerator/local_test_reel.mp4"
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://aj:aj@qpost.lk5htbl.mongodb.net/qpost?retryWrites=true&w=majority&appName=qpost")

def main():
    if not os.path.exists(VIDEO_PATH):
        print(f"❌ Video file not found at: {VIDEO_PATH}")
        return False

    with open(VIDEO_PATH, "rb") as f:
        video_data = f.read()

    file_size = len(video_data)
    print(f"📦 Loaded test video file: {file_size / (1024 * 1024):.2f} MB")

    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000, tlsAllowInvalidCertificates=True)
    db = client.qpost

    article_id = f"test_animated_reel_{int(datetime.utcnow().timestamp())}"
    headline = "US Tech Momentum & Global Economic Outlook Analysis"
    caption = (
        "US Tech Momentum & Global Economic Outlook Analysis 📈\n\n"
        "Exploring key market shifts, corporate earnings, and infrastructure developments shaping tomorrow's economy.\n\n"
        "🎧 Full story: https://forexyy.com/article/tech-economic-outlook\n\n"
        "#business #technology #economy #news #trending #viral #reels #forexyy"
    )

    reel_doc = {
        "headline": headline,
        "caption": caption,
        "article_url": "https://forexyy.com/article/tech-economic-outlook",
        "article_id": article_id,
        "video_data": video_data,
        "thumbnail_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1080&q=80",
        "ai_analysis": "Exploring key market shifts, corporate earnings, and infrastructure developments shaping tomorrow's economy.",
        "duration": 32.0,
        "file_size": file_size,
        "section": "business",
        "status": "pending",
        "created_at": datetime.utcnow(),
        "posted_at": None,
        "instagram_post_id": None,
        "youtube_video_id": None,
        "fb_post_id": None,
        "error_message": None,
        "retry_count": 0
    }

    result = db.reels.insert_one(reel_doc)
    print(f"✅ Successfully inserted pending reel into MongoDB qpost.reels!")
    print(f"   Reel ID: {result.inserted_id}")
    print(f"   Article ID: {article_id}")
    print(f"   Status: pending")
    return True

if __name__ == "__main__":
    main()
