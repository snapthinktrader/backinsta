# YouTube Shorts Setup Guide

## Overview
This guide walks you through setting up YouTube Shorts integration for automated posting.

## Prerequisites
- Google account: forexyynewsletter@gmail.com
- YouTube Data API key: AIzaSyBO1mrYoksmwSJFgOFtSc16b00yWi8cIwk (already added to .env)

## OAuth2 Credentials Setup

### Step 1: Go to Google Cloud Console
Visit: https://console.cloud.google.com/

### Step 2: Create or Select Project
- Click the project dropdown at the top
- Create a new project named "BackInsta" or select existing
- Note: Make sure billing is NOT required for YouTube Data API v3

### Step 3: Enable YouTube Data API v3
1. Click "APIs & Services" in the left menu
2. Click "Library"
3. Search for "YouTube Data API v3"
4. Click on it and press "ENABLE"

### Step 4: Configure OAuth Consent Screen
1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" user type
3. Fill in the form:
   - **App name**: BackInsta News Poster
   - **User support email**: forexyynewsletter@gmail.com
   - **Developer contact email**: forexyynewsletter@gmail.com
4. Click "Save and Continue"
5. Add Scopes:
   - Click "Add or Remove Scopes"
   - Search for "youtube.upload"
   - Check: `https://www.googleapis.com/auth/youtube.upload`
   - Click "Update" → "Save and Continue"
6. Add Test Users:
   - Click "Add Users"
   - Enter: forexyynewsletter@gmail.com
   - Click "Save and Continue"
7. Review and click "Back to Dashboard"

### Step 5: Create OAuth 2.0 Client ID
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: **Desktop app**
4. Name: "BackInsta YouTube Shorts Uploader"
5. Click "Create"

### Step 6: Download Credentials File
1. You'll see your new OAuth 2.0 Client ID in the list
2. Click the download button (⬇️) on the right
3. A JSON file will be downloaded
4. Rename it to: `youtube_credentials.json`
5. Move it to: `/Users/mahendrabahubali/Desktop/QPost/backinsta/youtube_credentials.json`

## First-Time Authentication

### Step 7: Run Authentication Flow
1. Set environment variable:
   ```bash
   export USE_YOUTUBE_SHORTS=true
   ```

2. Run the poster:
   ```bash
   cd /Users/mahendrabahubali/Desktop/QPost/backinsta
   python3 scheduled_poster.py
   ```

3. A browser window will open automatically
4. Sign in with: forexyynewsletter@gmail.com
5. Click "Allow" to authorize the app
6. The browser will show "The authentication flow has completed"
7. Close the browser and return to terminal

### Step 8: Token Saved
- A file `youtube_token.pickle` will be created
- This stores your authentication for future use
- You won't need to authorize again unless the token expires

## Environment Variables

Make sure your `.env` file includes:

```bash
# Feature Flags
USE_INSTAGRAM_REELS=true
USE_YOUTUBE_SHORTS=true
USE_BACKGROUND_AUDIO=false

# YouTube Configuration
YOUTUBE_API_KEY=AIzaSyBO1mrYoksmwSJFgOFtSc16b00yWi8cIwk
```

## Testing

Test YouTube upload with a single article:

```bash
cd /Users/mahendrabahubali/Desktop/QPost/backinsta
export USE_INSTAGRAM_REELS=true
export USE_YOUTUBE_SHORTS=true
export POST_INTERVAL_MINUTES=0

python3 scheduled_poster.py
```

## What Gets Posted

For each article:
1. **Instagram Reel** (@usdaily24):
   - 1080x1920 static video (7 seconds)
   - Transparent overlay with forexyy.com logo
   - Silent (add trending audio manually via Instagram app)

2. **YouTube Short** (forexyynewsletter@gmail.com):
   - Same 1080x1920 video
   - Title: "[Article Title]" (80 chars max)
   - Description: Article abstract + link + #Shorts hashtag
   - Category: News & Politics
   - Privacy: Public

## Database Tracking

MongoDB stores:
- `article_url` - Article URL
- `title` - First 100 chars of title
- `section` - News section
- `instagram_post_id` - Instagram post ID
- `youtube_video_id` - YouTube video ID (new)
- `youtube_url` - YouTube Shorts URL (new)
- `posted_at` - Timestamp
- `youtube_posted_at` - YouTube upload timestamp (new)

## Troubleshooting

### "youtube_credentials.json not found"
- Make sure you downloaded the OAuth credentials
- Place the file in `/Users/mahendrabahubali/Desktop/QPost/backinsta/`
- Rename it exactly to `youtube_credentials.json`

### "Access blocked: This app's request is invalid"
- Make sure you added forexyynewsletter@gmail.com as a test user
- OAuth consent screen must be configured correctly
- Try using "External" user type instead of "Internal"

### "The user has not granted the app sufficient permissions"
- Delete `youtube_token.pickle` if it exists
- Re-run the authentication flow
- Make sure to click "Allow" when authorizing

### YouTube upload fails but Instagram works
- Check that `USE_YOUTUBE_SHORTS=true` in environment
- Verify `youtube_credentials.json` exists
- Check logs for specific error messages
- YouTube will gracefully fail without breaking Instagram posting

## Notes

- YouTube API has a quota limit (10,000 units/day)
- Each video upload costs ~1600 units
- You can upload ~6 videos per day
- The system posts every 15 minutes, so max ~96 attempts/day
- Instagram will continue working even if YouTube fails

## Success Indicators

When working correctly, you'll see:
```
✅ YouTube Shorts uploader initialized
🎬 Uploading to YouTube Shorts...
✅ YouTube Short uploaded successfully!
📹 YouTube Video ID: ABC123xyz
🔗 YouTube URL: https://youtube.com/shorts/ABC123xyz
```

## Multi-Platform Success

Both platforms posting means:
- 📸 Instagram: @usdaily24 (17841477569192718)
- 📹 YouTube: forexyynewsletter@gmail.com
- 🌐 Double reach across platforms
- 🎵 Add trending audio to Instagram manually
- 📊 Track engagement on both platforms
