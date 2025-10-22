#!/usr/bin/env python3
"""
🎯 BackInsta - News to Instagram Automation Backend
Fetches news articles from Webstory backend and posts to Instagram using QPost
"""

import os
import sys
import json
import time
import requests
import schedule
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Import local modules
from config import Config
from database import BackInstaDB

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NewsToInstagramPipeline:
    """Main pipeline for fetching news and posting to Instagram"""
    
    def __init__(self):
        self.webstory_url = Config.WEBSTORY_API_URL
        self.qpost_url = Config.QPOST_API_URL
        self.access_token = Config.INSTAGRAM_ACCESS_TOKEN
        self.account_id = Config.INSTAGRAM_ACCOUNT_ID
        self.posted_articles = set()  # Track posted articles to avoid duplicates
        
        # Initialize BackInsta tracking database
        self.db = BackInstaDB(Config.MONGODB_URI)
        
        # Initialize Webstory MongoDB connection
        self.webstory_db = None
        self.webstory_client = None
        try:
            from pymongo import MongoClient
            self.webstory_client = MongoClient(Config.WEBSTORY_MONGODB_URI, serverSelectionTimeoutMS=5000, tlsAllowInvalidCertificates=True)
            self.webstory_db = self.webstory_client.webstory
            # Test connection
            self.webstory_client.admin.command('ping')
            logger.info("✅ Connected to Webstory MongoDB")
        except Exception as e:
            logger.warning(f"⚠️ Could not connect to Webstory MongoDB: {e}")
            self.webstory_db = None
        
    def fetch_latest_news(self, section: str = 'home', limit: int = 10) -> List[Dict]:
        """
        Fetch latest news articles from Webstory backend
        
        Args:
            section: News section (home, politics, technology, business, etc.)
            limit: Number of articles to fetch
            
        Returns:
            List of article dictionaries
        """
        try:
            logger.info(f"📰 Fetching {limit} articles from section: {section}")
            
            articles = []
            
            # Try MongoDB first if available
            if self.webstory_db is not None:
                try:
                    logger.info("📊 Fetching from Webstory MongoDB...")
                    
                    # Get list of already posted article URLs from database
                    posted_urls = set()
                    try:
                        if self.db is not None and self.db.collection is not None:
                            posted_docs = self.db.collection.find({}, {'article_url': 1})
                            posted_urls = {doc['article_url'] for doc in posted_docs if 'article_url' in doc}
                            logger.info(f"📋 Found {len(posted_urls)} already posted articles in database")
                    except Exception as e:
                        logger.warning(f"Could not fetch posted URLs: {e}")
                    
                    # Merge with memory cache
                    posted_urls.update(self.posted_articles)
                    
                    query = {}
                    if section and section != 'home':
                        query['section'] = section
                    
                    # Exclude already posted URLs
                    if len(posted_urls) > 0:
                        query['url'] = {'$nin': list(posted_urls)}
                    
                    collection = self.webstory_db.articles
                    # Fetch more than limit to ensure we have enough unique articles
                    cursor = collection.find(query).sort('publishedDate', -1).limit(limit * 3)
                    
                    for doc in cursor:
                        if len(articles) >= limit:
                            break
                        
                        # Convert MongoDB document to dict and clean it
                        article = {
                            'title': doc.get('title', ''),
                            'abstract': doc.get('abstract', ''),
                            'url': doc.get('url', ''),
                            'section': doc.get('section', section),
                            'source': doc.get('source', 'Webstory'),
                            'byline': doc.get('byline', ''),
                            'publishedDate': doc.get('publishedDate', ''),
                            'multimedia': doc.get('multimedia', [])
                        }
                        articles.append(article)
                    
                    if len(articles) > 0:
                        logger.info(f"✅ Fetched {len(articles)} NEW articles from MongoDB")
                    else:
                        logger.warning("⚠️ No new articles found in MongoDB")
                        
                except Exception as e:
                    logger.warning(f"MongoDB fetch failed, trying API: {e}")
                    import traceback
                    traceback.print_exc()
                    articles = []
            
            # Fallback to API endpoints if MongoDB didn't work
            if len(articles) == 0:
                endpoints = [
                    f"{self.webstory_url}/articles/section/{section}?limit={limit}",
                    f"{self.webstory_url}/articles?limit={limit}",
                    f"http://localhost:3001/api/articles/section/{section}?limit={limit}"
                ]
                
                for endpoint in endpoints:
                    try:
                        response = requests.get(endpoint, timeout=10)
                        if response.status_code == 200:
                            articles = response.json()
                            logger.info(f"✅ Fetched {len(articles)} articles from {endpoint}")
                            break
                    except requests.RequestException as e:
                        logger.warning(f"Failed to fetch from {endpoint}: {e}")
                        continue
            
            if len(articles) == 0:
                logger.error("❌ Could not fetch articles from any source")
                return []
            
            # Filter out already posted articles (check both memory and database)
            new_articles = []
            for article in articles:
                url = article.get('url')
                if not url:
                    continue
                
                # Check memory cache
                if url in self.posted_articles:
                    continue
                
                # Check database (if available)
                try:
                    if self.db is not None and self.db.is_already_posted(url):
                        self.posted_articles.add(url)  # Add to memory cache
                        continue
                except:
                    pass  # Continue anyway if DB check fails
                
                new_articles.append(article)
            
            logger.info(f"📊 Found {len(new_articles)} new articles to process")
            return new_articles
            
        except Exception as e:
            logger.error(f"❌ Error fetching news: {e}")
            return []
    
    def generate_ai_analysis(self, article: Dict) -> str:
        """
        Generate AI analysis/commentary for the article
        
        Args:
            article: Article dictionary
            
        Returns:
            AI-generated analysis text
        """
        try:
            # Use Groq API for AI analysis (similar to Webstory)
            import os
            groq_api_key = os.getenv('GROQ_API_KEY')
            
            if not groq_api_key:
                logger.warning("⚠️ GROQ_API_KEY not set, skipping AI analysis")
                return ""
            
            from groq import Groq
            client = Groq(api_key=groq_api_key)
            
            title = article.get('title', '')
            abstract = article.get('abstract', '')
            content = article.get('content', abstract)
            
            prompt = f"""You are a news analyst. Provide a brief, engaging 2-3 sentence analysis of this news article for social media.
Focus on key insights, implications, or interesting angles. Keep it conversational and engaging.

Title: {title}
Summary: {abstract}

Provide ONLY the analysis, no extra labels or formatting:"""
            
            completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert news analyst who provides insightful commentary on current events. Your analysis should be professional, balanced, and informative."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.1-8b-instant",  # Same model as Webstory
                temperature=0.7,
                max_tokens=500
            )
            
            analysis = completion.choices[0].message.content.strip()
            logger.info(f"✅ Generated AI analysis: {analysis[:100]}...")
            return analysis
            
        except Exception as e:
            logger.warning(f"⚠️ Could not generate AI analysis: {e}")
            return ""
    
    def create_instagram_caption(self, article: Dict) -> str:
        """
        Create Instagram-friendly caption from article
        
        Args:
            article: Article dictionary with title, abstract, etc.
            
        Returns:
            Instagram caption string
        """
        title = article.get('title', 'Breaking News')
        abstract = article.get('abstract', '')
        section = article.get('section', 'News')
        url = article.get('url', '')
        
        # Create engaging caption
        caption = f"📰 {title}\n\n"
        
        # Add AI analysis if available
        ai_analysis = self.generate_ai_analysis(article)
        if ai_analysis:
            caption += f"💡 {ai_analysis}\n\n"
        elif abstract:
            # Fallback to abstract if no AI analysis
            max_len = Config.MAX_ABSTRACT_LENGTH
            short_abstract = abstract[:max_len] + "..." if len(abstract) > max_len else abstract
            caption += f"{short_abstract}\n\n"
        
        # Add section hashtag
        section_hashtag = f"#{section.replace(' ', '').replace('-', '')}"
        caption += f"{section_hashtag} #News #BreakingNews #Trending\n\n"
        
        # Replace NYT link with forexyy.com
        forexyy_url = "https://forexyy.com"
        caption += f"🔗 Read more: {forexyy_url}\n"
        caption += f"📱 Follow us for daily news updates!"
        
        # Ensure caption is within Instagram limits
        if len(caption) > Config.MAX_CAPTION_LENGTH:
            caption = caption[:Config.MAX_CAPTION_LENGTH - 20] + "... #News"
        
        return caption
    
    def add_text_to_image(self, image_url: str, title: str, section: str) -> Optional[str]:
        """
        Download image, add text overlay, and return URL to processed image
        
        Args:
            image_url: Original image URL
            title: Article title to overlay
            section: Article section for branding
            
        Returns:
            URL to processed image or original URL if processing fails
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            import io
            import textwrap
            
            # Download image
            response = requests.get(image_url, timeout=15)
            if response.status_code != 200:
                return image_url
            
            img = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create drawing context
            draw = ImageDraw.Draw(img)
            width, height = img.size
            
            # Calculate overlay height (only 25-30% of image for better look)
            # This leaves more image visible
            overlay_height = int(height * 0.28)
            overlay_start = height - overlay_height
            
            # Add semi-transparent overlay at bottom (less opaque for better image visibility)
            overlay = Image.new('RGBA', (width, overlay_height), (0, 0, 0, 180))
            img.paste(overlay, (0, overlay_start), overlay)
            draw = ImageDraw.Draw(img)
            
            # Try to use a nice font, fallback to default
            try:
                # Smaller, more elegant font sizes
                base_font_size = max(28, int(width / 25))
                title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", base_font_size)
                section_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(base_font_size * 0.65))
            except:
                title_font = ImageFont.load_default()
                section_font = title_font
            
            # Wrap title text - shorter lines for better readability
            max_chars = int(width / (base_font_size * 0.6))
            wrapped_title = textwrap.fill(title, width=max_chars)
            
            # Calculate positions with centered content and proper spacing
            padding = 25
            current_y = overlay_start + padding
            
            # 1. Draw section tag at top (smaller, elegant)
            section_text = f"#{section.upper()}"
            draw.text((padding, current_y), section_text, font=section_font, fill=(255, 215, 0))
            current_y += int(base_font_size * 0.9)
            
            # 2. Draw title with better spacing between lines
            title_lines = wrapped_title.split('\n')
            for line in title_lines:
                draw.text((padding, current_y), line, font=title_font, fill=(255, 255, 255))
                current_y += int(base_font_size * 1.15)  # Tighter line spacing
            
            # 4. Draw branding at calculated position (not absolute bottom)
            # 2. Draw title with better spacing between lines
            title_lines = wrapped_title.split('\n')
            for line in title_lines:
                draw.text((padding, current_y), line, font=title_font, fill=(255, 255, 255))
                current_y += int(base_font_size * 1.15)  # Tighter line spacing
            
            # Save to BytesIO
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=95)
            output.seek(0)
            
            # Upload to a temporary storage or return as base64
            # For now, we'll save locally and upload
            import tempfile
            import base64
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file.write(output.getvalue())
            temp_file.close()
            
            # Upload to imgbb or similar service for Instagram
            # For now, return local path - Instagram API needs public URL
            logger.info(f"✅ Created image with text overlay: {temp_file.name}")
            
            # Convert to base64 data URL for Instagram Graph API
            img_data = base64.b64encode(output.getvalue()).decode()
            
            # Note: Instagram Graph API requires publicly accessible URLs
            # We need to upload this to a CDN or image hosting service
            # For now, we'll try to upload to imgbb
            uploaded_url = self.upload_image(output.getvalue())
            return uploaded_url if uploaded_url else image_url
            
        except Exception as e:
            logger.warning(f"⚠️ Could not add text to image: {e}")
            return image_url
    
    def upload_image(self, image_bytes: bytes) -> Optional[str]:
        """Upload image to imgbb or similar free host"""
        try:
            import base64
            
            # Use imgbb API (free tier)
            api_key = Config.IMGBB_API_KEY
            
            if not api_key:
                logger.warning("⚠️ IMGBB_API_KEY not configured, skipping image upload")
                return None
            
            img_b64 = base64.b64encode(image_bytes).decode()
            
            response = requests.post(
                'https://api.imgbb.com/1/upload',
                data={
                    'key': api_key,
                    'image': img_b64
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                url = data['data']['url']
                logger.info(f"✅ Uploaded image to imgbb: {url}")
                return url
            else:
                logger.warning(f"⚠️ Failed to upload to imgbb: {response.text}")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Image upload failed: {e}")
            return None
    
    def get_article_image_url(self, article: Dict) -> Optional[str]:
        """
        Extract image URL from article multimedia
        
        Args:
            article: Article dictionary
            
        Returns:
            Image URL or None
        """
        multimedia = article.get('multimedia', [])
        
        if not multimedia or len(multimedia) == 0:
            logger.warning(f"⚠️ No multimedia found for article: {article.get('title', 'Unknown')}")
            return None
        
        # Try to find a suitable image
        for media in multimedia:
            if media.get('format') in ['superJumbo', 'threeByTwoSmallAt2X', 'Standard Thumbnail']:
                return media.get('url')
        
        # Fallback to first image
        return multimedia[0].get('url') if multimedia else None
    
    def download_and_buffer_image(self, image_url: str, username: str = 'virall_official') -> Optional[str]:
        """
        Download image and store in QPost buffer
        
        Args:
            image_url: URL of the image to download
            username: QPost username
            
        Returns:
            Buffer ID if successful, None otherwise
        """
        try:
            logger.info(f"📥 Downloading image: {image_url[:50]}...")
            
            # Download image
            image_response = requests.get(image_url, timeout=15)
            if image_response.status_code != 200:
                logger.error(f"❌ Failed to download image: {image_response.status_code}")
                return None
            
            # Store in buffer via QPost API
            buffer_endpoint = f"{self.qpost_url}/buffer"
            
            files = {
                'file': ('article_image.jpg', image_response.content, 'image/jpeg')
            }
            data = {
                'username': username,
                'media_type': 'image',
                'original_url': image_url
            }
            
            buffer_response = requests.post(buffer_endpoint, files=files, data=data, timeout=30)
            
            if buffer_response.status_code == 200:
                result = buffer_response.json()
                buffer_id = result.get('buffer_id')
                logger.info(f"✅ Image buffered successfully: {buffer_id}")
                return buffer_id
            else:
                logger.error(f"❌ Failed to buffer image: {buffer_response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error downloading/buffering image: {e}")
            return None
    
    def post_to_instagram_direct(self, image_url: str, caption: str) -> Dict:
        """
        Post directly to Instagram using Graph API
        
        Args:
            image_url: Public URL of the image
            caption: Instagram caption
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            logger.info("📤 Posting to Instagram (direct method)...")
            
            # Step 1: Create media object
            create_url = f"https://graph.facebook.com/v18.0/{self.account_id}/media"
            create_params = {
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token
            }
            
            create_response = requests.post(create_url, params=create_params, timeout=30)
            
            if create_response.status_code != 200:
                logger.error(f"❌ Failed to create media object: {create_response.text}")
                return {'success': False, 'error': 'Failed to create media object'}
            
            creation_id = create_response.json().get('id')
            logger.info(f"✅ Media object created: {creation_id}")
            
            # Step 2: Publish media
            publish_url = f"https://graph.facebook.com/v18.0/{self.account_id}/media_publish"
            publish_params = {
                "creation_id": creation_id,
                "access_token": self.access_token
            }
            
            publish_response = requests.post(publish_url, params=publish_params, timeout=30)
            
            if publish_response.status_code != 200:
                logger.error(f"❌ Failed to publish media: {publish_response.text}")
                return {'success': False, 'error': 'Failed to publish media'}
            
            post_id = publish_response.json().get('id')
            logger.info(f"🎉 Successfully posted to Instagram: {post_id}")
            
            return {
                'success': True,
                'post_id': post_id,
                'instagram_url': f"https://www.instagram.com/p/{post_id}/",
                'creation_id': creation_id
            }
            
        except Exception as e:
            logger.error(f"❌ Error posting to Instagram: {e}")
            return {'success': False, 'error': str(e)}
    
    def post_article_to_instagram(self, article: Dict) -> bool:
        """
        Complete pipeline: prepare and post article to Instagram
        
        Args:
            article: Article dictionary
            
        Returns:
            True if posted successfully, False otherwise
        """
        try:
            article_title = article.get('title', 'Unknown Article')
            logger.info(f"\n🚀 Processing article: {article_title}")
            
            # Get image URL
            image_url = self.get_article_image_url(article)
            
            if not image_url:
                logger.warning("⚠️ No image found, skipping article")
                return False
            
            # Add text overlay to image
            logger.info("🎨 Adding text overlay to image...")
            processed_image_url = self.add_text_to_image(
                image_url,
                article.get('title', ''),
                article.get('section', 'News')
            )
            
            # Create caption
            caption = self.create_instagram_caption(article)
            
            # Try posting with processed image first, fallback to original if it fails
            final_image_url = processed_image_url if processed_image_url else image_url
            result = self.post_to_instagram_direct(final_image_url, caption)
            
            # If posting failed and we used processed image, retry with original
            if not result['success'] and processed_image_url and processed_image_url != image_url:
                logger.warning("⚠️ Processed image rejected, retrying with original image...")
                result = self.post_to_instagram_direct(image_url, caption)
            
            if result['success']:
                # Mark article as posted in memory
                self.posted_articles.add(article.get('url'))
                
                # Save to database (with safe check)
                try:
                    if self.db is not None:
                        self.db.mark_as_posted(article, result)
                except Exception as db_error:
                    logger.warning(f"⚠️ Could not save to database: {db_error}")
                
                logger.info(f"✅ Article posted successfully!")
                logger.info(f"📸 Post ID: {result.get('post_id')}")
                logger.info(f"🔗 Instagram URL: {result.get('instagram_url')}")
                
                return True
            else:
                logger.error(f"❌ Failed to post article: {result.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error in post pipeline: {e}")
            return False
    
    def run_posting_cycle(self, section: str = 'home', max_posts: int = 3):
        """
        Run a complete posting cycle
        
        Args:
            section: News section to fetch from
            max_posts: Maximum number of posts to create in this cycle
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 Starting posting cycle for section: {section}")
        logger.info(f"{'='*60}\n")
        
        # Fetch latest articles
        articles = self.fetch_latest_news(section=section, limit=10)
        
        if not articles:
            logger.warning("⚠️ No articles found to post")
            return
        
        # Post articles (up to max_posts)
        posts_created = 0
        
        for article in articles[:max_posts]:
            if posts_created >= max_posts:
                break
            
            success = self.post_article_to_instagram(article)
            
            if success:
                posts_created += 1
                # Wait between posts to avoid rate limiting
                if posts_created < max_posts:
                    wait_time = Config.POST_INTERVAL_SECONDS
                    logger.info(f"⏳ Waiting {wait_time} seconds before next post...")
                    time.sleep(wait_time)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Posting cycle complete: {posts_created}/{max_posts} posts created")
        
        # Print stats if database available
        if self.db:
            stats = self.db.get_stats()
            logger.info(f"📊 Total posts in database: {stats.get('total_posts', 0)}")
            sections = stats.get('sections', {})
            if sections:
                logger.info("📈 Posts by section:")
                for section, count in sections.items():
                    logger.info(f"   - {section}: {count}")
        
        logger.info(f"{'='*60}\n")


def main():
    """Main entry point"""
    logger.info("🚀 BackInsta - News to Instagram Automation")
    logger.info("=" * 60)
    
    # Print and validate configuration
    Config.print_config()
    
    errors = Config.validate()
    if errors:
        logger.error("\n❌ Configuration Errors:")
        for error in errors:
            logger.error(f"   - {error}")
        logger.error("\nPlease fix configuration in .env file")
        sys.exit(1)
    
    logger.info("✅ Configuration valid\n")
    
    # Initialize pipeline
    pipeline = NewsToInstagramPipeline()
    
    # Run immediate test
    logger.info("📋 Running initial test posting cycle...")
    pipeline.run_posting_cycle(section='technology', max_posts=Config.MAX_POSTS_PER_CYCLE)
    
    # Schedule regular posts
    logger.info("\n⏰ Setting up scheduled posting...")
    
    # Schedule based on configuration
    schedule.every(Config.SCHEDULE_HOME_HOURS).hours.do(
        pipeline.run_posting_cycle, 
        section='home', 
        max_posts=Config.MAX_POSTS_PER_CYCLE
    )
    schedule.every(Config.SCHEDULE_TECH_HOURS).hours.do(
        pipeline.run_posting_cycle, 
        section='technology', 
        max_posts=Config.MAX_POSTS_PER_CYCLE
    )
    schedule.every(Config.SCHEDULE_BUSINESS_HOURS).hours.do(
        pipeline.run_posting_cycle, 
        section='business', 
        max_posts=Config.MAX_POSTS_PER_CYCLE
    )
    
    logger.info("✅ Scheduler configured!")
    logger.info("📅 Schedule:")
    logger.info(f"   - Home section: Every {Config.SCHEDULE_HOME_HOURS} hours ({Config.MAX_POSTS_PER_CYCLE} posts)")
    logger.info(f"   - Technology: Every {Config.SCHEDULE_TECH_HOURS} hours ({Config.MAX_POSTS_PER_CYCLE} posts)")
    logger.info(f"   - Business: Every {Config.SCHEDULE_BUSINESS_HOURS} hours ({Config.MAX_POSTS_PER_CYCLE} posts)")
    
    # Run scheduler
    logger.info("\n🔄 Starting scheduler loop...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("\n\n👋 Shutting down gracefully...")
        if pipeline.db:
            pipeline.db.close()
        logger.info("✅ Goodbye!")
        sys.exit(0)


if __name__ == '__main__':
    main()
