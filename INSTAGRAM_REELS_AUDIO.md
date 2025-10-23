# Instagram Reels with Trending Audio 🎵

## Overview
Our system creates Instagram Reels from news articles with text overlays and animations. For maximum reach, you can add trending audio in two ways:

## Method 1: Silent Reels + Manual Instagram Music (RECOMMENDED ⭐)
**Best for reach** - Use Instagram's built-in trending music library

### How it works:
1. System posts **silent Reels** via API
2. You manually add trending music through Instagram app
3. Instagram's algorithm boosts Reels with trending sounds

### Steps:
1. After Reel is posted, open Instagram app
2. Go to your posted Reel
3. Tap "Edit" → "Add Music"
4. Search for trending sounds (look for 🔥 icon)
5. Select and save

### Advantages:
- ✅ Access to ALL Instagram trending sounds
- ✅ Better algorithm reach (Instagram prioritizes their music)
- ✅ Always up-to-date with trends
- ✅ No copyright issues

## Method 2: Embed Royalty-Free Background Music
**Automated** - Add background music before uploading

### Setup:
1. Download royalty-free music from:
   - Pixabay Audio: https://pixabay.com/music/
   - YouTube Audio Library
   - Free Music Archive
   - Epidemic Sound (subscription)

2. Add .mp3 files to `audio_tracks/` folder

3. Enable in environment:
   ```bash
   export USE_BACKGROUND_AUDIO=true
   export USE_INSTAGRAM_REELS=true
   ```

4. System will automatically:
   - Pick random audio from tracks
   - Loop/trim to video duration
   - Embed into Reel before upload

### Advantages:
- ✅ Fully automated
- ✅ Consistent branding
- ✅ No manual work needed

### Disadvantages:
- ❌ Can't use Instagram trending sounds
- ❌ Less algorithm boost
- ❌ Need to manage music library

## Configuration

### Enable Reels:
```bash
# In .env or Render environment variables
USE_INSTAGRAM_REELS=true          # Enable video Reels instead of images
USE_BACKGROUND_AUDIO=true          # Enable embedded audio (Method 2)
```

### Disable Reels (use static images):
```bash
USE_INSTAGRAM_REELS=false          # Default: posts static images
```

## Current Setup
- **Default**: Posts static images with transparent text overlay
- **With USE_INSTAGRAM_REELS=true**: Posts 7-second video Reels with zoom animation
- **Video Specs**: 1080x1920 (9:16 ratio), 30fps, H.264 codec

## Recommendations

### For Maximum Reach:
1. Enable `USE_INSTAGRAM_REELS=true`
2. Keep `USE_BACKGROUND_AUDIO=false` (post silent)
3. Manually add trending sounds via Instagram app
4. Check Instagram's trending page daily for hot sounds

### For Automation:
1. Enable both flags
2. Add 10-15 royalty-free tracks to `audio_tracks/`
3. Rotate tracks weekly to keep content fresh

## Finding Trending Sounds

### Via Instagram App:
1. Open Reels → Search
2. Look for 🔥 trending sounds
3. Note popular sounds used by big accounts

### Trending Categories (as of 2025):
- News intro beats
- Dramatic background scores
- Upbeat electronic music
- Cinematic transitions
- Podcast-style commentary music

## Technical Details

### Video Creation Process:
1. Download article image
2. Add text overlay + forexyy.com logo
3. Convert to 7s video with zoom animation
4. Add audio (if enabled)
5. Upload to imgbb/hosting
6. Post to Instagram as REEL

### API Limitations:
- Instagram Graph API doesn't support adding music from Instagram's library
- Can only embed external audio files
- Silent Reels can have music added post-upload via app

## Troubleshooting

### Reels not posting:
- Check imgbb supports .mp4 files (it does)
- Verify video is under 8MB
- Ensure 9:16 aspect ratio

### Audio not working:
- Check .mp3 files are in `audio_tracks/`
- Verify `USE_BACKGROUND_AUDIO=true`
- Check moviepy is installed: `pip install moviepy`

### Better reach:
- Use Method 1 (silent + manual music)
- Post during peak hours (6-9 AM, 12-1 PM, 7-9 PM EST)
- Add trending hashtags in caption
- Use Instagram's trending sounds
