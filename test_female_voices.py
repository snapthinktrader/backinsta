"""
Test female Google TTS voices for news anchor style
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
print("🎤 FEMALE GOOGLE TTS VOICE COMPARISON FOR NEWS ANCHOR")
print("="*60)

# Available Female Neural2 voices
voices = {
    "en-US-Neural2-C": "Female - Professional and clear",
    "en-US-Neural2-E": "Female - Warm and engaging",
    "en-US-Neural2-F": "Female - Authoritative news anchor",
    "en-US-Neural2-G": "Female - Serious and professional",
    "en-US-Neural2-H": "Female - Friendly and natural",
    "en-US-Studio-O": "Female - Studio quality news",
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
    
    output_path = f"/tmp/tts_female_{voice_name}.mp3"
    
    result = tts.generate_voice(test_text, output_path, voice_name=voice_name)
    
    if result:
        file_size = os.path.getsize(result)
        print(f"✅ Generated: {file_size / 1024:.1f} KB")
        print(f"📁 Location: {result}")
        print(f"🎧 Play: afplay {result}")
    else:
        print(f"❌ Failed to generate")

print("\n" + "="*60)
print("🎬 TESTING COMPLETE")
print("="*60)
print("\nRecommended FEMALE voices for news anchor:")
print("1. en-US-Neural2-F - Authoritative female news anchor")
print("2. en-US-Neural2-C - Professional and clear")
print("3. en-US-Studio-O - Studio quality female news")
print("\nTo play all female voices:")
print("afplay /tmp/tts_female_*.mp3")
