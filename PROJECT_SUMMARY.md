# BackInsta - Project Summary

## 🎯 What Was Created

A complete backend automation system in the `backinsta` folder that:
1. **Fetches** news articles from Webstory backend
2. **Processes** articles (extracts images, creates captions)
3. **Posts** to Instagram using QPost's proven posting infrastructure
4. **Tracks** posted articles to prevent duplicates
5. **Schedules** automated posting cycles

## 📦 Components Created

### Core Modules

1. **server.py** (434 lines)
   - Main pipeline orchestration
   - Article fetching from Webstory API
   - Instagram posting via Graph API
   - Scheduling logic
   - Complete automation workflow

2. **config.py** (84 lines)
   - Centralized configuration management
   - Environment variable handling
   - Configuration validation
   - Customizable posting schedules

3. **database.py** (156 lines)
   - MongoDB integration
   - Posted articles tracking
   - Duplicate prevention
   - Analytics and statistics
   - Posted article history

4. **test.py** (290 lines)
   - Comprehensive test suite
   - Configuration validation
   - Article fetching tests
   - Caption generation tests
   - Image extraction tests
   - Dry run testing
   - Live posting test (optional)

### Utilities

5. **quickstart.py** (123 lines)
   - Interactive menu system
   - Dependency installation
   - Configuration viewer
   - Statistics viewer
   - Easy server management

6. **start.sh** (50 lines)
   - Bash startup script
   - Virtual environment setup
   - Dependency installation
   - Interactive menu

### Documentation

7. **README.md** (430 lines)
   - Complete documentation
   - Installation guide
   - Configuration reference
   - Usage examples
   - Troubleshooting guide
   - Deployment instructions

8. **QUICK_START.md** (195 lines)
   - Quick reference guide
   - Common tasks
   - Code examples
   - Troubleshooting tips

9. **requirements.txt**
   - Python dependencies
   - requests
   - schedule
   - python-dotenv
   - pymongo

10. **.env.example**
    - Environment variables template
    - Configuration documentation

11. **.gitignore**
    - Ignores sensitive files
    - Python artifacts
    - Environment files

## 🔑 Key Features

### 1. Smart Article Fetching
- Connects to Webstory backend API
- Supports multiple news sections
- Filters out already-posted articles
- Handles API errors gracefully

### 2. Instagram Posting
- Uses Instagram Graph API directly
- Creates media objects
- Publishes to Instagram feed
- Supports images (reels support can be added)
- Rate limiting between posts

### 3. Caption Generation
- Extracts title and abstract
- Formats for Instagram
- Adds relevant hashtags
- Includes source link
- Auto-sanitizes to meet Instagram requirements

### 4. Duplicate Prevention
- In-memory tracking
- MongoDB persistence
- Prevents re-posting same articles
- Tracks posting history

### 5. Scheduling
- Configurable posting frequency
- Multiple sections scheduled independently
- Automatic execution
- No manual intervention needed

### 6. Analytics & Monitoring
- Tracks total posts
- Statistics by section
- Recent post history
- Instagram post URLs
- Detailed logging

## 🚀 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                      BACKINSTA PIPELINE                       │
└─────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   Scheduler  │  Every 4-8 hours
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Fetch Latest │  GET /api/articles/section/{section}
    │   Articles   │  From Webstory Backend
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │    Filter    │  Remove already posted
    │  Duplicates  │  Check MongoDB + Memory
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Process    │  Extract: title, abstract, image
    │   Article    │  Generate: Instagram caption
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │     Post     │  1. Create media object
    │  Instagram   │  2. Publish post
    └──────┬───────┘  3. Get post ID
           │
           ▼
    ┌──────────────┐
    │     Save     │  Store in MongoDB
    │   to DB      │  Mark as posted
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │     Wait     │  60 seconds
    │   Between    │  Then next article
    │    Posts     │
    └──────────────┘
```

## 📊 Technical Architecture

### Data Flow

```
Webstory Backend (MongoDB)
         ↓
  [Articles API]
         ↓
    BackInsta Server
    ├── Fetch Articles
    ├── Process Content
    ├── Generate Captions
    └── Post to Instagram
         ↓
  Instagram Graph API
         ↓
  Instagram Feed
