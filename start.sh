#!/bin/bash
# BackInsta Startup Script

echo "🚀 BackInsta - News to Instagram Automation"
echo "==========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env created. Please edit it with your credentials:"
    echo "   - REACT_APP_ACCESS_TOKEN"
    echo "   - REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Choose an option:"
echo "  1) Run tests"
echo "  2) Start server (live posting)"
echo "  3) Exit"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo "🧪 Running tests..."
        python test.py
        ;;
    2)
        echo "🚀 Starting BackInsta scheduler..."
        #!/bin/bash

# Multi-Platform News Poster - Quick Start Script
# This script starts the automated posting system for Instagram Reels and YouTube Shorts

echo "🚀 Starting Multi-Platform News Automation"
echo "=========================================="
echo ""
echo "📸 Instagram: @usdaily24"
echo "📹 YouTube: forexyynewsletter@gmail.com"
echo ""

# Set environment variables
export USE_INSTAGRAM_REELS=true
export USE_YOUTUBE_SHORTS=true
export POST_INTERVAL_MINUTES=30  # Post every 30 minutes

# Check if .env file exists in parent directory
if [ -f "../.env" ]; then
    echo "✅ Loading environment from ../.env"
    source ../.env
else
    echo "⚠️  No .env file found. Make sure you have:"
    echo "   - GROQ_API_KEY"
    echo "   - NYT_API_KEY" 
    echo "   - IMGBB_API_KEY"
    echo "   - REACT_APP_ACCESS_TOKEN"
    echo "   - REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID"
    echo "   - MONGODB_URI"
    echo ""
fi

# Get Python path
PYTHON_PATH="/Users/mahendrabahubali/.pyenv/versions/3.9.20/bin/python"

# Check if Python exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Python not found at $PYTHON_PATH"
    echo "   Using system python3..."
    PYTHON_PATH="python3"
fi

echo "🐍 Using Python: $PYTHON_PATH"
echo ""
echo "⏰ Posting interval: $POST_INTERVAL_MINUTES minutes"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Run the scheduler
$PYTHON_PATH scheduled_poster.py

        ;;
    3)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
