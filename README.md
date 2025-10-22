# BackInsta - News to Instagram Automation

Automated backend service that fetches news articles from Webstory backend and posts them to Instagram using QPost's posting functionality.

## 🎯 Features

- **Automated News Fetching**: Fetches latest news articles from Webstory backend API
- **Instagram Integration**: Posts articles to Instagram using QPost's proven posting pipeline
- **Smart Caption Generation**: Creates engaging, Instagram-friendly captions from article data
- **Image Processing**: Extracts and posts article images
- **Duplicate Prevention**: Tracks posted articles to avoid duplicates
- **Scheduled Posting**: Automated posting on a configurable schedule
- **Multiple Sections**: Supports different news sections (home, technology, business, politics, etc.)

## 📋 Prerequisites

- Python 3.8 or higher
- Instagram Business Account
- Facebook Graph API Access Token
- Access to Webstory backend API
- QPost backend running (optional, for buffer-based posting)

## 🚀 Quick Start

### 1. Installation

```bash
cd backinsta
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Instagram API Credentials (Required)
REACT_APP_ACCESS_TOKEN=your_instagram_access_token_here
REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_account_id

# Webstory API URL
WEBSTORY_API_URL=https://webstory-frontend.vercel.app/api

# QPost API URL (if using buffer method)
QPOST_API_URL=http://localhost:8000/api
```

### 3. Run the Service

```bash
python server.py
```

## 🔧 How It Works

### Pipeline Flow

1. **Fetch Articles**: Retrieves latest news articles from Webstory backend
   ```
   GET /api/articles/section/{section}?limit=10
   ```

2. **Process Article**: Extracts title, abstract, image, and URL

3. **Create Caption**: Generates Instagram-friendly caption with:
   - Article title
   - Short abstract (150 chars)
   - Relevant hashtags
   - Source link

4. **Post to Instagram**: Uses Instagram Graph API to:
   - Create media object with image URL and caption
   - Publish post to Instagram feed

5. **Track Posted**: Marks article as posted to prevent duplicates

### Scheduling

Default schedule:
- **Home section**: Every 4 hours (2 posts)
- **Technology**: Every 6 hours (2 posts)  
- **Business**: Every 8 hours (2 posts)

Customize in `server.py`:
```python
schedule.every(4).hours.do(pipeline.run_posting_cycle, section='home', max_posts=2)
```

## 📊 API Endpoints Used

### Webstory Backend
- `GET /api/articles/section/{section}?limit={limit}` - Fetch articles by section
- `GET /api/articles?limit={limit}` - Fetch all articles

### Instagram Graph API
- `POST /v18.0/{account_id}/media` - Create media object
- `POST /v18.0/{account_id}/media_publish` - Publish post

### QPost Backend (Optional)
- `POST /api/buffer` - Store media in buffer
- `POST /api/post` - Post from buffer

## 🎨 Caption Format

Example generated caption:

```
📰 Breaking: New AI Technology Revolutionizes Healthcare

Researchers have developed a groundbreaking AI system that can detect diseases with 99% accuracy...

#Technology #News #BreakingNews #Viral

🔗 Read more: https://nytimes.com/2025/10/21/technol...
```

## 🔍 Article Selection Criteria

Articles are selected based on:
- Recent publication date (from latest API fetch)
- Availability of high-quality images
- Not previously posted (tracked in memory)
- Valid article data (title, URL, multimedia)

## 🛠️ Advanced Configuration

### Posting Intervals

Adjust rate limiting between posts:

```python
# In server.py, modify sleep time
time.sleep(60)  # Wait 60 seconds between posts
```

### Caption Customization

Modify `create_instagram_caption()` method:

```python
def create_instagram_caption(self, article: Dict) -> str:
    title = article.get('title', 'Breaking News')
    # Customize your caption format here
    caption = f"🔥 {title}\n\n"
    # Add more customization...
    return caption
```

### Section Selection

Available sections:
- `home` - Top stories
- `technology` - Tech news
- `business` - Business & finance
- `politics` - Political news
- `sports` - Sports updates
- `entertainment` - Entertainment news

## 📈 Monitoring & Logs

The service provides detailed logging:

