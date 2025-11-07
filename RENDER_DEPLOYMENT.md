# Render Deployment Guide - CockroachDB Auto-Poster

## Overview
This deployment guide sets up the automated Instagram/YouTube posting system on Render. The system **fetches pre-generated reels** (with voice already embedded) from CockroachDB and posts them every **15 minutes**.

## Architecture
```
Local Machine → Generate Reels (with Google TTS voice) → CockroachDB (Cloud)
                                                              ↓
Render Web Service → Fetch Complete Videos → Post to Instagram/YouTube
(Every 15 minutes)                            (No voice generation needed)
```

**Key Point**: Render ONLY fetches and posts. All video generation (including voice) happens locally.

## Prerequisites

✅ **CockroachDB** - Already configured
- URI: `postgresql://snap:zY7iXb69bunWURtTeASzhg@backinsta-17456.j77.aws-ap-south-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full`
- 6 pending reels ready to post (with voice already embedded)

✅ **Instagram API** - Already configured
- Access Token: In environment variables
- Business Account ID: In environment variables

✅ **YouTube API** - Already configured
- OAuth credentials ready

❌ **Google Cloud TTS** - NOT NEEDED ON RENDER
- Only used locally for reel generation
- Videos in database already have voice embedded

## Step 1: Prepare Files for Render

The following files are already ready for deployment:

### Core Files
- ✅ `scheduled_poster_cockroach.py` - Main posting loop (15-min intervals)
- ✅ `cockroach_poster.py` - Instagram/YouTube posting logic
- ✅ `database/cockroach_setup.py` - Database utilities
- ✅ `requirements.txt` - All dependencies
- ✅ `youtube_shorts.py` - YouTube uploader

### Configuration Files
- ✅ `.env` - Local environment variables (DO NOT commit to GitHub)
- ✅ `render.yaml` - Render configuration (optional)

**Note**: `google_tts_voice.py` is NOT needed on Render since videos are pre-generated with voice.

## Step 2: Push to GitHub

```bash
# Navigate to backinsta directory
cd /Users/mahendrabahubali/Desktop/QPost/backinsta

# Initialize git if not already done
git init

# Add files
git add scheduled_poster_cockroach.py
git add cockroach_poster.py
git add database/
git add requirements.txt
git add youtube_shorts.py

# Commit
git commit -m "Add CockroachDB auto-poster for Render deployment"

# Add remote (if not already added)
git remote add origin https://github.com/snapthinktrader/backinsta.git

# Push
git push origin main
```

## Step 4: Create Web Service on Render

1. **Go to Render Dashboard**: https://dashboard.render.com

2. **Click "New +" → "Web Service"**

3. **Connect Repository**: 
   - Select `snapthinktrader/backinsta`
   - Click "Connect"

4. **Configure Service**:
   - **Name**: `backinsta-auto-poster`
   - **Region**: `Oregon (US West)` or closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave blank or `.`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python scheduled_poster_cockroach.py`
   - **Instance Type**: `Free` (sufficient for this use case)

## Step 4: Add Environment Variables

In Render dashboard, add these environment variables:

### Required Variables

```bash
# CockroachDB Connection
COCKROACHDB_URI=postgresql://snap:zY7iXb69bunWURtTeASzhg@backinsta-17456.j77.aws-ap-south-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full

# Instagram API
REACT_APP_ACCESS_TOKEN=<your_instagram_access_token>
REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID=<your_instagram_business_account_id>

# Posting Interval (minutes)
POST_INTERVAL_MINUTES=15

# Render Port (auto-set by Render)
PORT=10000
```

### Optional Variables

```bash
# YouTube API OAuth (if using YouTube)
# These are loaded from client_secret file in production
```

**That's it!** No Google Cloud credentials needed since videos are pre-generated.

## Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repo
   - Install dependencies from `requirements.txt`
   - Start `scheduled_poster_cockroach.py`
3. Monitor the **Logs** tab to see:
   ```
   🚀 Instagram Auto-Poster Starting (CockroachDB Mode)...
   ⏰ Posting interval: 15 minutes
   🏥 Health check server started on port 10000
   📊 Initial Database Stats:
      Total reels: 8
      Pending: 6
      Posted: 2
   🔄 Cycle #1 started...
   ```

## Step 8: Verify Deployment

### Check Health Endpoint
```bash
curl https://backinsta-auto-poster.onrender.com/health
# Should return: OK - Instagram Auto-Poster Running (CockroachDB Mode)
```

### Monitor First Post
Watch the Render logs for:
```
🔄 Fetching next reel from CockroachDB...
   ✅ Progress: 6/6 reels created