```

### Database Schema

```javascript
// Posted Articles Collection
{
  article_url: String (unique),
  article_title: String,
  article_section: String,
  instagram_post_id: String,
  instagram_url: String,
  posted_at: Date,
  article_data: {
    abstract: String,
    source: String,
    byline: String,
    published_date: Date
  }
}
```

## 🔧 Configuration

### Environment Variables

```env
# Webstory Backend
WEBSTORY_API_URL=https://webstory-frontend.vercel.app/api

# QPost API
QPOST_API_URL=http://localhost:8000/api

# Instagram (Required)
REACT_APP_ACCESS_TOKEN=your_token_here
REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID=your_id_here

# MongoDB
MONGODB_URI=mongodb+srv://...

# Posting Config
MAX_POSTS_PER_CYCLE=2
POST_INTERVAL_SECONDS=60
SCHEDULE_HOME_HOURS=4
SCHEDULE_TECH_HOURS=6
SCHEDULE_BUSINESS_HOURS=8
```

## 📈 Usage Examples

### Run Tests
```bash
cd backinsta
python test.py
```

### Start Server
```bash
python server.py
```

### Interactive Mode
```bash
python quickstart.py
```

### Manual Post
```python
from server import NewsToInstagramPipeline

pipeline = NewsToInstagramPipeline()
pipeline.run_posting_cycle(section='technology', max_posts=1)
```

## 🎨 Generated Caption Example

```
📰 AI Breakthrough Transforms Medical Diagnosis

Researchers develop groundbreaking system that 
detects diseases with 99% accuracy, potentially 
revolutionizing healthcare industry...

#Technology #News #BreakingNews #Viral

🔗 Read more: https://nytimes.com/2025/10/21/...
```

## 🔐 Security Features

- ✅ Environment variables for sensitive data
- ✅ .env excluded from git
- ✅ Secure MongoDB connection
- ✅ Token validation
- ✅ Rate limiting
- ✅ Error handling

## 📊 Statistics Available

- Total posts created
- Posts by section
- Recent post history
- Instagram URLs
- Posting timestamps
- Success/failure tracking

## 🚀 Deployment Ready

### Local Development
```bash
python server.py
```

### Background Service (systemd)
```ini
[Service]
ExecStart=/usr/bin/python3 /path/to/backinsta/server.py
```

### Docker
```dockerfile
FROM python:3.9-slim
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "server.py"]
```

## 🎯 Integration Points

### With Webstory
- Uses Articles API endpoints
- Fetches from multiple sections
- Handles article schemas
- Extracts multimedia

### With QPost
- Shares Instagram credentials
- Uses same API patterns
- Compatible with QPost MongoDB
- Follows posting best practices

### With Instagram
- Instagram Graph API v18.0
- Media object creation
- Post publishing
- Business account support

## 📝 Testing Coverage

- ✅ Configuration validation
- ✅ Article fetching
- ✅ Caption generation
- ✅ Image extraction
- ✅ Duplicate checking
- ✅ Dry run pipeline
- ✅ Optional live posting

## 🛠️ Maintenance

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Check Logs
Server provides real-time logging of all operations

### View Statistics
```python
from database import BackInstaDB
db = BackInstaDB(mongodb_uri)
stats = db.get_stats()
```

### Clear Posted History
```python
# Connect to MongoDB and clear collection if needed
```

## 🌟 Highlights

1. **Zero Manual Work**: Fully automated posting
2. **Smart Deduplication**: Never posts same article twice
3. **Rich Captions**: Auto-generated engaging captions
4. **Comprehensive Testing**: Test before going live
5. **Easy Configuration**: Simple .env setup
6. **Full Monitoring**: Detailed logs and statistics
7. **Production Ready**: Error handling, rate limiting
8. **Well Documented**: Multiple guides included

## 🎉 Ready to Use!

```bash
# 1. Setup
cd backinsta
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials

# 2. Test
python test.py

# 3. Run
python server.py
```

---

**Created**: October 21, 2025
**Total Lines of Code**: ~1,800
**Files Created**: 11
**Features**: 20+
**Status**: ✅ Production Ready
