"""
Animated Reel Generator
Generates dynamic reels with NYT image + stock footage + voice + synced captions
Based on generate_reels_local.py but uses animated_reel_creator.py
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
from animated_reel_creator import AnimatedReelCreator

# Load environment
load_dotenv()

class AnimatedReelGenerator:
    """Generate animated reels with NYT image + stock footage + voice + captions"""
    
    def __init__(self):
        self.pipeline = NewsToInstagramPipeline()
        self.google_tts = GoogleTTSVoice()
        self.animated_creator = AnimatedReelCreator()
        self.created_count = 0
        self.failed_count = 0
        print("✅ Animated Reel Generator initialized")
        print("   - NYT image + Stock footage")
        print("   - AI-selected media (Pexels + Google)")
        print("   - Voice narration")
        print("   - Synced word-by-word captions")
    
    def generate_reel(self, article):
        """Generate a single animated reel from article"""
        try:
            headline = article.get('title', article.get('headline', ''))
            article_url = article.get('url', article.get('web_url', ''))
            
            # Generate unique article ID
            from mongo_database import generate_article_id
            article_id = generate_article_id(article_url)
            
            print(f"\n{'='*60}")
            print(f"🎬 Creating ANIMATED reel: {headline[:50]}...")
            print(f"{'='*60}")
            
            # Step 1: Check if reel already exists
            print("🔍 Checking if reel already exists...")
            if cockroach_db.reel_exists(article_id):
                print("⚠️  Reel already exists in database (skipped)")
                return False
            
            # Step 2: Generate AI analysis
            print("🤖 Generating AI analysis...")
            ai_analysis = self.pipeline.generate_ai_analysis(article)
            
            if not ai_analysis:
                print("❌ Failed to generate AI analysis")
                return False
            
            print(f"✅ Analysis: {ai_analysis[:80]}...")
            
            # Step 3: Generate voice narration
            print("🎤 Generating voice narration with Google TTS...")
            voice_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
            
            success = self.google_tts.generate_voice(
                text=ai_analysis,
                output_path=voice_audio_path,
                voice_name="en-US-Studio-O"
            )
            
            if not success or not os.path.exists(voice_audio_path):
                print("❌ Failed to generate voice")
                return False
            print(f"✅ Voice generated: {voice_audio_path}")
            
            # Step 4: Get NYT article image URL
            print("📥 Getting NYT article image...")
            image_url = self.pipeline.get_article_image_url(article)
            if not image_url:
                print("⚠️ No NYT article image found, will use stock footage only")
                image_url = None
            else:
                print(f"✅ NYT image: {image_url[:60]}...")
            
            # Step 5: Create ANIMATED reel with NYT image + stock footage + voice + captions
            print("🎬 Creating ANIMATED reel (NYT image + stock footage + voice + captions)...")
            
            # Get audio duration for target video duration
            try:
                from moviepy import AudioFileClip
                audio = AudioFileClip(voice_audio_path)
                target_duration = int(audio.duration)
                audio.close()
            except:
                target_duration = 30  # Default
            
            # Create animated reel
            video_path = self.animated_creator.create_animated_reel(
                headline=headline,
                commentary=ai_analysis,
                voice_audio_path=voice_audio_path,
                target_duration=target_duration,
                clips_count=6,  # More clips (6-8) for dynamic, engaging reel
                nyt_image_url=image_url
            )
            
            if not video_path or not os.path.exists(video_path):
                print("❌ Animated reel creation failed")
                return False
            
            print(f"✅ Animated reel created successfully!")
            
            # Step 6: Read video data
            print("📦 Reading video data...")
            with open(video_path, 'rb') as f:
                video_data = f.read()
            
            file_size = len(video_data)
            file_size_mb = file_size / (1024 * 1024)
            
            # Get duration from audio
            try:
                from moviepy import AudioFileClip
                audio = AudioFileClip(voice_audio_path)
                duration = audio.duration
                audio.close()
            except:
                duration = target_duration
            
            # Step 7: Generate caption
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
                thumbnail_url=image_url,  # Use NYT image as thumbnail
                ai_analysis=ai_analysis,
                duration=duration,
                file_size=file_size
            )
            
            if reel_id:
                print(f"✅ SUCCESS! Animated reel saved to database: {reel_id}")
                print(f"   Duration: {duration:.1f}s")
                print(f"   Size: {file_size_mb:.2f} MB")
                print(f"   Features:")
                print(f"      - NYT image (first clip)")
                print(f"      - Stock footage (AI-selected)")
                print(f"      - Voice narration")
                print(f"      - Synced captions")
                self.created_count += 1
                
                # Cleanup temp files
                try:
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
            print(f"❌ Error creating animated reel: {e}")
            import traceback
            traceback.print_exc()
            self.failed_count += 1
            return False
    
    def generate_batch(self, count=5, sections=None):
        """
        Generate a batch of animated reels
        
        Args:
            count: Number of reels to create (default 5)
            sections: List of NYT sections to fetch from
        """
        if sections is None:
            sections = ['business', 'technology', 'politics', 'world']
        
        print("\n" + "="*60)
        print(f"🎬 Starting ANIMATED REEL batch generation: {count} reels")
        print("="*60)
        
        # Show current stats
        stats = cockroach_db.get_stats()
        print(f"\n📊 Current Database Stats:")
        print(f"   Total reels: {stats.get('total', 0)}")
        print(f"   Pending: {stats.get('pending', 0)}")
        print(f"   Posted: {stats.get('posted', 0)}")
        print("\n")
        
        articles_processed = 0
        
        for section in sections:
            if self.created_count >= count:
                break
            
            print(f"\n📰 Fetching articles from section: {section}")
            articles = self.pipeline.fetch_latest_news(section=section, limit=count)
            
            if not articles:
                print(f"⚠️  No articles found in {section}")
                continue
            
            print(f"✅ Found {len(articles)} articles\n")
            
            for article in articles:
                if self.created_count >= count:
                    break
                
                success = self.generate_reel(article)
                articles_processed += 1
                
                if success:
                    print(f"\n✅ Progress: {self.created_count}/{count} reels created\n")
        
        # Final summary
        print("\n" + "="*60)
        print("📊 ANIMATED REEL BATCH GENERATION COMPLETE")
        print("="*60)
        print(f"✅ Created: {self.created_count} animated reels")
        print(f"⚠️  Failed: {self.failed_count} reels")
        print(f"📝 Articles processed: {articles_processed}")
        
        # Updated stats
        final_stats = cockroach_db.get_stats()
        print(f"\n📊 Updated Database Stats:")
        print(f"   Total reels: {final_stats.get('total', 0)}")
        print(f"   Pending: {final_stats.get('pending', 0)}")
        print(f"   Posted: {final_stats.get('posted', 0)}")
        total_size_mb = (final_stats.get('total_size_bytes', 0) or 0) / (1024 * 1024)
        avg_duration = final_stats.get('avg_duration_seconds', 0) or 0
        print(f"   Total size: {total_size_mb:.2f} MB")
        print(f"   Avg duration: {avg_duration:.1f}s")

def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🎬 ANIMATED REEL GENERATOR")
    print("="*60)
    print("This script generates DYNAMIC animated reels:")
    print("  • NYT article image (first clip)")
    print("  • Stock footage (AI-selected from Pexels/Google)")
    print("  • Voice narration (Google TTS)")
    print("  • Synced word-by-word captions (Groq Whisper)")
    print("="*60)
    print()
    
    # Get user input
    try:
        count = input("How many animated reels to generate? (default 5): ").strip()
        count = int(count) if count else 5
    except (ValueError, KeyboardInterrupt):
        print("\n❌ Cancelled")
        return
    
    print(f"\n📝 Will generate {count} animated reels with voice + captions")
    confirm = input("Continue? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Cancelled")
        return
    
    # Generate reels
    generator = AnimatedReelGenerator()
    generator.generate_batch(count=count)
    
    print("\n✅ Done! Reels saved to CockroachDB")
    print("🚀 Render server will post them automatically")

if __name__ == "__main__":
    main()