```

## Step 6: Verify Deployment
📤 Uploading video to tmpfiles.org...
✅ Video uploaded to tmpfiles: http://tmpfiles.org/dl/...
📹 Creating Instagram media container...
✅ Media container created: 17848...
⏳ Waiting for Instagram to process video (30s)...
📱 Publishing to Instagram...
✅ Posted to Instagram: 18292...
📊 Database Stats:
   Pending: 5
   Posted: 3
⏰ Next post scheduled for: 14:15:00
💤 Sleeping for 15 minutes...
```

## Step 7: Configure SSL Certificate (CockroachDB)

CockroachDB requires SSL. Render should handle this automatically, but if you get SSL errors:

1. Download the CA cert:
```bash
curl --create-dirs -o ~/.postgresql/root.crt \
  'https://cockroachlabs.cloud/clusters/backinsta-17456/cert'
```

2. Add to Render as a **Secret File**:
   - Key: `PGSSLROOTCERT`
   - Content: Contents of `~/.postgresql/root.crt`

## Expected Behavior

### Timeline
- **Every 15 minutes**: Fetch 1 pending reel and post
- **6 pending reels**: Will be posted over 90 minutes (1.5 hours)
- **YouTube quota**: May fail initially (quota exceeded), will work after reset

### Database Status Flow
```
pending → posted (success)
pending → failed (error, will retry later)
```

### Posting Sequence
1. Fetch oldest pending reel from CockroachDB
2. Upload video to tmpfiles.org (120s timeout)
3. Create Instagram media container (Reels, 9:16)
4. Wait 30s for Instagram processing
5. Publish to Instagram
6. Upload same video to YouTube Shorts
7. Mark reel as posted (or failed)
8. Sleep 15 minutes
9. Repeat

## Monitoring

### Render Dashboard
- **Logs**: Real-time posting activity
- **Metrics**: CPU, Memory, Request count
- **Events**: Deployments, crashes

### Database Stats
Check current status:
```python
from database.cockroach_setup import get_stats
stats = get_stats()
print(f"Pending: {stats['pending']}, Posted: {stats['posted']}")
```

### Instagram Insights
- Check Instagram Business Account for new Reels
- Verify format is 9:16 (Reels, not Feed Posts)
- Monitor views, engagement

## Troubleshooting

### Issue: "No pending reels in database"
**Solution**: Generate more reels locally
```bash
cd /Users/mahendrabahubali/Desktop/QPost/backinsta
echo -e "6\ny" | python generate_reels_local.py
```

### Issue: "Instagram rate limited"
**Error**: Code 4 - Rate limit exceeded
**Solution**: Increase `POST_INTERVAL_MINUTES` to 30 or 60

### Issue: "YouTube quota exceeded"
**Error**: Quota exceeded
**Solution**: Wait until quota resets (daily at midnight PST), or YouTube will be skipped (Instagram still works)

### Issue: "SSL certificate verify failed"
**Solution**: Add `PGSSLROOTCERT` secret file to Render

### Issue: "Google credentials not found"
**Not applicable** - Render doesn't use Google TTS since videos are pre-generated

## Scaling

### Increase Posting Frequency
Change environment variable:
```bash
POST_INTERVAL_MINUTES=10  # Post every 10 minutes
```

### Generate More Reels
Run locally weekly:
```bash
echo -e "15\ny" | python generate_reels_local.py  # Generate 15 reels
```

### Monitor Costs
- **Render**: Free tier (sufficient)
- **CockroachDB**: Free tier (5 GB storage)
- **Google TTS**: Free tier (1M chars/month)
- **tmpfiles.org**: Free (public hosting)

## Success Checklist

- [ ] Code pushed to GitHub
- [ ] Render web service created
- [ ] Environment variables added (CockroachDB, Instagram)
- [ ] Service deployed successfully
- [ ] Health check returns OK
- [ ] First reel posted successfully
- [ ] Database status updated
- [ ] 15-minute interval working
- [ ] Instagram shows Reels (9:16 format)

## Maintenance

### Weekly Tasks
1. Generate 12-15 new reels locally
2. Check database stats (pending count)
3. Monitor Instagram analytics

### Monthly Tasks
1. Review Google TTS usage (stay under 1M chars)
2. Check CockroachDB storage (stay under 5 GB)
3. Verify Instagram token hasn't expired

### As Needed
- Update posting interval
- Generate more reels if queue low
- Check for Instagram API changes

## Current Status

✅ **6 pending reels ready** in CockroachDB
✅ **System tested** - Instagram posting works with tmpfiles.org
✅ **Format verified** - 9:16 Reels with Google TTS voice
✅ **Code ready** - All files prepared for deployment

**Next Action**: Follow this guide to deploy to Render!
