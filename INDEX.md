# 🚀 BackInsta - News to Instagram Automation

> Automated backend that fetches news from Webstory and posts to Instagram

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📚 Documentation Index

- **[README.md](README.md)** - Complete documentation with all features
- **[QUICK_START.md](QUICK_START.md)** - Quick reference guide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Technical overview

## ⚡ Quick Start

```bash
# 1. Setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Instagram credentials

# 2. Test
python test.py

# 3. Run
python server.py
```

## 🎯 What It Does

1. ✅ Fetches latest news from Webstory backend
2. ✅ Generates Instagram-friendly captions
3. ✅ Posts to Instagram automatically
4. ✅ Prevents duplicate posts
5. ✅ Runs on schedule (every 4-8 hours)
6. ✅ Tracks analytics in MongoDB

## 📂 Files

| File | Purpose |
|------|---------|
| `server.py` | Main automation server |
| `config.py` | Configuration management |
| `database.py` | MongoDB integration |
| `test.py` | Test suite |
| `quickstart.py` | Interactive menu |
| `start.sh` | Bash startup script |

## 🔧 Requirements

- Python 3.8+
- Instagram Business Account
- Facebook Graph API Access Token
- MongoDB (optional, for tracking)
- Webstory backend running

## 📸 Example Output

```
2025-10-21 10:30:00 - INFO - 📰 Fetching articles from technology
2025-10-21 10:30:02 - INFO - ✅ Fetched 8 articles
2025-10-21 10:30:03 - INFO - 🚀 Processing: AI Breakthrough
2025-10-21 10:30:08 - INFO - 🎉 Posted to Instagram: ABC123
2025-10-21 10:30:08 - INFO - 🔗 https://instagram.com/p/ABC123/
```

## 🤝 Integration

- **Webstory Backend**: News source
- **QPost**: Instagram posting infrastructure
- **Instagram Graph API**: Publishing platform

## 📊 Statistics

```python
from database import BackInstaDB
db = BackInstaDB(mongodb_uri)
stats = db.get_stats()
# {'total_posts': 45, 'sections': {'technology': 15, 'business': 12, ...}}
```

## 🆘 Support

See [README.md](README.md) for:
- Detailed installation
- Configuration options
- Troubleshooting
- Deployment guide

## 📝 License

Part of the QPost ecosystem.

---

**Made with ❤️ for automated social media**
