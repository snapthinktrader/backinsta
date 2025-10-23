# Render Deployment - Complete Setup with YouTube

## Environment Variables for Render

Copy these into Render Dashboard → Your Service → Environment:

### Instagram Configuration
```
REACT_APP_ACCESS_TOKEN=your_instagram_access_token_here
REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID=17841477569192718
```

### MongoDB
```
MONGODB_URI=your_mongodb_connection_string_here
```

### NYT API
```
NYT_API_KEY=your_nyt_api_key_here
```

### Groq AI
```
GROQ_API_KEY=your_groq_api_key_here
```

### Image Hosting
```
IMGBB_API_KEY=your_imgbb_api_key_here
```

### Feature Flags
```
USE_INSTAGRAM_REELS=true
USE_YOUTUBE_SHORTS=true
USE_BACKGROUND_AUDIO=false
```

### Posting Schedule
```
POST_INTERVAL_MINUTES=30
```

### YouTube Credentials (Base64 Encoded)

**YOUTUBE_CREDENTIALS_BASE64:**
```
eyJpbnN0YWxsZWQiOnsiY2xpZW50X2lkIjoiMTcwNjQxNDYzOTIzLWRzNGllMWJuNGF0cnVuamJzZXFjcmR2dTU0dXBkNGh0LmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29tIiwicHJvamVjdF9pZCI6Im51a2thZC1mb29kcyIsImF1dGhfdXJpIjoiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLCJ0b2tlbl91cmkiOiJodHRwczovL29hdXRoMi5nb29nbGVhcGlzLmNvbS90b2tlbiIsImF1dGhfcHJvdmlkZXJfeDUwOV9jZXJ0X3VybCI6Imh0dHBzOi8vd3d3Lmdvb2dsZWFwaXMuY29tL29hdXRoMi92MS9jZXJ0cyIsImNsaWVudF9zZWNyZXQiOiJHT0NTUFgtQVVIT09ORkMyOWM3Rkp4TVVJQ1lnLWhMeVdyaCIsInJlZGlyZWN0X3VyaXMiOlsiaHR0cDovL2xvY2FsaG9zdCJdfX0=
```

**YOUTUBE_TOKEN_BASE64:**
```
gASVAwQAAAAAAACMGWdvb2dsZS5vYXV0aDIuY3JlZGVudGlhbHOUjAtDcmVkZW50aWFsc5STlCmBlH2UKIwFdG9rZW6UjP15YTI5LmEwQVFRX0JEU0pIM0ZYT0dnY1pnaDk5YUJSWFZTRWJaUlUwV3dYUXRZbHNZSDVUOFNDaFlFLUxoNVE5NjBra2xtSFhzUjRub2QyWG1pR29fNlZxb2ZZcWNCa2pCc0NCaWNucGxuZkVfWjlka2tZMUVqOHpXVDVjX29lLUI3RE9JMHJWTUxFY1JfalhnbWFyQjFuWUFHWDFHdTFDWHA0M0w0T1EzUUFsMDBkaHlQZEtob0ZaaFdXRHpzMDNSaGpNclJhRHZmU1pWMGFDZ1lLQVlNU0FSVVNGUUhHWDJNaXNYUDZTYjFUSTlwWUFsWVRDZEc5SncwMjA2lIwGZXhwaXJ5lIwIZGF0ZXRpbWWUjAhkYXRldGltZZSTlEMKB+kKFwMSEgD5fpSFlFKUjA5fcmVmcmVzaF90b2tlbpSMZzEvLzBnUWtEVVNGTGlXZFFDZ1lJQVJBQUdCQVNOd0YtTDlJcjRmOE1ZQ3dxTktTRHhUaW1LbW96NmxLUHpWZi1vZ0hTNzd0Ui1vVklvc01TVE1uamlpR0pKTTVIZnFYdUxWd0xIcHOUjAlfaWRfdG9rZW6UTowHX3Njb3Blc5RdlIwuaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vYXV0aC95b3V0dWJlLnVwbG9hZJRhjA9fZGVmYXVsdF9zY29wZXOUTowPX2dyYW50ZWRfc2NvcGVzlF2UjC5odHRwczovL3d3dy5nb29nbGVhcGlzLmNvbS9hdXRoL3lvdXR1YmUudXBsb2FklGGMCl90b2tlbl91cmmUjCNodHRwczovL29hdXRoMi5nb29nbGVhcGlzLmNvbS90b2tlbpSMCl9jbGllbnRfaWSUjEgxNzA2NDE0NjM5MjMtZHM0aWUxYm40YXRydW5qYnNlcWNyZHZ1NTR1cGQ0aHQuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb22UjA5fY2xpZW50X3NlY3JldJSMI0dPQ1NQWC1BVUhPT05GQzI5YzdGSnhNVUlDWWctaEx5V3JolIwRX3F1b3RhX3Byb2plY3RfaWSUTowLX3JhcHRfdG9rZW6UTowWX2VuYWJsZV9yZWF1dGhfcmVmcmVzaJSJjA9fdHJ1c3RfYm91bmRhcnmUTowQX3VuaXZlcnNlX2RvbWFpbpSMDmdvb2dsZWFwaXMuY29tlIwPX2NyZWRfZmlsZV9wYXRolE6MGV91c2Vfbm9uX2Jsb2NraW5nX3JlZnJlc2iUiYwIX2FjY291bnSUjACUdWIu
```

