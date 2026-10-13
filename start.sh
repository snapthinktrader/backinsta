#!/bin/bash
# Multi-Platform News Poster - Production Start Script
# Posts to Instagram Reels (@usdaily24) and YouTube Shorts (forexyynewsletter@gmail.com)

echo "🚀 Multi-Platform News Automation"
echo "=========================================="
echo ""
echo "📸 Instagram: @usdaily24"
echo "📹 YouTube: forexyynewsletter@gmail.com"
echo ""

# Set environment variables
export USE_INSTAGRAM_REELS=true
export USE_YOUTUBE_SHORTS=true
export POST_INTERVAL_MINUTES=${POST_INTERVAL_MINUTES:-30}  # Default 30 minutes

# Check for .env file (try current directory first, then parent)
if [ -f ".env" ]; then
    echo "✅ Loading environment from .env"
    set -a
    source .env
    set +a
elif [ -f "../.env" ]; then
    echo "✅ Loading environment from ../.env"
    set -a
    source ../.env
    set +a
else
    echo "⚠️  No .env file found!"
    echo ""
    echo "Creating .env from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env created. Please edit it with your credentials:"
        echo "   - GROQ_API_KEY"
        echo "   - NYT_API_KEY"
        echo "   - IMGBB_API_KEY"
        echo "   - REACT_APP_ACCESS_TOKEN"
        echo "   - REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID"
        echo "   - MONGODB_URI"
        echo ""
        echo "Then run this script again."
        exit 1
    else
        echo "❌ .env.example not found!"
        exit 1
    fi
fi

# Detect Python path
PYTHON_PATH="/Users/mahendrabahubali/.pyenv/versions/3.9.20/bin/python"

if [ ! -f "$PYTHON_PATH" ]; then
    # Try pyenv global python
    if command -v pyenv &> /dev/null; then
        PYTHON_PATH="$(pyenv which python)"
    else
        # Fall back to system python3
        PYTHON_PATH="python3"
    fi
fi

echo "🐍 Python: $PYTHON_PATH"
echo "⏰ Posting interval: $POST_INTERVAL_MINUTES minutes"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Run the scheduler
$PYTHON_PATH scheduled_poster.py
