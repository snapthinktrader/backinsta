# Instagram Auto-Poster - Render Deployment Guide

Automatically posts news articles from Webstory to Instagram every 15 minutes.

## 🚀 Quick Deploy

### Option 1: Using Render Dashboard (Easiest)

1. **Create a GitHub repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Go to [Render Dashboard](https://dashboard.render.com)**

3. **Click "New +" → "Background Worker"**

4. **Connect your GitHub repository**

5. **Configure the service**:
   - **Name**: `instagram-auto-poster`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Root Directory**: `backinsta` (if this is a subdirectory)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python scheduled_poster.py`
   - **Plan**: Free

6. **Add Environment Variables**:
   ```
   REACT_APP_ACCESS_TOKEN=your_instagram_token
   REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID=17841477569192718
   GROQ_API_KEY=your_groq_key
   IMGBB_API_KEY=your_imgbb_key
   WEBSTORY_MONGODB_URI=mongodb+srv://ajay26:Ajtiwari26@cluster0.pfudopf.mongodb.net/webstory
   MONGODB_URI=mongodb+srv://aj:aj@qpost.lk5htbl.mongodb.net/
   ```

7. **Click "Create Background Worker"**

### Option 2: Using Render CLI

1. **Install Render CLI**:
   ```bash
   # macOS/Linux
   curl -fsSL https://render.com/install-cli.sh | bash
   
   # Or using npm
   npm install -g @render/cli
   ```

2. **Login to Render**:
   ```bash
   render login
   ```

3. **Deploy**:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

4. **Or manually**:
   ```bash
   render services create --yaml render.yaml
   ```

## 📋 Environment Variables

You need to set these in your `.env` file or Render dashboard:

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_ACCESS_TOKEN` | Instagram User Access Token | `EAALT8qe9kpE...` |
| `REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID` | Instagram Business Account ID | `17841477569192718` |
| `GROQ_API_KEY` | Groq AI API Key | `gsk_goh0lCRo...` |
| `IMGBB_API_KEY` | imgbb Image Hosting Key | `c21e386db487...` |
| `WEBSTORY_MONGODB_URI` | Webstory MongoDB Connection | `mongodb+srv://...` |
| `MONGODB_URI` | QPost MongoDB Connection | `mongodb+srv://...` |

## 🔧 Configuration

Edit `scheduled_poster.py` to change:

- **Posting interval**: Change `POST_INTERVAL = 15 * 60` (currently 15 minutes)
- **Section priority**: Modify the `sections` list
- **Error handling**: Adjust retry logic

## 📊 Monitoring

### View Logs

**Render Dashboard**:
- Go to your service → "Logs" tab

**Render CLI**:
```bash
render logs instagram-auto-poster --tail
```

### Check Service Status

```bash
render services list
```

## 🧪 Local Testing

Before deploying, test locally:

```bash
# Test single post
python3 test_post_article.py

# Test scheduled poster (Ctrl+C to stop)
python3 scheduled_poster.py
```

## 🐛 Troubleshooting

### Service not starting

1. Check logs for errors
2. Verify all environment variables are set
3. Ensure `requirements.txt` includes all dependencies

### No articles being posted

1. Check if there are articles in the database
2. Verify MongoDB connection strings
3. Check Instagram access token validity

### Instagram API errors

- **Access token expired**: Get a new long-lived token
- **Rate limits**: Reduce posting frequency
- **Media URL errors**: Verify imgbb API key

### Database connection issues

- Ensure MongoDB URIs are correct
- Check if IP address is whitelisted in MongoDB Atlas
- Verify credentials

## 📝 Files Structure

```
backinsta/
├── scheduled_poster.py    # Main scheduling script
├── server.py              # Instagram posting logic
├── config.py              # Configuration
├── database.py            # Database operations
├── requirements.txt       # Python dependencies
├── render.yaml            # Render configuration
├── Procfile              # Process configuration
├── runtime.txt           # Python version
└── deploy.sh             # Deployment script
```

## 🔐 Security Notes

- Never commit `.env` file to git
- Keep access tokens secure
- Use environment variables for sensitive data
- Regularly rotate API keys

## 📈 Scaling

**Free Tier Limits**:
- 750 hours/month of runtime
- Service sleeps after 15 min of inactivity
- Wakes up on schedule

**To upgrade**:
- Change plan in Render dashboard
- Adjust posting frequency in code
- Add multiple workers for different sections

## 🆘 Support

- Check logs: `render logs instagram-auto-poster`
- Render docs: https://render.com/docs
- Instagram API: https://developers.facebook.com/docs/instagram-api

## 📅 Posting Schedule

Current configuration:
- **Frequency**: Every 15 minutes
- **Sections**: business, technology, politics, entertainment, sports, home
- **Priority**: Tries sections in order until successful
- **Auto-retry**: Waits 5 minutes on multiple failures

## ✅ Success Indicators

Your service is working when you see:
```
✅ Configuration valid
🔄 Cycle #1 started at HH:MM:SS
✅ Found article from business: Title...
🎉 Successfully posted to Instagram: POST_ID
✅ Article saved to database
⏰ Next post scheduled for: HH:MM:SS
```
