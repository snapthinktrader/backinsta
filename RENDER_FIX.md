# 🔧 Fix Render Deployment

## Problem
Render is running `server.py` (old code with 60-sec intervals and small text) instead of `scheduled_poster.py` (new HD quality code with 15-min intervals).

## Solution: Update Render Settings Manually

### Step 1: Login to Render
1. Go to https://dashboard.render.com
2. Login with: **snapthinktrader@gmail.com**

### Step 2: Update Start Command
1. Click on **instagram-auto-poster** service
2. Go to **Settings** (left sidebar)
3. Scroll to **Build & Deploy** section
4. Find **Start Command**
5. Change from: `python server.py`
6. Change to: `python scheduled_poster.py`
7. Click **Save Changes**

### Step 3: Redeploy
1. Go to **Manual Deploy** (top right)
2. Click **Deploy latest commit**
3. Wait for deployment to complete (~2-3 minutes)

### Step 4: Verify
Check the logs should show:
- ✅ `🚀 Instagram Auto-Poster Starting...`
- ✅ `⏰ Posting interval: 15 minutes`
- ✅ `✅ Cropped and upscaled to portrait: 1080x1350`
- ✅ `✅ Using font size 72px`

NOT:
- ❌ `⏳ Waiting 60 seconds before next post...`
- ❌ Small image dimensions (400x600)
- ❌ Small font sizes (28px, 48px on small images)

## Expected Quality
- **Image**: 1080x1350 portrait (Instagram HD)
- **Font**: 72px (scales with image)
- **Quality**: JPEG 98%, no compression
- **Interval**: 15 minutes between posts
- **Upload**: imgbb (imgur as fallback)
