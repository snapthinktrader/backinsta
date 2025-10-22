# BackInsta - Quick Reference Guide

## 📁 File Structure

```
backinsta/
├── server.py           # Main server with posting pipeline
├── config.py           # Configuration management
├── database.py         # MongoDB integration for tracking posts
├── test.py            # Comprehensive test suite
├── quickstart.py      # Interactive startup script
├── start.sh           # Bash startup script
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variables template
├── .env              # Your configuration (create from .env.example)
├── README.md         # Full documentation
└── QUICK_START.md    # This file
```

## ⚡ Quick Start (3 Steps)

### 1. Install Dependencies

```bash
cd backinsta
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your Instagram credentials
```

Required in `.env`:
- `REACT_APP_ACCESS_TOKEN` - Your Instagram Graph API token
- `REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID` - Your Instagram account ID

### 3. Run

**Option A: Interactive Menu**
```bash
python quickstart.py
```

**Option B: Bash Script**
```bash
./start.sh
```

**Option C: Direct Commands**
```bash
# Run tests first
python test.py

# Start server for live posting
python server.py
```

## 🎯 Common Tasks

### Test Before Going Live

```bash
python test.py
```

This will:
- ✅ Validate configuration
- ✅ Test article fetching from Webstory
- ✅ Test caption generation
- ✅ Test image extraction
- ✅ Offer optional live posting test

### Start Automated Posting

```bash
python server.py
```

This will:
- Fetch latest news from Webstory backend
- Post to Instagram automatically
- Run on a schedule (every 4-8 hours)
- Track posted articles to avoid duplicates

### Check What Will Be Posted

```python
from server import NewsToInstagramPipeline

pipeline = NewsToInstagramPipeline()
articles = pipeline.fetch_latest_news(section='technology', limit=5)

for article in articles:
    print(f"Title: {article.get('title')}")
    print(f"Image: {pipeline.get_article_image_url(article)}")
    print(f"Caption: {pipeline.create_instagram_caption(article)[:100]}...")
    print("-" * 60)
```

### Post a Single Article Manually

```python
from server import NewsToInstagramPipeline

pipeline = NewsToInstagramPipeline()

# Fetch articles
articles = pipeline.fetch_latest_news(section='business', limit=5)

# Post the first one
if articles:
    success = pipeline.post_article_to_instagram(articles[0])
    print(f"Posted: {success}")
```

## 🔧 Configuration Options

Edit `.env` to customize:

```env
# How many posts per cycle
MAX_POSTS_PER_CYCLE=2

# Wait time between posts (seconds)
POST_INTERVAL_SECONDS=60

# Schedule frequency (hours)
SCHEDULE_HOME_HOURS=4
SCHEDULE_TECH_HOURS=6
SCHEDULE_BUSINESS_HOURS=8

# Caption limits
MAX_CAPTION_LENGTH=500
MAX_ABSTRACT_LENGTH=150
```

## 📊 View Statistics

```python
from database import BackInstaDB
from config import Config

db = BackInstaDB(Config.MONGODB_URI)
stats = db.get_stats()

print(f"Total posts: {stats['total_posts']}")
print(f"By section: {stats['sections']}")

# See recent posts
recent = db.get_posted_articles(limit=10)
for post in recent:
    print(f"{post['article_title']} - {post['instagram_url']}")
```

## 🚨 Troubleshooting

### "No articles found"
- Check Webstory backend is running
- Try different section: `'home'`, `'technology'`, `'business'`
- Check `WEBSTORY_API_URL` in `.env`

### "Instagram posting failed"
- Verify `REACT_APP_ACCESS_TOKEN` is valid
- Check token hasn't expired
- Verify account ID is correct
- Ensure image URLs are publicly accessible

### "Import errors"
- Install dependencies: `pip install -r requirements.txt`
- Create `.env` file from `.env.example`

## 📝 Available News Sections

- `home` - Top stories
- `technology` - Tech news
- `business` - Business & finance
- `politics` - Political news
- `sports` - Sports updates
- `entertainment` - Entertainment news

## 🔍 Logs & Monitoring

The server provides detailed logging:

```
2025-10-21 10:30:00 - INFO - 📰 Fetching articles from section: technology
2025-10-21 10:30:02 - INFO - ✅ Fetched 8 articles
2025-10-21 10:30:03 - INFO - 🚀 Processing article: AI Breakthrough
2025-10-21 10:30:08 - INFO - 🎉 Successfully posted to Instagram: ABC123
```

## 🎨 Caption Format Example

```
📰 Revolutionary AI System Transforms Healthcare

Researchers have developed a groundbreaking AI system 
that can detect diseases with 99% accuracy...

#Technology #News #BreakingNews #Viral

🔗 Read more: https://nytimes.com/2025/...
```

## 🔐 Security Checklist

- ✅ Never commit `.env` file
- ✅ Keep access tokens private
- ✅ Rotate tokens regularly
- ✅ Monitor API usage limits
- ✅ Use `.gitignore` to exclude sensitive files

## 🆘 Quick Help

**Test everything first:**
```bash
python test.py
```

**Start with dry run:**
Check what will be posted before going live

**Monitor the first posts:**
Watch the logs to ensure everything works

**Check Instagram:**
Verify posts appear correctly on your account

---

**Ready to Go?**

```bash
# 1. Test
python test.py

# 2. Start
python server.py
```

🎉 **Your news-to-Instagram pipeline is ready!**
