# Deploy to Render NOW - Simple 3-Step Guide

## What Render Does
✅ Fetches pre-generated videos from CockroachDB (with voice already included)  
✅ Posts to Instagram/YouTube every 15 minutes  
❌ Does NOT generate videos (that's done locally)  
❌ Does NOT need Google Cloud credentials (videos already have voice)

---

## Prerequisites ✓

- ✅ 6 reels ready in CockroachDB (with Google TTS voice)
- ✅ Instagram API credentials
- ✅ YouTube API credentials  
- ✅ All code tested locally

---

## Step 1: Push to GitHub (2 minutes)

```bash
cd /Users/mahendrabahubali/Desktop/QPost/backinsta

git add scheduled_poster_cockroach.py cockroach_poster.py database/ requirements.txt youtube_shorts.py
git commit -m "Add 15-min auto-poster"
git push origin main
```

---

## Step 2: Create Render Web Service (5 minutes)

1. Go to https://dashboard.render.com
2. Click **"New +" → "Web Service"**
3. Connect repository: `snapthinktrader/backinsta`
4. Configure:
   - **Name**: `backinsta-auto-poster`
   - **Branch**: `main`
   - **Root Directory**: *(leave blank)*
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python scheduled_poster_cockroach.py`
   - **Instance Type**: `Free`

---

## Step 3: Add Environment Variables (2 minutes)

Add only these 3 variables in Render dashboard:

```bash
COCKROACHDB_URI=postgresql://snap:zY7iXb69bunWURtTeASzhg@backinsta-17456.j77.aws-ap-south-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full

REACT_APP_ACCESS_TOKEN=<your_instagram_token>

REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID=<your_instagram_id>

POST_INTERVAL_MINUTES=15
```

**Optional** (for YouTube):
- Add `client_secret_*.json` if you want YouTube posting

---

## Step 4: Deploy! (1 minute)

Click **"Create Web Service"** and watch the logs:

Expected output:
```
🚀 Instagram Auto-Poster Starting (CockroachDB Mode)...
⏰ Posting interval: 15 minutes
📊 Initial Database Stats: Pending: 6
🔄 Cycle #1 started...
✅ Posted to Instagram: 18292...
```

---

## What Happens Next?

| Time | Action |
|------|--------|
| 0:00 | Deploy complete |
| 0:15 | First reel posted |
| 0:30 | Second reel posted |
| 0:45 | Third reel posted |
| 1:00 | Fourth reel posted |
| 1:15 | Fifth reel posted |
| 1:30 | All 6 reels posted! |

---

## Weekly Maintenance

Generate more reels locally (once per week):
```bash
cd /Users/mahendrabahubali/Desktop/QPost/backinsta
echo -e "12\ny" | python generate_reels_local.py
```

This creates 12 new reels → Render posts them automatically over next 3 hours (at 15-min intervals).

---

## That's It!

No Google Cloud setup needed on Render.  
No complicated configurations.  
Just fetch and post. 🚀
