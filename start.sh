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
        python scheduled_poster.py
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