```
2025-10-21 10:30:00 - INFO - 🚀 BackInsta - News to Instagram Automation
2025-10-21 10:30:01 - INFO - 📰 Fetching 10 articles from section: technology
2025-10-21 10:30:02 - INFO - ✅ Fetched 8 articles
2025-10-21 10:30:03 - INFO - 🚀 Processing article: AI Breakthrough in Medicine
2025-10-21 10:30:04 - INFO - 📤 Posting to Instagram (direct method)...
2025-10-21 10:30:08 - INFO - 🎉 Successfully posted to Instagram: ABC123
2025-10-21 10:30:08 - INFO - 📸 Post ID: ABC123
2025-10-21 10:30:08 - INFO - 🔗 Instagram URL: https://www.instagram.com/p/ABC123/
```

## 🐛 Troubleshooting

### No Articles Found
- Verify Webstory backend is running
- Check `WEBSTORY_API_URL` in `.env`
- Try different section names

### Instagram Posting Fails
- Verify access token is valid and not expired
- Check Instagram account ID is correct
- Ensure image URLs are publicly accessible
- Verify Instagram API limits not exceeded

### Image Download Errors
- Check article has multimedia field
- Verify image URLs are valid and accessible
- Check network connectivity

## 🔐 Security Best Practices

1. **Never commit `.env` file** - Use `.env.example` instead
2. **Rotate access tokens regularly** - Instagram tokens expire
3. **Monitor API usage** - Stay within Instagram rate limits
4. **Use environment variables** - Don't hardcode credentials

## 📝 Example Usage

### Manual Test Run

```python
from server import NewsToInstagramPipeline

# Initialize pipeline
pipeline = NewsToInstagramPipeline()

# Post one article from technology section
pipeline.run_posting_cycle(section='technology', max_posts=1)
```

### Custom Article Posting

```python
# Fetch articles manually
articles = pipeline.fetch_latest_news(section='business', limit=5)

# Post specific article
if articles:
    success = pipeline.post_article_to_instagram(articles[0])
    print(f"Posted: {success}")
```

## 🚀 Deployment

### As a Background Service (Linux)

Create systemd service file `/etc/systemd/system/backinsta.service`:

```ini
[Unit]
Description=BackInsta News to Instagram Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/QPost/backinsta
ExecStart=/usr/bin/python3 server.py
Restart=always
Environment="PATH=/usr/bin:/usr/local/bin"
EnvironmentFile=/path/to/QPost/backinsta/.env

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable backinsta
sudo systemctl start backinsta
sudo systemctl status backinsta
```

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "server.py"]
```

Build and run:
```bash
docker build -t backinsta .
docker run -d --env-file .env --name backinsta backinsta
```

## 📊 Performance Metrics

- **Fetch Speed**: ~1-2 seconds per API call
- **Post Speed**: ~5-8 seconds per Instagram post
- **Processing**: ~10-15 seconds per article (end-to-end)
- **Memory**: ~50-100 MB typical usage

## 🤝 Integration with QPost

BackInsta seamlessly integrates with QPost's Instagram posting infrastructure:

1. Uses same Instagram credentials from QPost
2. Can leverage QPost's buffer system (optional)
3. Follows QPost's caption sanitization rules
4. Compatible with QPost's MongoDB storage

## 📚 Architecture

```
┌─────────────────┐
│ Webstory Backend│
│   (News API)    │
└────────┬────────┘
         │
         │ Fetch Articles
         ▼
┌─────────────────┐
│   BackInsta     │
│   Pipeline      │
│                 │
│ • Fetch News    │
│ • Create Caption│
│ • Process Image │
└────────┬────────┘
         │
         │ Post Content
         ▼
┌─────────────────┐
│  Instagram API  │
│  (Graph API)    │
└─────────────────┘
```

## 📄 License

This project is part of the QPost ecosystem.

## 🙏 Credits

- **Webstory Backend**: News aggregation and API
- **QPost**: Instagram posting infrastructure
- **Instagram Graph API**: Social media publishing

## 🆘 Support

For issues or questions:
1. Check troubleshooting section
2. Review logs for error details
3. Verify configuration in `.env`
4. Test Webstory API availability
5. Validate Instagram credentials

---

**Made with ❤️ for automated social media management**
