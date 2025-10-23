# Production Deployment Guide

## Instagram Rate Limits Explained

### What Your Dashboard Shows
- **App-level limits**: 0% used ✅ (This is fine!)
- These limits apply to all API calls across your entire app

### What's Actually Blocking You
Instagram has **hidden limits** not shown in the dashboard:

1. **Account-level limits**: 
   - Max ~25 posts per day per Instagram account
   - Max ~1-2 posts per hour
   - Failed publish attempts count against limits

2. **Testing-induced limits**:
   - Multiple rapid test posts trigger temporary blocks
   - Typically reset after 1-2 hours
   - More strict for new/unverified apps

3. **Content Publishing API limits**:
   - Different from general Graph API limits
   - Designed to prevent spam
   - Affects publish/create operations specifically

## Current Situation

Your testing today has temporarily hit Instagram's anti-spam limits:
- ✅ **App is fine** (0% of app-level limits used)
- ⚠️ **Account temporarily restricted** (will reset soon)
- ✅ **YouTube working perfectly** (no limits hit)

## Instagram Rate Limit Reset

**Your account will be fully operational again in:**
- Best case: 1-2 hours from last failed attempt
- Worst case: 24 hours

**To check if reset:**
```bash
cd /Users/mahendrabahubali/Desktop/QPost/backinsta
/Users/mahendrabahubali/.pyenv/versions/3.9.20/bin/python -c "
from server import NewsToInstagramPipeline
pipeline = NewsToInstagramPipeline()
result = pipeline.post_to_instagram_direct(
    'https://i.ibb.co/0RQtz07j/5b2a2a507bdf.jpg',
    'Test post - checking rate limits'
)
print('✅ Limits reset!' if result['success'] else '⚠️ Still limited')
"
```

## Recommended Production Settings

### For Maximum Reach (Avoid Limits):

```bash
# Post every 30 minutes (safe for Instagram + YouTube)
export POST_INTERVAL_MINUTES=30

# Enable both platforms
export USE_INSTAGRAM_REELS=true
export USE_YOUTUBE_SHORTS=true

# Silent videos (add trending audio manually)
export USE_BACKGROUND_AUDIO=false

# API keys
export GROQ_API_KEY=your_groq_api_key_here
export NYT_API_KEY=your_nyt_api_key_here
export IMGBB_API_KEY=your_imgbb_api_key_here
```

### Expected Daily Output:

With 30-minute intervals:
- **48 posting attempts per day**
- **~20-25 Instagram posts** (some will be skipped due to limits)
- **~45 YouTube Shorts** (fewer limits)
- Both platforms get fresh content continuously

## Safe Posting Schedule

### Option 1: Conservative (Recommended)
```bash
POST_INTERVAL_MINUTES=30  # Every 30 minutes
# Result: ~25 Instagram posts + ~45 YouTube Shorts per day
```

### Option 2: Moderate
```bash
POST_INTERVAL_MINUTES=20  # Every 20 minutes
# Result: ~25 Instagram posts (will hit limits) + ~70 YouTube Shorts per day
```

### Option 3: Aggressive (Not Recommended)
```bash
POST_INTERVAL_MINUTES=15  # Every 15 minutes
# Result: Instagram will block frequently, YouTube fine
```

## Handling Rate Limits in Code

The system already handles rate limits gracefully:

1. **Instagram fails** → System logs warning
2. **Moves to YouTube** → Posts successfully
3. **Waits for next interval** → Tries Instagram again
4. **After 3 consecutive failures** → Extends wait time by 5 minutes

## Best Practices for Production

### 1. Start Slow
First week: 30-minute intervals
- Builds trust with Instagram
- Establishes posting pattern
- Reduces risk of permanent blocks

### 2. Monitor Logs
Watch for these patterns:
```
✅ Good: "Post ID: 17847941841585640"
⚠️ Warning: "Application request limit reached"
🔄 Recovery: System automatically retries later
```

### 3. Manual Trending Audio
After automated posting:
1. Open Instagram app
2. Edit the Reel
3. Add trending audio (REQUIRED for algorithm boost!)
4. Instagram heavily promotes Reels with trending sounds

### 4. Database Cleanup
Your MongoDB will grow over time:
```bash
# Check database size
mongo "mongodb+srv://aj:aj@qpost.lk5htbl.mongodb.net/" --eval "db.posts.count()"

# Current: 77 posts (very lightweight with new schema)
# Monthly: ~750 posts (manageable)
# Yearly: ~9,000 posts (still fine with lightweight storage)
```

## Deployment Options

