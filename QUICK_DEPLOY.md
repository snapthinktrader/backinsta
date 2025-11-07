# Quick Render Deployment Commands

## ✅ System Ready - 6 Pending Reels in Database

**Current Status**: All checks passed, system ready for deployment!

**Key Point**: Render ONLY fetches and posts pre-generated videos. No voice generation needed on Render!

---

## Step 1: Push to GitHub

```bash
cd /Users/mahendrabahubali/Desktop/QPost/backinsta

# Add files
git add scheduled_poster_cockroach.py
git add cockroach_poster.py
git add database/
git add requirements.txt
git add youtube_shorts.py

# Commit
git commit -m "Add 15-minute auto-poster for Render deployment"

# Push
git push origin main
```

---

## Step 2: Render Configuration

### Web Service Settings:
- **Name**: `backinsta-auto-poster`
- **Region**: `Oregon (US West)`
- **Branch**: `main`
- **Root Directory**: Leave blank
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python scheduled_poster_cockroach.py`
- **Instance Type**: `Free`

### Environment Variables (Add in Render Dashboard):

```bash
# CockroachDB Connection
COCKROACHDB_URI=postgresql://snap:zY7iXb69bunWURtTeASzhg@backinsta-17456.j77.aws-ap-south-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full

# Instagram API
REACT_APP_ACCESS_TOKEN=<your-token>
REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID=<your-id>

# Posting Interval (15 minutes)
POST_INTERVAL_MINUTES=15

# Port (auto-set by Render)
PORT=10000
```

**That's it!** Only 3 variables needed (plus PORT).

---

## Step 3: Deploy and Monitor

1. Click **"Create Web Service"** in Render
2. Wait for deployment (2-3 minutes)
3. Check logs for:
   ```
   🚀 Instagram Auto-Poster Starting (CockroachDB Mode)...
   ⏰ Posting interval: 15 minutes
   📊 Initial Database Stats: Pending: 6
   🔄 Cycle #1 started...
   ```

4. Verify health:
   ```bash
   curl https://backinsta-auto-poster.onrender.com/health
   ```

---

## Expected Timeline

With **15-minute intervals** and **6 pending reels**:

- **0:00** - Deploy to Render
- **0:15** - First reel posted (Social Security)
- **0:30** - Second reel posted (Pay Attention to Savings)
- **0:45** - Third reel posted (Bonds Should Be Boring)
- **1:00** - Fourth reel posted (NBA Insider Trading)
- **1:15** - Fifth reel posted (Companies Shield Tariffs)
- **1:30** - Sixth reel posted (Smart Beds)
- **1:45** - No pending reels, waits for new ones

---

## Maintenance

### Generate More Reels (Weekly)
```bash
cd /Users/mahendrabahubali/Desktop/QPost/backinsta
echo -e "12\ny" | /Users/mahendrabahubali/Desktop/QPost/.venv/bin/python generate_reels_local.py
```

### Check Database Status
```bash
/Users/mahendrabahubali/Desktop/QPost/.venv/bin/python -c "
from database.cockroach_setup import get_stats
stats = get_stats()
print(f'Pending: {stats[\"pending\"]}, Posted: {stats[\"posted\"]}')
"
```

### Update Posting Interval
In Render Dashboard → Environment → Edit `POST_INTERVAL_MINUTES`

---

## Troubleshooting

### No pending reels
Generate more:
```bash
echo -e "6\ny" | python generate_reels_local.py
```

### Rate limited
Increase interval to 30 minutes:
```bash
POST_INTERVAL_MINUTES=30
```

### SSL certificate error
Add environment variable in Render:
```bash
PGSSLMODE=verify-full
```

---

## Success Indicators

✅ **Health check returns**: `OK - Instagram Auto-Poster Running`
✅ **Logs show**: `✅ Posted to Instagram: 18292...`
✅ **Database**: Pending count decreases, Posted count increases
✅ **Instagram**: New Reels appear in 9:16 format every 15 minutes
✅ **No errors**: System runs continuously without crashes

---

## Current Deployment Status

- ✅ **Code Ready**: All files prepared
- ✅ **Database Ready**: 6 pending reels (9:16 format, Google TTS)
- ✅ **Testing Complete**: Instagram posting verified
- ⏳ **Next**: Create service account and deploy to Render

**Estimated Deployment Time**: 15-20 minutes
