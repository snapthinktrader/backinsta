#!/usr/bin/env python3
"""
Database utilities for BackInsta
Stores posted articles to prevent duplicates and track analytics
"""

import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

try:
    from pymongo import MongoClient
    from bson import ObjectId
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    logger.warning("⚠️ pymongo not installed. Database features disabled.")


def generate_article_id(title: str, url: str = None) -> str:
    """
    Generate a unique article ID from title and optionally URL
    This ensures we never post the same article twice
    
    Args:
        title: Article title/headline
        url: Optional article URL for extra uniqueness
        
    Returns:
        Unique article ID (MD5 hash)
    """
    # Normalize title: lowercase, remove extra whitespace
    normalized_title = ' '.join(title.lower().strip().split())
    
    # Create unique string
    if url:
        unique_string = f"{normalized_title}|{url}"
    else:
        unique_string = normalized_title
    
    # Generate MD5 hash (first 16 chars is enough for uniqueness)
    article_id = hashlib.md5(unique_string.encode()).hexdigest()[:16]
    return article_id


class BackInstaDB:
    """Database handler for BackInsta"""
    
    def __init__(self, mongodb_uri: str):
        """
        Initialize database connection
        
        Args:
            mongodb_uri: MongoDB connection string
        """
        self.mongodb_uri = mongodb_uri
        self.client = None
        self.db = None
        self.collection = None
        
        if MONGODB_AVAILABLE:
            self._connect()
    
    def _connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(
                self.mongodb_uri, 
                serverSelectionTimeoutMS=5000,
                tlsAllowInvalidCertificates=True  # Allow self-signed certificates
            )
            self.db = self.client.backinsta
            self.collection = self.db.posted_articles
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("✅ MongoDB connection successful")
            
            # Create indexes for efficient queries
            try:
                self.collection.create_index("article_url", unique=True)
                self.collection.create_index("posted_at")
                self.collection.create_index("section")
                
                # Create article_id index (sparse to allow old documents without article_id)
                self.collection.create_index("article_id", unique=True, sparse=True)
                logger.info("✅ Database indexes created")
            except Exception as idx_error:
                logger.warning(f"⚠️ Could not create all indexes: {idx_error}")
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            self.client = None
    
    def mark_as_posted(self, article: Dict, post_result: Dict) -> bool:
        """
        Mark article as posted (lightweight: only stores article ID and minimal data)
        
        Args:
            article: Article data
            post_result: Instagram/YouTube post result
            
        Returns:
            True if saved successfully
        """
        if self.collection is None:
            return False
        
        try:
            # Generate unique article ID from title
            article_id = generate_article_id(
                title=article.get('title', ''),
                url=article.get('url')
            )
            
            # Store minimal data to save MongoDB space
            doc = {
                'article_id': article_id,  # Unique ID based on title+URL
                'article_url': article.get('url'),  # NYT article URL
                'article_title': article.get('title')[:100],  # Truncated title
                'section': article.get('section'),
                'instagram_post_id': post_result.get('post_id'),
                'youtube_video_id': post_result.get('youtube_video_id'),
                'youtube_url': post_result.get('youtube_url'),
                'posted_at': datetime.now()
            }
            
            # Use upsert to avoid duplicates (update if article_id exists)
            self.collection.update_one(
                {'article_id': article_id},
                {'$set': doc},
                upsert=True
            )
            logger.info(f"✅ Article saved to database (ID: {article_id}): {article.get('title')[:50]}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save article to database: {e}")
            return False
    
    def is_already_posted(self, article_url: str = None, article_title: str = None) -> bool:
        """
        Check if article has already been posted (by URL or title)
        
        Args:
            article_url: URL of the article
            article_title: Title of the article
            
        Returns:
            True if already posted
        """
        if self.collection is None:
            return False
        
        try:
            # Check by article ID (generated from title)
            if article_title:
                article_id = generate_article_id(title=article_title, url=article_url)
                result = self.collection.find_one({'article_id': article_id})
                if result:
                    return True
            
            # Fallback: check by URL
            if article_url:
                result = self.collection.find_one({'article_url': article_url})
                return result is not None
                
            return False
        except Exception as e:
            logger.error(f"❌ Error checking if article posted: {e}")
            return False
    
    def get_posted_articles(self, limit: int = 100) -> List[Dict]:
        """
        Get list of posted articles
        
        Args:
            limit: Maximum number of articles to return
            
        Returns:
            List of posted articles
        """
        if self.collection is None:
            return []
        
        try:
            cursor = self.collection.find().sort('posted_at', -1).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"❌ Error fetching posted articles: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """
        Get posting statistics
        
        Returns:
            Dictionary with stats
        """
        if self.collection is None:
            return {'total_posts': 0, 'sections': {}}
        
        try:
            total = self.collection.count_documents({})
            
            # Get counts by section
            pipeline = [
                {'$group': {'_id': '$section', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}
            ]
            section_stats = list(self.collection.aggregate(pipeline))
            
            sections = {item['_id']: item['count'] for item in section_stats}
            
            return {
                'total_posts': total,
                'sections': sections
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {'total_posts': 0, 'sections': {}}
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("✅ Database connection closed")
