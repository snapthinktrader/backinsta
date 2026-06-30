#!/usr/bin/env python3
"""
Scheduled poster for BackInsta - Posts articles at regular intervals
"""

import os
import sys
import time
import signal
from datetime import datetime
import logging
import requests
from dotenv import load_dotenv
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import from same directory (not as package)
from server import NewsToInstagramPipeline
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simple health check handler for Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Match /, /health, /health1, /health2, /health3, /health4, /health5 (with or without trailing slash)
        path = self.path.rstrip('/')
        if path in ['', '/health', '/health1', '/health2', '/health3', '/health4', '/health5']:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK - Instagram Auto-Poster Running')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress HTTP logs to keep output clean
        pass

def post_article():
    """Post a single article to Instagram and YouTube (both platforms attempted independently)"""
    try:
        logger.info("🔄 Starting multi-platform posting cycle...")
        
        # Create pipeline
        pipeline = NewsToInstagramPipeline()
        
        # Try different sections in priority order
        sections = ['business', 'technology', 'politics', 'entertainment', 'sports', 'home']
        
        for section in sections:
            logger.info(f"📰 Trying section: {section}")
            articles = pipeline.fetch_latest_news(section=section, limit=1)
            
            if articles:
                article = articles[0]
                logger.info(f"✅ Found article from {section}: {article.get('title')[:60]}...")
                
                # CRITICAL: ONE ATTEMPT PER ARTICLE - NEVER RETRY THE SAME ARTICLE
                # Even if both platforms fail, we mark it as attempted and move to next cycle
                success = pipeline.post_article_to_instagram(article)
                
                # Return immediately after first article attempt (success or failure)
                # The article is already marked as "attempted" in the database
                if success:
                    logger.info(f"🎉 Successfully posted to at least one platform from {section} section!")
                    return True
                else:
                    logger.warning(f"⚠️ Both platforms failed for article from {section}")
                    logger.info(f"✅ Article marked as attempted - will try DIFFERENT article next cycle")
                    return False  # ← CHANGED: Stop here, don't try more sections
            else:
                logger.warning(f"⚠️ No articles found in {section} section")
        
        logger.error("❌ Could not find any fresh articles from any section")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error in posting cycle: {e}")
        import traceback
        traceback.print_exc()
        return False

def keep_alive_during_sleep(sleep_duration, ping_interval=720):
    """
    Keep Render service alive during sleep by pinging health endpoints
    
    Args:
        sleep_duration: Total time to sleep in seconds
        ping_interval: Time between pings in seconds (default 12 minutes = 720s)
    """
    # Get the service URL from environment (Render provides this)
    service_url = os.getenv('RENDER_EXTERNAL_URL', 'http://localhost:10000')
    
    # Try different endpoints as fallbacks
    endpoints = ["/health", "/health1", "/health2", "/health3", "/health4"]
    
    elapsed = 0
    endpoint_idx = 0
    while elapsed < sleep_duration:
        # Calculate how long to sleep this iteration
        sleep_time = min(ping_interval, sleep_duration - elapsed)
        time.sleep(sleep_time)
        elapsed += sleep_time
        
        # Ping health endpoint if we're not done sleeping
        if elapsed < sleep_duration:
            # Rotate endpoints to avoid hitting the same blocked/cached path
            endpoint = endpoints[endpoint_idx % len(endpoints)]
            endpoint_idx += 1
            health_url = f"{service_url.rstrip('/')}{endpoint}"
            
            try:
                logger.info(f"💓 Sending keep-alive ping to {health_url}...")
                response = requests.get(health_url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"💓 Keep-alive ping to {endpoint} successful ({elapsed}/{sleep_duration}s)")
                else:
                    logger.warning(f"⚠️ Keep-alive ping to {endpoint} returned {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ Keep-alive ping to {endpoint} failed: {e}")

def main():
    """Main scheduling loop"""
    print("=" * 70)
    print("🚀 Instagram Auto-Poster Starting...")
    print("=" * 70)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if using local testing interval
    interval_minutes = int(os.getenv('POST_INTERVAL_MINUTES', '0'))
    if interval_minutes > 0:
        print(f"⏰ Posting interval: {interval_minutes} minutes (Production)")
    else:
        print(f"⏰ Posting interval: 15 seconds (Local Testing)")
        print(f"💡 Set POST_INTERVAL_MINUTES=15 for production (15 min)")
    
    print("=" * 70)
    print()
    
    # Start health check servers in background on multiple ports (for Render web service redundancy)
    base_port = int(os.getenv('PORT', '10000'))
    ports = [base_port + i for i in range(5)]
    health_servers = []
    
    for p in ports:
        try:
            health_server = HTTPServer(('0.0.0.0', p), HealthCheckHandler)
            health_thread = Thread(target=health_server.serve_forever, daemon=True)
            health_thread.start()
            logger.info(f"🏥 Health check server started on port {p}")
            health_servers.append(health_server)
        except Exception as e:
            logger.error(f"❌ Failed to start health check server on port {p}: {e}")
    
    # Validate config
    errors = Config.validate()
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"   - {error}")
        return 1
    
    logger.info("✅ Configuration valid")
    
    # Post interval in seconds
    # Use environment variable or default to 15 seconds for local testing
    # For production on Render, set POST_INTERVAL_MINUTES=15 in environment
    interval_minutes = int(os.getenv('POST_INTERVAL_MINUTES', '0'))
    if interval_minutes > 0:
        POST_INTERVAL = interval_minutes * 60
        logger.info(f"⏰ Using production interval: {interval_minutes} minutes")
    else:
        POST_INTERVAL = 15  # 15 seconds for local testing
        logger.info(f"⏰ Using local testing interval: {POST_INTERVAL} seconds")
    
    # Counter for posts
    post_count = 0
    error_count = 0
    
    while True:
        try:
            cycle_start = datetime.now()
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 Cycle #{post_count + 1} started at {cycle_start.strftime('%H:%M:%S')}")
            logger.info(f"{'='*60}")
            
            # Post article
            success = post_article()
            
            if success:
                post_count += 1
                error_count = 0  # Reset error count on success
                logger.info(f"✅ Total posts so far: {post_count}")
            else:
                error_count += 1
                logger.warning(f"⚠️ Failed attempts: {error_count}")
                
                # If too many consecutive errors, wait longer
                if error_count >= 3:
                    logger.warning("⚠️ Multiple consecutive failures, extending wait time...")
                    time.sleep(300)  # Wait 5 minutes extra
                    error_count = 0
            
            # Calculate next posting time
            next_post_time = datetime.now().timestamp() + POST_INTERVAL
            next_post_datetime = datetime.fromtimestamp(next_post_time)
            
            if POST_INTERVAL >= 60:
                wait_display = f"{POST_INTERVAL // 60} minutes"
            else:
                wait_display = f"{POST_INTERVAL} seconds"
            
            logger.info(f"⏰ Next post scheduled for: {next_post_datetime.strftime('%H:%M:%S')}")
            logger.info(f"💤 Sleeping for {wait_display}...\n")
            
            # Sleep with keep-alive pings (every 12 minutes)
            keep_alive_during_sleep(POST_INTERVAL, ping_interval=720)
            
        except KeyboardInterrupt:
            logger.info("\n\n⚠️ Received interrupt signal")
            logger.info(f"📊 Total posts made: {post_count}")
            logger.info("👋 Shutting down gracefully...")
            break
            
        except Exception as e:
            logger.error(f"❌ Unexpected error in main loop: {e}")
            import traceback
            traceback.print_exc()
            logger.info("⏰ Waiting 5 minutes before retry...")
            time.sleep(300)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
