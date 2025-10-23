#!/usr/bin/env python3
"""
Database utilities for BackInsta
Stores posted articles to prevent duplicates and track analytics
"""

import os
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
            self.collection.create_index("article_url", unique=True)
            self.collection.create_index("posted_at")
            self.collection.create_index("section")
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            self.client = None
    
    def mark_as_posted(self, article: Dict, post_result: Dict) -> bool:
        """
        Mark article as posted (lightweight: only stores article ID and minimal data)
        
        Args:
            article: Article data
            post_result: Instagram post result
            
        Returns:
            True if saved successfully
        """
        if self.collection is None:
            return False
        
        try:
            # Store minimal data to save MongoDB space
            doc = {
                'article_url': article.get('url'),  # NYT article URL as unique identifier
                'article_title': article.get('title')[:100],  # Truncated title
                'section': article.get('section'),
                'instagram_post_id': post_result.get('post_id'),
                'posted_at': datetime.now()
            }
            
            self.collection.insert_one(doc)
            logger.info(f"✅ Article saved to database: {article.get('title')[:50]}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save article to database: {e}")
            return False
    
    def is_already_posted(self, article_url: str) -> bool:
        """
        Check if article has already been posted
        
        Args:
            article_url: URL of the article
            
        Returns:
            True if already posted
        """
        if self.collection is None:
            return False
        
        try:
            result = self.collection.find_one({'article_url': article_url})
            return result is not None
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