## Render Service Configuration

### Service Settings:
- **Name:** backinsta-news-poster
- **Region:** Oregon (US West) or closest to you
- **Branch:** main
- **Root Directory:** (leave blank, or set to `backinsta` if needed)

### Build Settings:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python scheduled_poster.py`

### Service Type:
- **Web Service** (required for health check on port 10000)

### Instance Type:
- **Free** (should be sufficient for 30-min posting intervals)

## Deployment Steps

1. **Go to Render Dashboard:** https://dashboard.render.com/

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub account if not already connected
   - Select repository: `snapthinktrader/backinsta`
   - Click "Connect"

3. **Configure Service:**
   - Name: `backinsta-news-poster`
   - Region: Choose closest to you
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python scheduled_poster.py`

4. **Add Environment Variables:**
   - Click "Advanced" → "Add Environment Variable"
   - Copy-paste all variables from above (one by one)
   - **Important:** Add both `YOUTUBE_CREDENTIALS_BASE64` and `YOUTUBE_TOKEN_BASE64`

5. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment (2-5 minutes)

6. **Monitor Logs:**
   Look for these success messages:
   ```
   ✅ YouTube credentials file created from environment
   ✅ YouTube token file created from environment
   ✅ YouTube API authenticated
   ✅ YouTube Shorts uploader initialized
   ```

## Verification

After deployment, check logs for:
- ✅ MongoDB connection successful
- ✅ YouTube API authenticated
- ✅ Health check server started on port 10000
- ✅ Configuration valid

First post should happen within 30 minutes!

## Troubleshooting

### If YouTube authentication fails:
1. Check `YOUTUBE_TOKEN_BASE64` is set correctly (long base64 string)
2. Token might be expired - regenerate locally:
   ```bash
   cd /Users/mahendrabahubali/Desktop/QPost/backinsta
   rm youtube_token.pickle
   python3 -c "from youtube_shorts import YouTubeShortsUploader; y = YouTubeShortsUploader()"
   # Browser will open for re-authentication
   base64 -i youtube_token.pickle
   # Copy new base64 string to Render
   ```

### If posts aren't happening:
1. Check Render logs for errors
2. Verify Instagram token hasn't expired
3. Ensure MongoDB connection is successful
4. Check if rate limited (wait 1-2 hours)

## Expected Behavior

With 30-minute intervals:
- **~48 posting attempts per day**
- **~25 Instagram posts** (accounting for rate limits)
- **~45 YouTube posts** (higher limit)
- **Multi-platform resilience:** If Instagram fails, YouTube still posts

## Monitoring

- **Render Logs:** Real-time posting activity
- **MongoDB:** Check `backinsta.posted_articles` collection
- **Instagram:** @usdaily24 account
- **YouTube:** forexyynewsletter@gmail.com channel

## Cost

- **Render Free Tier:** $0/month (750 hours/month included)
- **Note:** Free tier services may sleep after 15 min of inactivity
  - Health check endpoint keeps it awake
  - Or upgrade to paid ($7/month) for always-on

## Success! 🎉

Once deployed, your system will:
- ✅ Post to Instagram Reels every 30 minutes
- ✅ Post to YouTube Shorts every 30 minutes
- ✅ Run 24/7 without your computer on
- ✅ Never post duplicate articles
- ✅ Handle rate limits gracefully
