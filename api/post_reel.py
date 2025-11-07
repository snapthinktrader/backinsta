"""
Vercel Serverless Function - Post Reel from CockroachDB
Triggered by Vercel Cron every 15 minutes
"""

import os
import sys
import json
from http.server import BaseHTTPRequestHandler

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from cockroach_poster import CockroachDBPoster
from database.cockroach_setup import get_stats

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET request (for manual trigger or health check)"""
        try:
            # Get stats first
            stats = get_stats()
            
            if stats['pending'] == 0:
                # No pending reels
                response = {
                    "success": False,
                    "message": "No pending reels in database",
                    "stats": stats
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Post next reel
            poster = CockroachDBPoster()
            success = poster.post_next_reel()
            
            # Get updated stats
            updated_stats = get_stats()
            
            response = {
                "success": success,
                "message": "Reel posted successfully" if success else "Failed to post reel",
                "stats": updated_stats
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                "success": False,
                "error": str(e)
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_POST(self):
        """Handle POST request (for Vercel Cron)"""
        # Verify it's from Vercel Cron
        auth_header = self.headers.get('Authorization')
        cron_secret = os.getenv('CRON_SECRET')
        
        if cron_secret and auth_header != f"Bearer {cron_secret}":
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode())
            return
        
        # Same logic as GET
        self.do_GET()
