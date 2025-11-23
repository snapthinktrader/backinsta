"""
Generate reels WITHOUT voice narration (for testing 9:16 format)
Save to CockroachDB for Render posting
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import NewsToInstagramPipeline
from database.mongodb_setup import insert_reel, get_stats
from mongo_database import generate_article_id

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LocalReelGeneratorNoVoice:
    """Generate reels locally without voice and save to CockroachDB"""
    
    def __init__(self):
        self.pipeline = NewsToInstagramPipeline()
        logger.info("✅ Pipeline initialized (NO VOICE mode)")
    
    def generate_reel(self, article):
        """Generate a single reel from article (NO VOICE)"""
        try:
            headline = article.get('title', article.get('headline', ''))
            article_url = article.get('url', article.get('web_url', ''))
            article_id = generate_article_id(article_url)
            
            print(f"\n{'='*60}")
            print(f"🎬 Creating reel: {headline[:50]}...")
            print(f"{'='*60}")
            
            # 1. Generate AI analysis
            print("🤖 Generating AI analysis...")
            ai_analysis = self.pipeline.generate_ai_analysis(article)
            
            if not ai_analysis:
                print("❌ Failed to generate AI analysis")
                return None
            
            print(f"✅ Analysis: {ai_analysis[:80]}...")
            
            # 2. Get article image
            print("📥 Getting article image...")
            image_url = self.pipeline.get_article_image_url(article)
            
            if not image_url:
                print("❌ No image found")
                return None
            
            # 3. Create image with text overlay (NOW 1080x1920 for Reels!)
            print("🎨 Creating 9:16 image with text overlay...")
            processed_image_result = self.pipeline.add_text_to_image(
                image_url,
                article.get('title', ''),
                article.get('section', 'News')
            )
            
            if not processed_image_result:
                print("❌ Failed to process image")
                return None
            
            print(f"✅ Image created: 1080x1920 (9:16 Reels format)")
            thumbnail_url = processed_image_result
            
            # 4. Download processed image
            import requests
            import tempfile
            response = requests.get(processed_image_result, timeout=15)
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_img.write(response.content)
            temp_img.close()
            temp_img_path = temp_img.name
            
            # 5. Convert to video (7 seconds, no audio)
            print("🎬 Creating 7s video...")
            video_path = self.pipeline.convert_image_to_video_reel(
                temp_img_path,
                duration=7,
                audio_path=None  # NO VOICE
            )
            
            if not video_path:
                print("❌ Failed to create video")
                os.unlink(temp_img_path)
                return None
            
            # 6. Read video data
            with open(video_path, 'rb') as f:
                video_data = f.read()
            
            file_size = len(video_data)
            duration = 7.0
            
            print(f"✅ Video created: {file_size / (1024*1024):.2f} MB")
            
            # 7. Generate caption
            section = article.get('section', 'News')
            caption = f"📰 Breaking News\n\n{headline}\n\n{ai_analysis[:200]}...\n\n#news #{section.lower()} #breakingnews"
            
            # 8. Save to CockroachDB
            print("💾 Saving to CockroachDB...")
            reel_id = insert_reel(
                headline=headline,
                caption=caption,
                article_url=article_url,
                article_id=article_id,
                video_data=video_data,
                thumbnail_url=thumbnail_url,
                ai_analysis=ai_analysis,
                duration=duration,
                file_size=file_size
            )
            
            # Cleanup
            os.unlink(temp_img_path)
            if os.path.exists(video_path):
                os.unlink(video_path)
            
            print(f"✅ SUCCESS! Reel saved to database")
            print(f"   Reel ID: {reel_id}")
            print(f"   Size: {file_size / (1024*1024):.2f} MB")
            print(f"   Duration: {duration}s")
            print(f"   Format: 1080x1920 (9:16 Reels)")
            
            return reel_id
            
        except Exception as e:
            logger.error(f"❌ Error generating reel: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_batch(self, count=6):
        """Generate multiple reels"""
        print(f"\n{'='*60}")
        print(f"🎬 Starting batch generation: {count} reels (NO VOICE)")
        print(f"{'='*60}")
        
        # Show current stats
        try:
            stats = get_stats()
            print(f"\n📊 Current Database Stats:")
            print(f"   Total reels: {stats['total']}")
            print(f"   Pending: {stats['pending']}")
            print(f"   Posted: {stats['posted']}\n")
        except:
            pass
        
        # Fetch articles from NYT
        sections = ['business', 'technology', 'world']
        all_articles = []
        
        for section in sections:
            if len(all_articles) >= count:
                break
            
            print(f"\n📰 Fetching articles from section: {section}")
            articles = self.pipeline.fetch_nyt_articles(section, limit=12)
            
            if articles:
                print(f"✅ Found {len(articles)} articles")
                all_articles.extend(articles)
            else:
                print(f"⚠️  No articles found in {section}")
        
        if not all_articles:
            print("❌ No articles found")
            return
        
        # Generate reels
        created = 0
        failed = 0
        
        for i, article in enumerate(all_articles[:count]):
            reel_id = self.generate_reel(article)
            
            if reel_id:
                created += 1
            else:
                failed += 1
            
            print(f"\n📊 Progress: {i+1}/{count} | Created: {created} | Failed: {failed}")
        
        # Final stats
        print(f"\n{'='*60}")
        print(f"📊 BATCH COMPLETE")
        print(f"{'='*60}")
        print(f"✅ Created: {created} reels")
        print(f"⚠️  Failed: {failed} reels")
        
        try:
            stats = get_stats()
            print(f"\n📊 Updated Database Stats:")
            print(f"   Total reels: {stats['total']}")
            print(f"   Pending: {stats['pending']}")
            print(f"   Posted: {stats['posted']}")
        except:
            pass

def main():
    print("\n" + "="*60)
    print("🎬 LOCAL REEL GENERATOR (NO VOICE)")
    print("="*60)
    print("Generates 9:16 Reels without voice narration")
    print("Perfect for testing or when ElevenLabs quota is exhausted")
    print("="*60)
    
    count = input("\nHow many reels to generate? (default 6): ")
    count = int(count) if count.strip() else 6
    
    print(f"\n📝 Will generate {count} reels WITHOUT voice narration")
    print(f"✅ Format: 1080x1920 (9:16 for Instagram Reels)")
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("❌ Cancelled")
        return
    
    generator = LocalReelGeneratorNoVoice()
    generator.generate_batch(count)

if __name__ == "__main__":
    main()
