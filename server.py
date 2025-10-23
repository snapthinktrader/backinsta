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
from youtube_shorts import YouTubeShortsUploader

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
        
        # Initialize YouTube Shorts uploader (if enabled)
        self.youtube_uploader = None
        use_youtube = os.getenv('USE_YOUTUBE_SHORTS', 'false').lower() == 'true'
        if use_youtube:
            try:
                self.youtube_uploader = YouTubeShortsUploader()
                logger.info("✅ YouTube Shorts uploader initialized")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize YouTube Shorts uploader: {e}")
        
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
        Fetch latest news articles from NYT API (fresh content)
        
        Args:
            section: News section (home, politics, technology, business, etc.)
            limit: Number of articles to fetch
            
        Returns:
            List of article dictionaries
        """
        try:
            logger.info(f"📰 Fetching {limit} FRESH articles from NYT API for section: {section}")
            
            # Get NYT API key from environment
            nyt_api_key = os.getenv('NYT_API_KEY', 'LAi7B0DrisIZ7g0xD8t5NvjqjHGUfRri')
            
            # Map sections to NYT API sections
            nyt_section_map = {
                'home': 'home',
                'technology': 'technology',
                'business': 'business',
                'politics': 'politics',
                'sports': 'sports',
                'entertainment': 'arts'
            }
            
            nyt_section = nyt_section_map.get(section, 'home')
            
            # Fetch from NYT API
            nyt_url = f"https://api.nytimes.com/svc/topstories/v2/{nyt_section}.json?api-key={nyt_api_key}"
            
            try:
                logger.info(f"� Fetching from NYT API: {nyt_section}")
                response = requests.get(nyt_url, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    nyt_articles = data.get('results', [])
                    
                    # Get list of already posted article IDs and URLs
                    posted_urls = set()
                    posted_article_ids = set()
                    try:
                        if self.db is not None and self.db.collection is not None:
                            posted_docs = self.db.collection.find({}, {'article_url': 1, 'article_id': 1})
                            for doc in posted_docs:
                                if 'article_url' in doc:
                                    posted_urls.add(doc['article_url'])
                                if 'article_id' in doc:
                                    posted_article_ids.add(doc['article_id'])
                            logger.info(f"📋 Found {len(posted_urls)} already posted articles in database")
                    except Exception as e:
                        logger.warning(f"Could not fetch posted URLs: {e}")
                    
                    # Merge with memory cache
                    posted_urls.update(self.posted_articles)
                    
                    # Convert NYT articles to our format and filter out posted ones
                    articles = []
                    for nyt_article in nyt_articles:
                        url = nyt_article.get('url', '')
                        title = nyt_article.get('title', '')
                        
                        # Generate article ID to check for duplicates based on title
                        from database import generate_article_id
                        article_id = generate_article_id(title=title, url=url)
                        
                        # Skip if already posted (check both URL and article ID)
                        if url in posted_urls or article_id in posted_article_ids:
                            continue
                        
                        # Convert multimedia
                        multimedia = []
                        if nyt_article.get('multimedia'):
                            for media in nyt_article['multimedia']:
                                multimedia.append({
                                    'url': media.get('url', ''),
                                    'format': media.get('format', 'Standard Thumbnail'),
                                    'type': media.get('type', 'image')
                                })
                        
                        article = {
                            'article_id': article_id,  # ✅ ADD article_id to article dict
                            'title': nyt_article.get('title', ''),
                            'abstract': nyt_article.get('abstract', ''),
                            'url': url,
                            'section': nyt_article.get('section', section),
                            'source': 'New York Times',
                            'byline': nyt_article.get('byline', ''),
                            'published_date': nyt_article.get('published_date', ''),
                            'multimedia': multimedia
                        }
                        
                        articles.append(article)
                        
                        if len(articles) >= limit:
                            break
                    
                    logger.info(f"✅ Fetched {len(articles)} FRESH articles from NYT API")
                    logger.info(f"📊 Found {len(articles)} new articles to process")
                    return articles
                else:
                    logger.error(f"❌ NYT API returned status {response.status_code}")
                    
            except Exception as e:
                logger.error(f"❌ Failed to fetch from NYT API: {e}")
            
            logger.error("❌ Could not fetch articles from NYT API")
            return []
            
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
            
            # Handle EXIF orientation and strip metadata
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)  # Auto-rotate based on EXIF
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            original_width, original_height = img.size
            
            # Convert landscape images to portrait by cropping to 4:5 ratio (Instagram portrait)
            if original_width > original_height:
                logger.info(f"🔄 Converting landscape image ({original_width}x{original_height}) to portrait...")
                
                # Calculate target dimensions for 4:5 portrait ratio
                # Keep the height, calculate new width
                target_height = original_height
                target_width = int(target_height * 0.8)  # 4:5 ratio
                
                # If calculated width is larger than original, adjust based on width
                if target_width > original_width:
                    target_width = original_width
                    target_height = int(target_width * 1.25)  # 5:4 ratio
                
                # Crop from center
                left = (original_width - target_width) // 2
                top = (original_height - target_height) // 2
                right = left + target_width
                bottom = top + target_height
                
                img = img.crop((left, top, right, bottom))
                
                # Upscale to Instagram's recommended portrait size (1080x1350)
                img = img.resize((1080, 1350), Image.Resampling.LANCZOS)
                width, height = img.size
                logger.info(f"✅ Cropped and upscaled to portrait: {width}x{height}")
            else:
                # For portrait/square images, just ensure good resolution
                width, height = img.size
                if width < 1080 or height < 1350:
                    # Upscale maintaining aspect ratio
                    scale = max(1080/width, 1350/height)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    width, height = img.size
                    logger.info(f"✅ Upscaled to {width}x{height} for better quality")
            
            # Create drawing context
            draw = ImageDraw.Draw(img)
            
            # Calculate positions with centered content and proper spacing
            padding = 30  # Increased padding
            small_margin = 8  # extra margin inside overlay

            # Define overlay size bounds (as fractions of image height)
            min_overlay_ratio = 0.12  # at least 12% of image height
            max_overlay_ratio = 0.25  # at most 25% of image height (reduced to show more image)
            min_overlay_px = int(height * min_overlay_ratio)
            max_overlay_px = int(height * max_overlay_ratio)

            # Start with a smaller font size for compact overlay
            base_font_size = max(60, int(width / 15))  # Reduced from width/10 to width/15
            
            # Function to get cross-platform font
            def get_font(size):
                """Try to load a good quality font across different platforms"""
                font_paths = [
                    # macOS
                    "/System/Library/Fonts/Helvetica.ttc",
                    "/System/Library/Fonts/SFNSDisplay.ttf",
                    # Linux (Ubuntu/Debian)
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                    # Alternative Linux paths
                    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
                    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
                ]
                
                for font_path in font_paths:
                    try:
                        font = ImageFont.truetype(font_path, size)
                        logger.info(f"✅ Using font: {font_path} (size: {size}px)")
                        return font
                    except:
                        continue
                
                # Fallback to default font with size
                logger.warning(f"⚠️ No TrueType font found, using default font")
                try:
                    # Try to use default with size parameter (Pillow 10+)
                    return ImageFont.load_default(size=size)
                except:
                    # Older Pillow versions
                    return ImageFont.load_default()
            
            # Function to wrap text and return layout metrics
            def wrap_and_check_fit(font_size):
                title_font = get_font(font_size)
                section_font = get_font(int(font_size * 0.7))
                
                # Wrap title text using actual font measurements
                available_width = width - (2 * padding)
                
                # Smart text wrapping - split into lines that fit
                words = title.split()
                lines = []
                current_line = []
                
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    bbox = draw.textbbox((0, 0), test_line, font=title_font)
                    text_width = bbox[2] - bbox[0]
                    
                    if text_width <= available_width:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                        else:
                            lines.append(word)
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                # Calculate total height needed for overlay content (including padding)
                section_height = int(font_size * 0.9)  # Section tag height
                title_height = len(lines) * int(font_size * 1.15)  # All title lines
                content_height = section_height + title_height
                total_height = content_height + (2 * padding) + small_margin

                return title_font, section_font, lines, total_height
            
            # Try decreasing font sizes until content height fits within max_overlay_px.
            # Enforce a minimum readable font size (reduced for 25% overlay)
            MIN_READABLE_FONT = 45  # Reduced from 70px to fit in 25% overlay
            chosen_font = None
            chosen_lines = None
            chosen_content_height = None
            for attempt_size in range(base_font_size, MIN_READABLE_FONT - 1, -2):  # Stop at min readable
                title_font, section_font, title_lines, required_total = wrap_and_check_fit(attempt_size)
                # If required overlay height fits within maximum allowed, choose it
                if required_total <= max_overlay_px:
                    chosen_font = attempt_size
                    chosen_lines = title_lines
                    chosen_content_height = required_total
                    break
            if chosen_font is None:
                # Use minimum readable font even if it's slightly large
                chosen_font = MIN_READABLE_FONT
                title_font, section_font, chosen_lines, chosen_content_height = wrap_and_check_fit(chosen_font)
                logger.info(f"⚠️ Using minimum font {MIN_READABLE_FONT}px - overlay may exceed ideal size")
                logger.warning("⚠️ Text is long; using minimum font and allowing overlay to hit max height")

            # Compute final overlay height tightly based on content, clamped between min and max
            overlay_height = max(min_overlay_px, min(chosen_content_height, max_overlay_px))
            overlay_start = height - overlay_height
            logger.info(f"🔧 Font size: {chosen_font}px for {len(chosen_lines)} lines")
            logger.info(f"🔧 Computed overlay height: {overlay_height}px (content needed: {chosen_content_height}px)")

            # Load final fonts for rendering
            title_font = get_font(chosen_font)
            section_font = get_font(int(chosen_font * 0.7))

            # No black overlay - text will be directly on image with outline/shadow for readability
            # Convert to RGBA for transparency support
            img = img.convert('RGBA')
            
            # Create a transparent overlay layer for drawing text
            txt_layer = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)

            # Function to draw text with outline for better readability on any background
            def draw_text_with_outline(xy, text, font, fill_color, outline_color=(0, 0, 0, 255), outline_width=3):
                x, y = xy
                # Draw outline
                for adj_x in range(-outline_width, outline_width + 1):
                    for adj_y in range(-outline_width, outline_width + 1):
                        if adj_x != 0 or adj_y != 0:
                            draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_color)
                # Draw main text
                draw.text((x, y), text, font=font, fill=fill_color)

            # Calculate starting position for text at bottom
            overlay_start = height - overlay_height
            current_y = overlay_start + padding
            
            # 1. Draw section tag at top (smaller, elegant) with outline
            section_text = f"#{section.upper()}"
            draw_text_with_outline((padding, current_y), section_text, section_font, (255, 215, 0, 255))
            current_y += int(base_font_size * 0.9)
            
            # 2. Draw title with better spacing between lines and outline
            wrapped_title = '\n'.join(chosen_lines)
            title_lines = wrapped_title.split('\n')
            for line in title_lines:
                draw_text_with_outline((padding, current_y), line, title_font, (255, 255, 255, 255))
                current_y += int(base_font_size * 1.15)  # Tighter line spacing
            
            # 3. Add forexyy.com logo watermark in top-right corner
            try:
                logo_path = os.path.join(os.path.dirname(__file__), 'forexyy_logo.png')
                if os.path.exists(logo_path):
                    logo = Image.open(logo_path).convert('RGBA')
                    # Resize logo to be 15% of image width, maintaining aspect ratio
                    logo_width = int(width * 0.15)
                    logo_ratio = logo_width / logo.width
                    logo_height = int(logo.height * logo_ratio)
                    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                    
                    # Position in top-right corner with some padding
                    logo_x = width - logo_width - 20
                    logo_y = 20
                    txt_layer.paste(logo, (logo_x, logo_y), logo)
                    logger.info(f"✅ Added forexyy.com logo watermark: {logo_width}x{logo_height}px")
                else:
                    logger.warning(f"⚠️ Logo not found at {logo_path}")
            except Exception as e:
                logger.warning(f"⚠️ Could not add logo watermark: {e}")
            
            # Composite the text layer onto the image
            img = Image.alpha_composite(img, txt_layer)
            # Convert back to RGB for JPEG
            img = img.convert('RGB')
            
            # Save to BytesIO with maximum quality for sharp text
            output = io.BytesIO()
            # Strip EXIF and save with MAXIMUM quality (100 for sharpest text)
            img.save(output, format='JPEG', quality=100, optimize=False, subsampling=0, exif=b'')
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
            
            if uploaded_url:
                logger.info(f"✅ Text overlay image uploaded successfully: {uploaded_url}")
                return uploaded_url
            else:
                logger.warning("⚠️ Failed to upload overlay image, using original image instead")
                return image_url
            
        except Exception as e:
            logger.error(f"❌ Could not add text to image: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return image_url
    
    def upload_image(self, image_bytes: bytes) -> Optional[str]:
        """Upload image to imgur or imgbb (imgur first, more Instagram-compatible)"""
        import base64
        
        # Try imgur first (more Instagram-compatible)
        try:
            logger.info(f"📤 Uploading to imgur (size: {len(image_bytes)} bytes)...")
            headers = {'Authorization': 'Client-ID 546c25a59c58ad7'}  # Public anonymous client
            img_b64 = base64.b64encode(image_bytes).decode()
            
            response = requests.post(
                'https://api.imgur.com/3/image',
                headers=headers,
                data={'image': img_b64},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                url = data['data']['link']
                logger.info(f"✅ Uploaded to imgur: {url}")
                return url
            else:
                logger.warning(f"⚠️ imgur upload failed (HTTP {response.status_code}): {response.text}")
        except Exception as imgur_error:
            logger.warning(f"⚠️ imgur upload exception: {str(imgur_error)}")
            
        # Fallback: Try imgbb
        try:
            api_key = Config.IMGBB_API_KEY
            
            if api_key:
                logger.info(f"📤 Trying imgbb as fallback (size: {len(image_bytes)} bytes)...")
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
                    logger.info(f"✅ Uploaded to imgbb: {url}")
                    return url
                else:
                    logger.error(f"❌ imgbb upload failed (HTTP {response.status_code}): {response.text}")
            else:
                logger.warning("⚠️ IMGBB_API_KEY not configured for fallback")
            
            return None
                
        except Exception as e:
            logger.error(f"❌ Image upload exception: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
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
    
    def convert_image_to_video_reel(self, image_path: str, duration: int = 7) -> Optional[str]:
        """
        Convert static image to video Reel with zoom animation and background music
        
        Args:
            image_path: Path to the image file
            duration: Video duration in seconds (default 7)
            
        Returns:
            Path to created video file or None if failed
        """
        try:
            # MoviePy v2.x uses different import path
            try:
                from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip
            except ImportError:
                # Fallback for older MoviePy versions
                from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip
            
            import numpy as np
            import tempfile
            from audio_config import get_audio_path, USE_AUDIO
            
            logger.info(f"🎬 Converting image to {duration}s video Reel (static)...")
            
            # Create image clip
            clip = ImageClip(image_path, duration=duration)
            
            # Set video dimensions (1080x1920 for Reels - 9:16 aspect ratio)
            w, h = 1080, 1920
            
            # Resize to fill the Reel dimensions (static, no zoom)
            video_clip = clip.resized((w, h))
            
            # Try to add background music if available
            final_clip = video_clip
            if USE_AUDIO:
                try:
                    audio_path = get_audio_path()
                    if audio_path and os.path.exists(audio_path):
                        logger.info(f"🎵 Adding background music: {audio_path}")
                        audio = AudioFileClip(audio_path)
                        
                        # Loop or trim audio to match video duration
                        if audio.duration < duration:
                            # Loop audio
                            loops_needed = int(duration / audio.duration) + 1
                            audio = CompositeAudioClip([audio] * loops_needed).subclipped(0, duration)
                        else:
                            # Trim audio
                            audio = audio.subclipped(0, duration)
                        
                        # Set audio to video
                        final_clip = video_clip.with_audio(audio)
                        logger.info(f"✅ Added {duration}s background music to Reel")
                    else:
                        logger.info("ℹ️ No background audio found, creating silent Reel")
                        logger.info("💡 Tip: Add trending music manually via Instagram app for better reach")
                except Exception as audio_error:
                    logger.warning(f"⚠️ Could not add audio: {audio_error}")
                    final_clip = video_clip
            else:
                logger.info("ℹ️ Creating silent Reel (set USE_BACKGROUND_AUDIO=true to enable)")
                logger.info("💡 Recommendation: Post silent Reels and add Instagram trending sounds via app")
            
            # Export video
            temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            temp_video.close()
            
            final_clip.write_videofile(
                temp_video.name,
                fps=30,
                codec='libx264',
                audio_codec='aac' if hasattr(final_clip, 'audio') and final_clip.audio else None,
                logger=None,  # Suppress moviepy logs
                preset='ultrafast'  # Faster encoding
            )
            
            logger.info(f"✅ Created video Reel: {temp_video.name}")
            return temp_video.name
            
        except Exception as e:
            logger.error(f"❌ Failed to create video Reel: {e}")
            import traceback
            logger.error(traceback.format_exc())
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

            # Ensure the image URL is reachable and likely downloadable by Instagram
            def ensure_image_accessible(url: str) -> str:
                """Return a public image URL that Instagram can fetch. If the provided
                URL is unreachable or too large, download, recompress and re-upload it
                via our upload_image() helper and return that new URL."""
                try:
                    head = requests.head(url, timeout=10, allow_redirects=True)
                except Exception:
                    head = None

                if head is None or head.status_code != 200:
                    logger.warning(f"⚠️ Image URL not reachable (HEAD): {url} - will reupload")
                else:
                    ctype = head.headers.get('Content-Type', '')
                    clen = head.headers.get('Content-Length')
                    if not ctype.startswith('image'):
                        logger.warning(f"⚠️ Image URL Content-Type not image: {ctype} - will reupload")
                    else:
                        # If content-length exists and is < 8MB, trust it
                        try:
                            if clen and int(clen) < 8 * 1024 * 1024:
                                logger.info("✅ Image URL looks reachable and small enough for Instagram")
                                return url
                        except Exception:
                            pass

                # Download image, recompress/rescale and reupload
                try:
                    r = requests.get(url, timeout=15)
                    r.raise_for_status()
                    img = Image.open(io.BytesIO(r.content)).convert('RGB')
                    # Ensure portrait crop size used previously (fit within 1080x1350)
                    img.thumbnail((1080, 1350), Image.Resampling.LANCZOS)
                    out = io.BytesIO()
                    img.save(out, format='JPEG', quality=90, optimize=True, subsampling=0)
                    out.seek(0)
                    new_url = self.upload_image(out.getvalue())
                    if new_url:
                        logger.info(f"✅ Reuploaded optimized image for Instagram: {new_url}")
                        return new_url
                    else:
                        logger.error("❌ Reupload failed - will fallback to original URL")
                        return url
                except Exception as e:
                    logger.error(f"❌ Could not reupload image: {e}")
                    return url

            final_image_url = ensure_image_accessible(image_url)

            # Attempt to create and publish media with retries and backoff
            create_url = f"https://graph.facebook.com/v18.0/{self.account_id}/media"
            publish_url = f"https://graph.facebook.com/v18.0/{self.account_id}/media_publish"

            # Detect if it's a video (Reel) or image
            is_video = final_image_url.lower().endswith(('.mp4', '.mov', '.avi'))
            media_type = "VIDEO" if is_video else "IMAGE"
            logger.info(f"📹 Detected media type: {media_type}")

            # Single attempt only - no retries to avoid duplicate media objects
            max_attempts = 1
            creation_id = None
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.info(f"🔁 Media creation attempt {attempt} for URL: {final_image_url}")
                    
                    # Different parameters for video vs image
                    if is_video:
                        create_params = {
                            "media_type": "REELS",
                            "video_url": final_image_url,
                            "caption": caption,
                            "access_token": self.access_token
                        }
                    else:
                        create_params = {
                            "image_url": final_image_url,
                            "caption": caption,
                            "access_token": self.access_token
                        }
                    
                    create_response = requests.post(create_url, params=create_params, timeout=30)
                    if create_response.status_code == 200:
                        creation_id = create_response.json().get('id')
                        logger.info(f"✅ Media object created: {creation_id}")
                        break
                    else:
                        logger.warning(f"⚠️ Create media failed (HTTP {create_response.status_code}): {create_response.text}")
                        # Don't retry - just fail and let the next cycle try again
                        break
                except Exception as e:
                    logger.warning(f"⚠️ Exception creating media (attempt {attempt}): {e}")
                    break

            if not creation_id:
                logger.error("❌ Could not create media object after retries")
                return {'success': False, 'error': 'Failed to create media object after retries'}

            # Wait for Instagram to process the image
            logger.info("⏳ Waiting 10 seconds for Instagram to process the image...")
            time.sleep(10)

            # Publish media (single attempt only to avoid duplicates)
            try:
                publish_params = {
                    "creation_id": creation_id,
                    "access_token": self.access_token
                }
                publish_response = requests.post(publish_url, params=publish_params, timeout=30)
                if publish_response.status_code == 200:
                    post_id = publish_response.json().get('id')
                    logger.info(f"🎉 Successfully posted to Instagram: {post_id}")
                    return {
                        'success': True,
                        'post_id': post_id,
                        'instagram_url': f"https://www.instagram.com/p/{post_id}/",
                        'creation_id': creation_id
                    }
                else:
                    logger.warning(f"⚠️ Publish failed (HTTP {publish_response.status_code}): {publish_response.text}")
                    # Check if rate limited
                    error_text = publish_response.text
                    if 'rate limit' in error_text.lower() or '"code":4' in error_text or publish_response.status_code == 403:
                        logger.warning("⚠️ Instagram rate limited - will retry in next cycle")
                    return {'success': False, 'error': error_text, 'creation_id': creation_id}
            except Exception as e:
                logger.warning(f"⚠️ Exception publishing media: {e}")
                return {'success': False, 'error': str(e), 'creation_id': creation_id}

            logger.error("❌ Failed to publish media")
            return {'success': False, 'error': 'Failed to publish media after retries'}

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
            # ✅ SAFETY CHECK: Ensure article_id is present
            if 'article_id' not in article:
                from database import generate_article_id
                article['article_id'] = generate_article_id(
                    title=article.get('title', ''),
                    url=article.get('url', '')
                )
                logger.info(f"🔖 Generated article_id: {article['article_id']}")
            
            article_title = article.get('title', 'Unknown Article')
            logger.info(f"\n🚀 Processing article: {article_title}")
            logger.info(f"🔖 Article ID: {article.get('article_id')}")
            
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
            
            # Option to convert to Reel (currently disabled - enable by setting env var)
            use_reels = os.getenv('USE_INSTAGRAM_REELS', 'false').lower() == 'true'
            video_path = None
            temp_img_path = None
            
            if use_reels and processed_image_url:
                logger.info("🎬 Converting to Instagram Reel...")
                # Download the processed image first
                try:
                    import tempfile
                    img_response = requests.get(processed_image_url, timeout=15)
                    if img_response.status_code == 200:
                        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                        temp_img.write(img_response.content)
                        temp_img.close()
                        temp_img_path = temp_img.name
                        logger.info(f"✅ Downloaded image to: {temp_img_path}")
                        
                        # Convert to video Reel
                        logger.info("🎬 Converting image to 7s video Reel (static)...")
                        video_path = self.convert_image_to_video_reel(temp_img_path, duration=7)
                        
                        if video_path:
                            logger.info(f"✅ Created video Reel: {video_path} (size: {os.path.getsize(video_path)} bytes)")
                            # Upload video to hosting service
                            with open(video_path, 'rb') as vf:
                                video_url = self.upload_image(vf.read())  # imgbb supports videos
                                
                            if video_url:
                                logger.info(f"✅ Reel created and uploaded: {video_url}")
                                final_image_url = video_url
                            else:
                                logger.warning("⚠️ Failed to upload Reel, using image")
                                final_image_url = processed_image_url
                            
                            # Don't cleanup yet - we might need the video for YouTube
                            logger.info(f"📹 Video saved for YouTube: {video_path}")
                        else:
                            logger.warning("⚠️ Failed to create Reel (returned None), using image")
                            final_image_url = processed_image_url
                            video_path = None
                    else:
                        logger.warning(f"⚠️ Failed to download image (HTTP {img_response.status_code}), skipping video creation")
                        final_image_url = processed_image_url
                        video_path = None
                except Exception as reel_error:
                    logger.error(f"❌ Reel creation exception: {reel_error}, using image", exc_info=True)
                    final_image_url = processed_image_url if processed_image_url else image_url
                    video_path = None
            else:
                logger.info(f"ℹ️ Skipping video creation: use_reels={use_reels}, processed_image_url={bool(processed_image_url)}")
                final_image_url = processed_image_url if processed_image_url else image_url
            
            # Create caption with AI analysis
            caption = self.create_instagram_caption(article)
            
            # Extract AI analysis for YouTube (it's the first part of the caption before hashtags)
            ai_analysis = self.generate_ai_analysis(article)
            
            # Post with processed image (don't retry with original to avoid duplicates)
            final_image_url = processed_image_url if processed_image_url else image_url
            result = self.post_to_instagram_direct(final_image_url, caption)
            
            instagram_success = result['success']
            youtube_success = False
            
            # Check if Instagram failure was due to rate limiting (error code 4 or 403)
            instagram_rate_limited = False
            if not instagram_success:
                error_msg = str(result.get('error', ''))
                if 'rate limit' in error_msg.lower() or 'code":4' in error_msg or 'HTTP 403' in error_msg:
                    instagram_rate_limited = True
                    logger.warning("⚠️ Instagram is rate limited - marking article as attempted to prevent re-posting")
                    # Mark article as posted in memory to prevent immediate retry
                    self.posted_articles.add(article.get('url'))
            
            if instagram_success:
                # Mark article as posted in memory
                self.posted_articles.add(article.get('url'))
                
                # Save to database (with safe check)
                try:
                    if self.db is not None:
                        self.db.mark_as_posted(article, result)
                except Exception as db_error:
                    logger.warning(f"⚠️ Could not save to database: {db_error}")
                
                logger.info(f"✅ Article posted to Instagram successfully!")
                logger.info(f"📸 Instagram Post ID: {result.get('post_id')}")
                logger.info(f"🔗 Instagram URL: {result.get('instagram_url')}")
            else:
                logger.warning(f"⚠️ Instagram posting failed: {result.get('error')}")
                logger.info("🎬 Continuing with YouTube Shorts anyway...")
            
            # ALWAYS attempt YouTube if enabled and we have a video (independent of Instagram)
            logger.info(f"🔍 YouTube check: uploader={bool(self.youtube_uploader)}, use_reels={use_reels}, video_path={video_path}, exists={os.path.exists(video_path) if video_path else False}")
            if self.youtube_uploader and use_reels and video_path and os.path.exists(video_path):
                try:
                    logger.info("\n🎬 Uploading to YouTube Shorts...")
                    youtube_result = self.youtube_uploader.create_short_from_article(
                        video_path=video_path,
                        article=article,
                        ai_analysis=ai_analysis  # Pass AI analysis to YouTube
                    )
                    
                    if youtube_result.get('success'):
                        youtube_success = True
                        logger.info(f"✅ YouTube Short uploaded successfully!")
                        logger.info(f"📹 YouTube Video ID: {youtube_result.get('video_id')}")
                        logger.info(f"🔗 YouTube URL: {youtube_result.get('video_url')}")
                        
                        # Save YouTube info to database
                        try:
                            if self.db is not None:
                                # If Instagram succeeded, update existing record
                                if instagram_success:
                                    self.db.posts.update_one(
                                        {'article_url': article.get('url')},
                                        {'$set': {
                                            'youtube_video_id': youtube_result.get('video_id'),
                                            'youtube_url': youtube_result.get('video_url'),
                                            'youtube_posted_at': datetime.utcnow()
                                        }}
                                    )
                                else:
                                    # If Instagram failed, create new record for YouTube only
                                    self.db.mark_as_posted(article, {
                                        'success': True,
                                        'youtube_video_id': youtube_result.get('video_id'),
                                        'youtube_url': youtube_result.get('video_url'),
                                        'youtube_posted_at': datetime.utcnow()
                                    })
                                    self.posted_articles.add(article.get('url'))
                        except Exception as db_error:
                            logger.warning(f"⚠️ Could not save YouTube info to database: {db_error}")
                    else:
                        logger.warning(f"⚠️ YouTube upload failed: {youtube_result.get('error')}")
                except Exception as yt_error:
                    logger.warning(f"⚠️ YouTube Shorts upload error: {yt_error}")
            
            # Cleanup temporary files
            try:
                if video_path and os.path.exists(video_path):
                    os.unlink(video_path)
                if temp_img_path and os.path.exists(temp_img_path):
                    os.unlink(temp_img_path)
            except Exception as cleanup_error:
                logger.warning(f"⚠️ Cleanup error: {cleanup_error}")
            
            # Consider success if either platform succeeded
            if instagram_success or youtube_success:
                if instagram_success and youtube_success:
                    logger.info("🎉 Multi-platform success: Posted to both Instagram and YouTube!")
                elif instagram_success:
                    logger.info("✅ Posted to Instagram (YouTube not configured or failed)")
                elif youtube_success:
                    logger.info("✅ Posted to YouTube (Instagram failed but YouTube succeeded)")
                return True
            else:
                logger.error(f"❌ Both platforms failed")
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
