#!/usr/bin/env python3
"""
Vercel Cron Job Handler for Instagram Auto-Poster
Runs every 15 minutes via Vercel Cron
"""

import os
import sys
import logging
from http.server import BaseHTTPRequestHandler

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import NewsToInstagramPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request from Vercel Cron"""
        try:
            logger.info("🔄 Cron job triggered - Starting posting cycle...")
            
            # Create pipeline
            pipeline = NewsToInstagramPipeline()
            
            # Try different sections in priority order
            sections = ['business', 'technology', 'politics', 'entertainment', 'sports', 'home']
            
            posted = False
            for section in sections:
                logger.info(f"📰 Trying section: {section}")
                articles = pipeline.fetch_latest_news(section=section, limit=1)
                
                if articles:
                    logger.info(f"✅ Found article from {section}: {articles[0].get('title')[:60]}...")
                    success = pipeline.post_article_to_instagram(articles[0])
                    
                    if success:
                        logger.info(f"🎉 Successfully posted article from {section} section!")
                        posted = True
                        break
                    else:
                        logger.warning(f"⚠️ Failed to post article from {section}, trying next section...")
                        continue
                else:
                    logger.warning(f"⚠️ No articles found in {section} section")
            
            if posted:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "success", "message": "Article posted successfully"}')
            else:
                logger.error("❌ Could not post article from any section")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "error", "message": "No articles available to post"}')
                
        except Exception as e:
            logger.error(f"❌ Error in cron job: {e}")
            import traceback
            traceback.print_exc()
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_msg = f'{{"status": "error", "message": "{str(e)}"}}'
            self.wfile.write(error_msg.encode())
