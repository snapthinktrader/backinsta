"""
Local Reel Generator
Fetches articles, generates voice narration, creates videos, and saves to CockroachDB
Run this locally on your Mac to batch create 12-15 reels
"""

import os
import sys
import tempfile
from datetime import datetime
from dotenv import load_dotenv

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from server import NewsToInstagramPipeline
import database.cockroach_setup as cockroach_db
from google_tts_voice import GoogleTTSVoice

# Load environment
load_dotenv()

class LocalReelGenerator:
    """Generate reels locally and save to CockroachDB"""
    
    def __init__(self):
        self.pipeline = NewsToInstagramPipeline()
        self.google_tts = GoogleTTSVoice()  # Initialize Google TTS
        self.created_count = 0
        self.failed_count = 0
        
    def generate_reel(self, article):
        """
        Generate a single reel from an article
        
        Args:
            article: Article data from NYT API
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            headline = article.get('title', 'Untitled')
            article_url = article.get('url', '')
            article_id = article.get('article_id', '')
            
            print(f"\n{'='*60}")
            print(f"🎬 Creating reel: {headline[:50]}...")
            print(f"{'='*60}")
            
            # ✅ CHECK IF REEL ALREADY EXISTS BEFORE GENERATING (saves resources!)
            print("🔍 Checking if reel already exists...")
            if cockroach_db.reel_exists(article_id):
                print(f"⏭️  Skipping duplicate: {headline[:60]}...")
                print("   (Reel with this article_id already in database)")
                return False
            
            # Step 1: Generate AI analysis
            print("🤖 Generating AI analysis...")
            ai_analysis = self.pipeline.generate_ai_analysis(article)
            if not ai_analysis:
                print("❌ Failed to generate AI analysis")
                return False
            print(f"✅ Analysis: {ai_analysis[:80]}...")
            
            # Step 2: Generate voice narration with Google TTS
            print("🎤 Generating voice narration with Google TTS...")
            
            # Create narration text (headline + analysis)
            narration_text = f"{headline}. {ai_analysis}"
            
            # Generate voice using Google TTS (Studio-O female voice)
            voice_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            voice_temp.close()
            
            voice_audio_path = self.google_tts.generate_voice(
                text=narration_text,
                output_path=voice_temp.name,
                voice_name="en-US-Studio-O"  # Studio quality female news voice
            )
            
            if not voice_audio_path:
                print("❌ Failed to generate voice narration")
                return False
            print(f"✅ Voice generated: {voice_audio_path}")
            
            # Step 3: Get article image
            print("📥 Getting article image...")
            image_url = self.pipeline.get_article_image_url(article)
            if not image_url:
                print("❌ Failed to get article image")
                return False
            
            # Step 4: Create image with text overlay
            print("🎨 Creating image with text overlay...")
            processed_image_result = self.pipeline.add_text_to_image(
                image_url,
                article.get('title', ''),
                article.get('section', 'News')
            )
            
            # Handle both dict and string returns
            if isinstance(processed_image_result, dict):
                thumbnail_url = processed_image_result.get('url')
                temp_img_path = processed_image_result.get('local_path')
            else:
                thumbnail_url = processed_image_result
                temp_img_path = None
            
            if not temp_img_path or not os.path.exists(temp_img_path):
                print("❌ Failed to create local image file")
                return False
            
            print(f"✅ Image created: {temp_img_path}")
            print(f"✅ Thumbnail: {thumbnail_url}")
            
            # Step 5: Convert to video with voice
            print("🎬 Creating video reel with voice...")
            video_path = self.pipeline.convert_image_to_video_reel(
                temp_img_path,
                duration=7,
                audio_path=voice_audio_path
            )
            
            if not video_path or not os.path.exists(video_path):
                print("❌ Failed to create video")
                return False
            
            # Get video info
            file_size = os.path.getsize(video_path)
            file_size_mb = file_size / (1024 * 1024)
            print(f"✅ Video created: {file_size_mb:.2f} MB")
            
            # Get duration from audio
            try:
                from moviepy import AudioFileClip
                audio = AudioFileClip(voice_audio_path)
                duration = audio.duration
                audio.close()
            except:
                duration = 7.0  # Default
            
            # Step 6: Read video data
            print("📦 Reading video data...")
            with open(video_path, 'rb') as f:
                video_data = f.read()
            
            # Step 7: Generate caption
            # Create caption with AI analysis
            caption_parts = [
                ai_analysis,
                "",
                f"📰 Read more: {article_url}",
                "",
                "#news #breakingnews #trending #viral #reels #instareels"
            ]
            caption = "\n".join(caption_parts)
            
            # Step 8: Save to CockroachDB
            print("💾 Saving to CockroachDB...")
            reel_id = cockroach_db.insert_reel(
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
            
            if reel_id:
                print(f"✅ SUCCESS! Reel saved to database: {reel_id}")
                print(f"   Duration: {duration:.1f}s")
                print(f"   Size: {file_size_mb:.2f} MB")
                self.created_count += 1
                
                # Cleanup temp files
                try:
                    if os.path.exists(temp_img_path):
                        os.unlink(temp_img_path)
                    if os.path.exists(video_path):
                        os.unlink(video_path)
                    if os.path.exists(voice_audio_path):
                        os.unlink(voice_audio_path)
                except:
                    pass
                
                return True
            else:
                print("⚠️  Reel already exists in database (skipped)")
                return False
                
        except Exception as e:
            print(f"❌ Error creating reel: {e}")
            import traceback
            traceback.print_exc()
            self.failed_count += 1
            return False
    
    def generate_batch(self, count=12, sections=None):
        """
        Generate a batch of reels
        
        Args:
            count: Number of reels to create (default 12)
            sections: List of NYT sections to fetch from
        """
        if sections is None:
            sections = ['business', 'technology', 'politics', 'world', 'sports', 'arts']
        
        print("\n" + "="*60)
        print(f"🎬 Starting batch generation: {count} reels")
        print("="*60)
        
        # Show current stats
        try:
            stats = cockroach_db.get_stats()
            print(f"\n📊 Current Database Stats:")
            print(f"   Total reels: {stats['total']}")
            print(f"   Pending: {stats['pending']}")
            print(f"   Posted: {stats['posted']}")
            print(f"\n")
        except:
            pass
        
        articles_processed = 0
        
        for section in sections:
            if self.created_count >= count:
                break
                
            print(f"\n📰 Fetching articles from section: {section}")
            
            try:
                # Fetch more articles than needed to account for duplicates
                articles = self.pipeline.fetch_latest_news(section=section, limit=count * 2)
                
                if not articles:
                    print(f"⚠️  No articles found in {section}")
                    continue
                
                print(f"✅ Found {len(articles)} articles")
                
                for article in articles:
                    if self.created_count >= count:
                        break
                    
                    articles_processed += 1
                    success = self.generate_reel(article)
                    
                    if success:
                        print(f"\n✅ Progress: {self.created_count}/{count} reels created")
                    
            except Exception as e:
                print(f"❌ Error fetching from {section}: {e}")
                continue
        
        # Final summary
        print("\n" + "="*60)
        print("📊 BATCH GENERATION COMPLETE")
        print("="*60)
        print(f"✅ Created: {self.created_count} reels")
        print(f"⚠️  Failed: {self.failed_count} reels")
        print(f"📝 Articles processed: {articles_processed}")
        
        # Show updated stats
        try:
            stats = cockroach_db.get_stats()
            print(f"\n📊 Updated Database Stats:")
            print(f"   Total reels: {stats['total']}")
            print(f"   Pending: {stats['pending']}")
            print(f"   Posted: {stats['posted']}")
            if stats['total_size_bytes']:
                total_mb = stats['total_size_bytes'] / (1024 * 1024)
                print(f"   Total size: {total_mb:.2f} MB")
            if stats['avg_duration_seconds']:
                print(f"   Avg duration: {stats['avg_duration_seconds']:.1f}s")
        except Exception as e:
            print(f"⚠️  Could not get stats: {e}")

def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🎬 LOCAL REEL GENERATOR")
    print("="*60)
    print("This script will generate reels locally and save to CockroachDB")
    print("Render server will then fetch and post them hourly")
    print("="*60)
    
    # Check environment
    if not os.getenv('USE_VOICE_NARRATION', 'false').lower() == 'true':
        print("\n⚠️  WARNING: USE_VOICE_NARRATION is not enabled in .env")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Get batch size
    try:
        count_input = input("\nHow many reels to generate? (default 12): ").strip()
        count = int(count_input) if count_input else 12
        
        if count < 1 or count > 50:
            print("⚠️  Please enter a number between 1 and 50")
            return
    except ValueError:
        print("❌ Invalid number")
        return
    
    # Confirm
    print(f"\n📝 Will generate {count} reels with voice narration")
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("❌ Cancelled")
        return
    
    # Generate batch
    generator = LocalReelGenerator()
    
    try:
        generator.generate_batch(count=count)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print(f"✅ Created {generator.created_count} reels before stopping")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
