#!/usr/bin/env python3
"""
Test ElevenLabs voice narration for Instagram Reels
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the server
from server import NewsToInstagramPipeline

def test_voice_generation():
    """Test voice narration generation"""
    print("=" * 70)
    print("🎤 Testing ElevenLabs Voice Narration")
    print("=" * 70)
    
    # Check API key
    api_key = os.getenv('elevenlabspaliapi', '')
    if not api_key:
        print("❌ Error: elevenlabspaliapi not found in .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    print(f"✅ Voice ID: {os.getenv('ELEVENLABS_VOICE_ID', 'pMsXgVXv3BLzUgSXRplE')}")
    print(f"✅ Voice narration enabled: {os.getenv('USE_VOICE_NARRATION', 'true')}")
    print()
    
    # Create pipeline
    pipeline = NewsToInstagramPipeline()
    
    # Test with sample article data
    headline = "Trump Pardons Founder of Crypto Exchange Binance"
    ai_analysis = "In a shocking move that raises eyebrows across financial markets, former President Trump has granted clemency to Changpeng Zhao, the billionaire founder of Binance who previously admitted to money laundering violations."
    
    print("📝 Test Content:")
    print(f"   Headline: {headline}")
    print(f"   Analysis: {ai_analysis[:100]}...")
    print()
    
    # Generate voice narration
    print("🎤 Generating voice narration...")
    audio_path = pipeline.generate_voice_narration(headline, ai_analysis)
    
    if audio_path and os.path.exists(audio_path):
        file_size = os.path.getsize(audio_path)
        print(f"✅ SUCCESS! Voice narration generated:")
        print(f"   📁 File: {audio_path}")
        print(f"   📊 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print()
        print("💡 You can play this file to test the voice quality")
        print(f"   Command: afplay {audio_path}")
        print()
        
        # Ask if user wants to play
        try:
            import subprocess
            play = input("▶️  Play the audio now? (y/n): ").lower().strip()
            if play == 'y':
                print("🔊 Playing audio...")
                subprocess.run(['afplay', audio_path])
                print("✅ Playback complete!")
        except KeyboardInterrupt:
            print("\n⏸️  Skipped playback")
        
        # Cleanup
        try:
            os.unlink(audio_path)
            print(f"🗑️  Cleaned up temporary file")
        except:
            pass
        
        return True
    else:
        print("❌ Failed to generate voice narration")
        return False

def test_full_video_with_voice():
    """Test creating a video with voice narration"""
    print("\n" + "=" * 70)
    print("🎬 Testing Full Video Creation with Voice")
    print("=" * 70)
    
    # Check if we should run this test
    try:
        run_test = input("⚠️  This will create a full video. Continue? (y/n): ").lower().strip()
        if run_test != 'y':
            print("⏸️  Test skipped")
            return True
    except KeyboardInterrupt:
        print("\n⏸️  Test cancelled")
        return True
    
    pipeline = NewsToInstagramPipeline()
    
    # Fetch a real article
    print("\n📰 Fetching latest article from NYT...")
    articles = pipeline.fetch_latest_news(section='business', limit=1)
    
    if not articles:
        print("❌ No articles found")
        return False
    
    article = articles[0]
    print(f"✅ Found article: {article.get('title')}")
    print()
    
    # Generate AI analysis
    print("🤖 Generating AI analysis...")
    ai_analysis = pipeline.generate_ai_analysis(article)
    print(f"✅ Analysis: {ai_analysis[:100]}...")
    print()
    
    # Generate voice narration
    print("🎤 Generating voice narration...")
    headline = article.get('title', '')
    audio_path = pipeline.generate_voice_narration(headline, ai_analysis)
    
    if not audio_path or not os.path.exists(audio_path):
        print("❌ Voice generation failed")
        return False
    
    print(f"✅ Voice generated: {audio_path}")
    print()
    
    # Create image with text overlay
    print("🎨 Creating image with text overlay...")
    image_url = article.get('multimedia', [{}])[0].get('url', '')
    
    if not image_url:
        print("❌ No image URL found")
        if os.path.exists(audio_path):
            os.unlink(audio_path)
        return False
    
    # Use the correct method name
    title = article.get('title', '')
    section = article.get('section', 'business')
    
    result = pipeline.add_text_to_image(image_url, title, section)
    
    # The method returns a dict with 'url' and 'local_path'
    if isinstance(result, dict):
        local_image_path = result.get('local_path')
    elif isinstance(result, str):
        # If it returns just a URL, we need to download it
        print("⚠️ Got URL instead of local path, need to download...")
        if os.path.exists(audio_path):
            os.unlink(audio_path)
        return False
    else:
        print("❌ Failed to create image")
        if os.path.exists(audio_path):
            os.unlink(audio_path)
        return False
    
    if not local_image_path or not os.path.exists(local_image_path):
        print("❌ Local image not created")
        if os.path.exists(audio_path):
            os.unlink(audio_path)
        return False
    
    print(f"✅ Image created: {local_image_path}")
    print()
    
    # Create video with voice
    print("🎬 Creating video Reel with voice narration...")
    video_path = pipeline.convert_image_to_video_reel(
        local_image_path,
        duration=7,
        audio_path=audio_path
    )
    
    # Cleanup audio
    if os.path.exists(audio_path):
        os.unlink(audio_path)
    
    if video_path and os.path.exists(video_path):
        file_size = os.path.getsize(video_path)
        print(f"✅ SUCCESS! Video Reel created with voice:")
        print(f"   📁 File: {video_path}")
        print(f"   📊 Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        print()
        print("💡 You can play this video to test:")
        print(f"   Command: open {video_path}")
        print()
        
        # Ask if user wants to play
        try:
            play = input("▶️  Play the video now? (y/n): ").lower().strip()
            if play == 'y':
                print("🎬 Opening video...")
                import subprocess
                subprocess.run(['open', video_path])
        except KeyboardInterrupt:
            print("\n⏸️  Skipped playback")
        
        # Cleanup
        cleanup = input("🗑️  Delete test files? (y/n): ").lower().strip()
        if cleanup == 'y':
            try:
                os.unlink(video_path)
                os.unlink(local_image_path)
                print("✅ Test files deleted")
            except:
                pass
        else:
            print(f"📁 Video saved at: {video_path}")
        
        return True
    else:
        print("❌ Failed to create video")
        # Cleanup image
        if os.path.exists(local_image_path):
            os.unlink(local_image_path)
        return False

if __name__ == '__main__':
    print("\n")
    
    # Test 1: Voice generation only
    success1 = test_voice_generation()
    
    if success1:
        # Test 2: Full video with voice (optional)
        test_full_video_with_voice()
    
    print("\n" + "=" * 70)
    print("✅ Testing complete!")
    print("=" * 70)
    print()
