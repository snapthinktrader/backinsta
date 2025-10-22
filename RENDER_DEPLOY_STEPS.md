# 🚀 Deploy to Render - Step by Step

## Quick Start (5 minutes)

### 1. Prepare Your Code

The code is ready! Just make sure you have:
- ✅ `scheduled_poster.py` - Main scheduler
- ✅ `render.yaml` - Render configuration
- ✅ `requirements.txt` - Dependencies
- ✅ `Procfile` - Process definition
- ✅ `runtime.txt` - Python version

### 2. Push to GitHub

```bash
# If not already a git repo
cd /Users/mahendrabahubali/Desktop/QPost/backinsta
git init

# Add all files
git add .
git commit -m "Add Instagram auto-poster with 15-minute intervals"

# Create repo on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/instagram-autoposter.git
git branch -M main
git push -u origin main
```

### 3. Deploy on Render

#### Option A: Using Dashboard (Easiest)

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Background Worker"**
3. Click **"Connect GitHub"** and authorize
4. Select your repository
5. Configure:
   - **Name**: `instagram-auto-poster`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `backinsta` if in subdirectory)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python scheduled_poster.py`
   - **Plan**: Free
6. Add **Environment Variables**:
   ```
   POST_INTERVAL_MINUTES=15
   REACT_APP_ACCESS_TOKEN=<your_instagram_never_expire_token>
   REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID=17841477569192718
   GROQ_API_KEY=<your_groq_api_key>
   IMGBB_API_KEY=<your_imgbb_api_key>
   WEBSTORY_MONGODB_URI=<your_webstory_mongodb_connection_string>
   MONGODB_URI=<your_qpost_mongodb_connection_string>
   ```
7. Click **"Create Background Worker"**

#### Option B: Using Render CLI

```bash
# Install Render CLI
npm install -g @render/cli

# Login
render login

# Deploy
render services create --yaml render.yaml

# Set environment variables
render env set POST_INTERVAL_MINUTES=15
render env set REACT_APP_ACCESS_TOKEN="YOUR_TOKEN"
render env set REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID="17841477569192718"
render env set GROQ_API_KEY="YOUR_KEY"
render env set IMGBB_API_KEY="YOUR_KEY"
```

### 4. Monitor Deployment

**Watch Logs**:
```bash
render logs instagram-auto-poster --tail
```

**Or in Dashboard**:
- Go to your service → Logs tab

### 5. Verify It's Working

You should see logs like:
```
🚀 Instagram Auto-Poster Starting...
⏰ Posting interval: 15 minutes (Production)
✅ Configuration valid
🔄 Cycle #1 started at HH:MM:SS
✅ Found article from business: Title...
🎉 Successfully posted to Instagram: POST_ID
✅ Article saved to database
⏰ Next post scheduled for: HH:MM:SS
💤 Sleeping for 15 minutes...
```

## 📊 What Happens on Render?

1. **Build Phase**: Installs Python dependencies
2. **Start Phase**: Runs `python scheduled_poster.py`
3. **Runtime**: Posts every 15 minutes indefinitely
4. **Auto-restart**: If crashes, Render restarts automatically

## ⚙️ Configuration Options

### Change Posting Interval

In Render Dashboard → Environment Variables:
- Set `POST_INTERVAL_MINUTES=30` for 30 minutes
- Set `POST_INTERVAL_MINUTES=60` for 1 hour
- Default if not set: 15 seconds (local testing only)

### Change Section Priority

Edit `scheduled_poster.py` line 29:
```python
sections = ['business', 'technology', 'politics', 'entertainment', 'sports', 'home']
```

### Adjust Error Handling

Edit `scheduled_poster.py` line 104:
```python
if error_count >= 3:
    time.sleep(300)  # Change this to adjust wait time
```

## 🐛 Troubleshooting

### Service Won't Start
- Check logs for Python errors
- Verify all environment variables are set
- Ensure requirements.txt is complete

### No Posts Being Made
- Check Instagram access token validity
- Verify MongoDB connections
- Check if articles exist in database

### Rate Limiting
- Instagram has posting limits
- Reduce frequency if needed
- Monitor for API errors in logs

## 💰 Cost

**Free Tier**:
- ✅ 750 hours/month included
- ✅ Enough for 24/7 operation
- ✅ Auto-sleeps after 15 min inactivity
- ✅ Wakes up on schedule

**No credit card required for free tier!**

## 🎯 Success Checklist

- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] All environment variables set
- [ ] Service shows "Live" status
- [ ] Logs show successful posts
- [ ] Instagram account shows new posts
- [ ] Database tracking articles

## 📞 Support

- **Render Status**: https://status.render.com
- **Render Docs**: https://render.com/docs/background-workers
- **Instagram API**: https://developers.facebook.com/docs/instagram-api

## 🔄 Updates

To update your deployment:
```bash
git add .
git commit -m "Update message"
git push

# Render auto-deploys on push!
```

## 🛑 Stop/Pause Service

**Temporary Pause**:
- Dashboard → Your Service → Suspend

**Delete Service**:
- Dashboard → Your Service → Settings → Delete Service
