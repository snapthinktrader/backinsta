#!/usr/bin/env python3
"""
Test script to verify system is ready for Render deployment
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def check_env_var(name, required=True):
    """Check if environment variable is set"""
    value = os.getenv(name)
    if value:
        # Mask sensitive values
        if 'TOKEN' in name or 'KEY' in name:
            display = f"{value[:10]}...{value[-10:]}"
        elif 'URI' in name:
            display = value.split('@')[0] + '@...'
        else:
            display = value[:30] + '...' if len(value) > 30 else value
        
        print(f"✅ {name}: {display}")
        return True
    else:
        if required:
            print(f"❌ {name}: NOT SET (REQUIRED)")
        else:
            print(f"⚠️  {name}: NOT SET (optional)")
        return not required

def test_database_connection():
    """Test CockroachDB connection"""
    try:
        from database.mongodb_setup import get_stats
        stats = get_stats()
        print(f"\n✅ CockroachDB Connection:")
        print(f"   Total reels: {stats['total']}")
        print(f"   Pending: {stats['pending']}")
        print(f"   Posted: {stats['posted']}")
        print(f"   Failed: {stats['failed']}")
        return True
    except Exception as e:
        print(f"\n❌ CockroachDB Connection Failed: {e}")
        return False

def test_google_tts():
    """Test Google TTS"""
    try:
        from google_tts_voice import GoogleTTSVoice
        tts = GoogleTTSVoice()
        if tts.client:
            print(f"\n✅ Google TTS: Initialized")
            return True
        else:
            print(f"\n❌ Google TTS: Failed to initialize")
            return False
    except Exception as e:
        print(f"\n❌ Google TTS Error: {e}")
        return False

def test_instagram_config():
    """Test Instagram configuration"""
    access_token = os.getenv('REACT_APP_ACCESS_TOKEN')
    account_id = os.getenv('REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID')
    
    if access_token and account_id:
        print(f"\n✅ Instagram Configuration:")
        print(f"   Access Token: {access_token[:20]}...")
        print(f"   Business Account ID: {account_id}")
        return True
    else:
        print(f"\n❌ Instagram Configuration: Missing credentials")
        return False

def main():
    print("\n" + "="*70)
    print("🔍 RENDER DEPLOYMENT READINESS CHECK")
    print("="*70)
    
    all_checks_passed = True
    
    # Check environment variables
    print("\n📋 ENVIRONMENT VARIABLES:")
    print("-" * 70)
    
    all_checks_passed &= check_env_var('COCKROACHDB_URI', required=True)
    all_checks_passed &= check_env_var('REACT_APP_ACCESS_TOKEN', required=True)
    all_checks_passed &= check_env_var('REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID', required=True)
    check_env_var('POST_INTERVAL_MINUTES', required=False)
    check_env_var('GOOGLE_APPLICATION_CREDENTIALS_JSON', required=False)
    
    # Check database connection
    print("\n📊 DATABASE CONNECTION:")
    print("-" * 70)
    all_checks_passed &= test_database_connection()
    
    # Check Google TTS
    print("\n🎤 GOOGLE TEXT-TO-SPEECH:")
    print("-" * 70)
    all_checks_passed &= test_google_tts()
    
    # Check Instagram config
    print("\n📱 INSTAGRAM API:")
    print("-" * 70)
    all_checks_passed &= test_instagram_config()
    
    # Check critical files
    print("\n📁 CRITICAL FILES:")
    print("-" * 70)
    
    required_files = [
        'scheduled_poster_cockroach.py',
        'cockroach_poster.py',
        'google_tts_voice.py',
        'database/cockroach_setup.py',
        'requirements.txt',
        'youtube_shorts.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_checks_passed = False
    
    # Final summary
    print("\n" + "="*70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - READY FOR RENDER DEPLOYMENT!")
        print("\n📝 Next Steps:")
        print("1. Create Google Cloud service account (see RENDER_DEPLOYMENT.md)")
        print("2. Push code to GitHub")
        print("3. Create Render web service")
        print("4. Add environment variables to Render")
        print("5. Deploy and monitor logs")
        print("\n📖 See RENDER_DEPLOYMENT.md for detailed instructions")
    else:
        print("❌ SOME CHECKS FAILED - FIX ISSUES BEFORE DEPLOYMENT")
        print("\nℹ️  Review errors above and fix before deploying to Render")
    print("="*70)
    
    return 0 if all_checks_passed else 1

if __name__ == '__main__':
    sys.exit(main())
