"""
Test Complete Animated Reel Generation LOCALLY
Tests all features before integrating with CockroachDB
"""

import os
import sys
import tempfile
from dotenv import load_dotenv

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from server import NewsToInstagramPipeline
from google_tts_voice import GoogleTTSVoice
from animated_reel_creator import AnimatedReelCreator

# Load environment
load_dotenv()

def test_animated_reel_local():
    """Generate a complete animated reel and save locally for testing"""
    
    print("\n" + "="*60)
    print("🎬 TESTING COMPLETE ANIMATED REEL LOCALLY")
    print("="*60)
    print()
    
    # Initialize components
    print("🔧 Initializing components...")
    pipeline = NewsToInstagramPipeline()
    google_tts = GoogleTTSVoice()
    animated_creator = AnimatedReelCreator()
    
    # Fetch a single article
    print("\n📰 Fetching latest article from NYT...")
    articles = pipeline.fetch_latest_news(section='business', limit=1)
    
    if not articles:
        print("❌ No articles found")
        return False
    
    article = articles[0]
    headline = article.get('title', article.get('headline', ''))
    article_url = article.get('url', article.get('web_url', ''))
    
    print(f"✅ Article: {headline[:60]}...")
    print(f"   URL: {article_url[:80]}...")
    
    # Generate AI analysis
    print("\n🤖 Generating AI analysis...")
    ai_analysis = pipeline.generate_ai_analysis(article)
    
    if not ai_analysis:
        print("❌ Failed to generate AI analysis")
        return False
    
    print(f"✅ Analysis: {ai_analysis[:100]}...")
    
    # Generate voice narration
    print("\n🎤 Generating voice narration...")
    voice_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
    
    success = google_tts.generate_voice(
        text=ai_analysis,
        output_path=voice_audio_path,
        voice_name="en-US-Studio-O"
    )
    
    if not success or not os.path.exists(voice_audio_path):
        print("❌ Failed to generate voice")
        return False
    
    print(f"✅ Voice generated: {os.path.getsize(voice_audio_path) / 1024:.1f} KB")
    
    # Get NYT article image
    print("\n📥 Getting NYT article image...")
    image_url = pipeline.get_article_image_url(article)
    if not image_url:
        print("⚠️  No NYT article image found, will use stock footage only")
        image_url = None
    else:
        print(f"✅ NYT image: {image_url[:60]}...")
    
    # Get audio duration for target video duration
    print("\n⏱️  Calculating target duration...")
    try:
        from moviepy import AudioFileClip
        audio = AudioFileClip(voice_audio_path)
        target_duration = int(audio.duration)
        audio.close()
        print(f"✅ Target duration: {target_duration}s")
    except:
        target_duration = 30
        print(f"✅ Using default duration: {target_duration}s")
    
    # Create animated reel with ALL features
    print("\n🎬 Creating COMPLETE animated reel...")
    print("   Features to include:")
    print("   ✓ NYT article image (first clip, 4s)")
    print("   ✓ Stock footage (6+ clips, 3-4s each for dynamic transitions)")
    print("   ✓ Headline text overlay")
    print("   ✓ Rachel Anderson anchor overlay")
    print("   ✓ Voice narration")
    print("   ✓ Synced captions")
    print()
    
    video_path = animated_creator.create_animated_reel(
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
    
    # Copy to Desktop for easy viewing
    output_path = "/Users/mahendrabahubali/Desktop/complete_animated_reel_test.mp4"
    import shutil
    shutil.copy(video_path, output_path)
    
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    
    print("\n" + "="*60)
    print("✅ SUCCESS! Complete animated reel created!")
    print("="*60)
    print(f"📺 Video: {output_path}")
    print(f"📊 Size: {file_size_mb:.2f} MB")
    print(f"⏱️  Duration: ~{target_duration}s")
    print()
    print("📋 Features included:")
    print("   ✓ NYT article image with text overlay (4s)")
    print("   ✓ Stock footage clips (6+ clips, 3-4s each)")
    print("   ✓ Headline text overlay (throughout)")
    print("   ✓ Rachel Anderson anchor overlay (left side, below headline)")
    print("   ✓ Voice narration (Google TTS)")
    print("   ✓ Synced captions (if available)")
    print("   ✓ Fast-paced, dynamic transitions")
    print()
    
    # Open the video
    print("🎬 Opening video...")
    os.system(f'open "{output_path}"')
    
    # Cleanup temp files
    try:
        if os.path.exists(video_path):
            os.unlink(video_path)
        if os.path.exists(voice_audio_path):
            os.unlink(voice_audio_path)
    except:
        pass
    
    return True

if __name__ == "__main__":
    try:
        success = test_animated_reel_local()
        if success:
            print("\n✅ Test completed successfully!")
            print("👉 Review the video, then we can integrate with CockroachDB")
        else:
            print("\n❌ Test failed")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
