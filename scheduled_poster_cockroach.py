#!/usr/bin/env python3
"""
Scheduled poster for BackInsta - Posts reels from CockroachDB at regular intervals
Simplified version that fetches pre-generated reels from database
"""

import os
import sys
import time
from datetime import datetime
import logging
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import from same directory
from cockroach_poster import CockroachDBPoster
from database.cockroach_setup import get_stats

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simple health check handler for Render
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK - Instagram Auto-Poster Running (CockroachDB Mode)')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress HTTP logs to keep output clean
        pass

def post_next_reel():
    """Fetch and post next pending reel from database"""
    try:
        logger.info("🔄 Fetching next reel from CockroachDB...")
        
        # Create poster
        poster = CockroachDBPoster()
        
        # Post next reel
        success = poster.post_next_reel()
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Error in posting cycle: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main scheduling loop"""
    print("=" * 70)
    print("🚀 Instagram Auto-Poster Starting (CockroachDB Mode)...")
    print("=" * 70)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📦 Reels are pre-generated locally and fetched from database")
    
    # Check posting interval (default 15 minutes)
    interval_minutes = int(os.getenv('POST_INTERVAL_MINUTES', '15'))
    print(f"⏰ Posting interval: {interval_minutes} minutes")
    print("=" * 70)
    print()
    
    # Start health check server in background (for Render web service)
    port = int(os.getenv('PORT', '10000'))
    health_server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    health_thread = Thread(target=health_server.serve_forever, daemon=True)
    health_thread.start()
    logger.info(f"🏥 Health check server started on port {port}")
    
    # Show initial database stats
    try:
        stats = get_stats()
        logger.info(f"📊 Initial Database Stats:")
        logger.info(f"   Total reels: {stats['total']}")
        logger.info(f"   Pending: {stats['pending']}")
        logger.info(f"   Posted: {stats['posted']}")
        logger.info(f"   Failed: {stats['failed']}")
    except Exception as e:
        logger.warning(f"⚠️  Could not get database stats: {e}")
    
    # Post interval in seconds
    POST_INTERVAL = interval_minutes * 60
    logger.info(f"⏰ Posting every {interval_minutes} minutes ({POST_INTERVAL} seconds)")
    
    # Counter for posts
    post_count = 0
    error_count = 0
    
    while True:
        try:
            cycle_start = datetime.now()
            logger.info(f"\n{'='*60}")
            logger.info(f"🔄 Cycle #{post_count + 1} started at {cycle_start.strftime('%H:%M:%S')}")
            logger.info(f"{'='*60}")
            
            # Post next reel
            success = post_next_reel()
            
            if success:
                post_count += 1
                error_count = 0  # Reset error count on success
                logger.info(f"✅ Total posts so far: {post_count}")
            else:
                error_count += 1
                logger.warning(f"⚠️ Failed attempts: {error_count}")
            
            # Show current stats
            try:
                stats = get_stats()
                logger.info(f"📊 Database Stats:")
                logger.info(f"   Pending: {stats['pending']}")
                logger.info(f"   Posted: {stats['posted']}")
                logger.info(f"   Failed: {stats['failed']}")
            except:
                pass
            
            # Calculate next posting time
            next_post_time = datetime.now().timestamp() + POST_INTERVAL
            next_post_datetime = datetime.fromtimestamp(next_post_time)
            
            if POST_INTERVAL >= 60:
                wait_display = f"{POST_INTERVAL // 60} minutes"
            else:
                wait_display = f"{POST_INTERVAL} seconds"
            
            logger.info(f"⏰ Next post scheduled for: {next_post_datetime.strftime('%H:%M:%S')}")
            logger.info(f"💤 Sleeping for {wait_display}...\n")
            
            # Sleep until next cycle
            time.sleep(POST_INTERVAL)
            
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