### Option A: Local Machine (Simplest)
```bash
cd /Users/mahendrabahubali/Desktop/QPost/backinsta

# Create a launch script
cat > start_poster.sh << 'EOF'
#!/bin/bash
export USE_INSTAGRAM_REELS=true
export USE_YOUTUBE_SHORTS=true
export POST_INTERVAL_MINUTES=30
export GROQ_API_KEY=your_groq_api_key_here

cd /Users/mahendrabahubali/Desktop/QPost/backinsta
/Users/mahendrabahubali/.pyenv/versions/3.9.20/bin/python scheduled_poster.py
EOF

chmod +x start_poster.sh

# Run in background with nohup
nohup ./start_poster.sh > poster.log 2>&1 &

# View logs
tail -f poster.log
```

### Option B: Render (Cloud - Recommended)
1. Push code to GitHub
2. Create Render Web Service
3. Add environment variables in dashboard
4. Auto-deploys on git push
5. Always online, no local machine needed

**Render Environment Variables:**
```
USE_INSTAGRAM_REELS=true
USE_YOUTUBE_SHORTS=true
POST_INTERVAL_MINUTES=30
GROQ_API_KEY=your_groq_api_key_here
NYT_API_KEY=your_nyt_api_key_here
IMGBB_API_KEY=your_imgbb_api_key_here
MONGODB_URI=your_mongodb_uri_here
INSTAGRAM_ACCESS_TOKEN=your_instagram_token_here
INSTAGRAM_ACCOUNT_ID=your_instagram_account_id
PORT=10000
```

**Note:** YouTube OAuth credentials (youtube_token.pickle) need to be generated locally first, then uploaded to Render or use service account instead.

## Troubleshooting Rate Limits

### Issue: "Application request limit reached"
**Solution:**
1. Wait 1-2 hours
2. Reduce posting frequency (increase POST_INTERVAL_MINUTES)
3. System will automatically continue with YouTube only

### Issue: "Fatal - Unable to publish media"
**Causes:**
- Image URL unreachable
- Image too large (>8MB)
- Invalid image format

**Solution:** System automatically retries with original image

### Issue: Instagram works but YouTube fails
**Causes:**
- YouTube OAuth token expired
- youtube_token.pickle missing
- Video format incompatible

**Solution:**
```bash
# Re-authenticate YouTube
rm youtube_token.pickle
python3 -c "from youtube_shorts import YouTubeShortsUploader; YouTubeShortsUploader()"
```

## Monitoring & Analytics

### Check System Health
```bash
# View recent posts
mongo "mongodb+srv://aj:aj@qpost.lk5htbl.mongodb.net/" --eval "
db.posts.find().sort({posted_at: -1}).limit(5).pretty()
"

# Count posts by platform
mongo "mongodb+srv://aj:aj@qpost.lk5htbl.mongodb.net/" --eval "
db.posts.aggregate([
  { \$group: { 
    _id: null, 
    instagram: { \$sum: { \$cond: [{ \$ne: ['\$instagram_post_id', null] }, 1, 0] }},
    youtube: { \$sum: { \$cond: [{ \$ne: ['\$youtube_video_id', null] }, 1, 0] }}
  }}
])
"
```

### Instagram Insights
- Open Instagram app → @usdaily24 → Professional Dashboard
- Check Reels performance
- Identify best posting times
- Track trending audio impact

### YouTube Analytics
- Go to YouTube Studio → Analytics
- Monitor Shorts performance
- Check viewer retention
- Track subscriber growth

## Long-Term Strategy

### Week 1: Testing
- 30-minute intervals
- Monitor rate limits
- Adjust as needed

### Week 2-4: Stabilization
- Consistent posting pattern
- Add trending audio manually
- Build audience

### Month 2+: Optimization
- Analyze best-performing content
- Adjust posting schedule to peak hours
- Consider multiple accounts for scaling

## Peak Posting Times (EST)

Based on social media engagement data:

**High Engagement:**
- 6:00-9:00 AM (Morning commute)
- 12:00-1:00 PM (Lunch break)
- 7:00-9:00 PM (Evening relaxation)

**Lower Engagement:**
- 2:00-5:00 AM (Night hours)
- 2:00-4:00 PM (Work hours)

**Recommendation:** Start with 24/7 posting, then analyze Instagram Insights to find YOUR audience's peak times.

## Success Metrics

After 1 month, you should see:
- ✅ 600-750 posts across both platforms
- ✅ Consistent posting without manual intervention
- ✅ Growing follower base on Instagram
- ✅ Increasing views on YouTube Shorts
- ✅ MongoDB database under 50MB storage

## Support & Maintenance

### Weekly Tasks:
- Check logs for errors
- Verify posts are going through
- Add trending audio to Instagram Reels

### Monthly Tasks:
- Review analytics
- Update NYT API key if needed
- Check MongoDB storage usage
- Update Python dependencies

### As Needed:
- Refresh Instagram access token (every 60 days)
- Re-authenticate YouTube if token expires
- Update Groq API key if needed

---

## Ready to Go Live?

1. **Wait for Instagram rate limits to reset** (1-2 hours)
2. **Start with conservative settings** (30-minute intervals)
3. **Monitor first 24 hours** closely
4. **Adjust as needed** based on performance

Your system is production-ready! 🚀
