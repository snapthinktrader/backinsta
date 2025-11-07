"""
Test different Google TTS voices to find the best news anchor voice
"""

import os
from google_tts_voice import GoogleTTSVoice

# Test commentary (news anchor style)
test_text = """
Breaking news from the world of technology. 
Trump has pardoned the founder of the cryptocurrency exchange Binance, 
who previously admitted to violating anti-money laundering laws. 
This controversial decision has sparked debate across financial and political circles, 
with critics questioning the timing and implications of this presidential action.
"""

print("\n" + "="*60)
print("🎤 GOOGLE TTS VOICE COMPARISON FOR NEWS ANCHOR")
print("="*60)

# Available Neural2 voices
voices = {
    "en-US-Neural2-A": "Male - Clear and authoritative",
    "en-US-Neural2-D": "Male - Deep and serious",
    "en-US-Neural2-I": "Male - Warm and friendly",
    "en-US-Neural2-J": "Male - Professional news anchor",
    "en-US-Studio-M": "Male - Studio quality",
    "en-US-Studio-Q": "Male - Natural and engaging",
}

tts = GoogleTTSVoice()

if not tts.client:
    print("❌ Google TTS not initialized")
    exit(1)

print(f"\n📝 Test text ({len(test_text)} characters):")
print(test_text[:100] + "...\n")

for voice_name, description in voices.items():
    print(f"\n{'='*60}")
    print(f"🎙️  Testing: {voice_name}")
    print(f"   {description}")
    print("="*60)
    
    output_path = f"/tmp/tts_test_{voice_name}.mp3"
    
    result = tts.generate_voice(test_text, output_path, voice_name=voice_name)
    
    if result:
        file_size = os.path.getsize(result)
        print(f"✅ Generated: {file_size / 1024:.1f} KB")
        print(f"📁 Location: {result}")
        print(f"🎧 Play: afplay {result}")
        
        # Optionally play automatically
        # os.system(f"afplay {result}")
    else:
        print(f"❌ Failed to generate")

print("\n" + "="*60)
print("🎬 TESTING COMPLETE")
print("="*60)
print("\nRecommended voices for news anchor:")
print("1. en-US-Neural2-J - Professional TV news anchor style")
print("2. en-US-Studio-Q - Natural and engaging")
print("3. en-US-Neural2-D - Authoritative and serious")
print("\nTo play all files:")
print("afplay /tmp/tts_test_*.mp3")
