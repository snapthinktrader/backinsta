#!/bin/bash

# Deploy to Render using CLI
# Make sure you have Render CLI installed: npm install -g render-cli

echo "🚀 Deploying Instagram Auto-Poster to Render..."
echo "================================================"
echo ""

# Check if render CLI is installed
if ! command -v render &> /dev/null; then
    echo "❌ Render CLI not found!"
    echo "📦 Install it with: npm install -g render-cli"
    echo "Or use: curl -fsSL https://render.com/install-cli.sh | bash"
    exit 1
fi

# Check if logged in
echo "🔐 Checking Render authentication..."
if ! render whoami &> /dev/null; then
    echo "❌ Not logged in to Render"
    echo "🔑 Please login with: render login"
    exit 1
fi

echo "✅ Authenticated"
echo ""

# Create .env file template if it doesn't exist
if [ ! -f .env ]; then
    echo "⚠️ .env file not found. Creating template..."
    cat > .env << EOF
REACT_APP_ACCESS_TOKEN=your_instagram_access_token_here
REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_account_id_here
GROQ_API_KEY=your_groq_api_key_here
IMGBB_API_KEY=your_imgbb_api_key_here
WEBSTORY_MONGODB_URI=mongodb+srv://ajay26:Ajtiwari26@cluster0.pfudopf.mongodb.net/webstory?retryWrites=true&w=majority&appName=Cluster0
MONGODB_URI=mongodb+srv://aj:aj@qpost.lk5htbl.mongodb.net/?retryWrites=true&w=majority&appName=qpost
EOF
    echo "✅ .env template created. Please update with your credentials."
fi

# Load environment variables
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Create service using render.yaml
echo "🔧 Creating/Updating Render service..."
render services create --yaml render.yaml

# Set environment variables
echo "🔑 Setting environment variables..."
render env set REACT_APP_ACCESS_TOKEN="$REACT_APP_ACCESS_TOKEN"
render env set REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID="$REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID"
render env set GROQ_API_KEY="$GROQ_API_KEY"
render env set IMGBB_API_KEY="$IMGBB_API_KEY"

echo ""
echo "✅ Deployment configuration complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Go to https://dashboard.render.com"
echo "   2. Find your 'instagram-auto-poster' service"
echo "   3. Verify environment variables are set"
echo "   4. The service will start automatically and post every 15 minutes"
echo ""
echo "🔍 Monitor logs with: render logs instagram-auto-poster"
echo ""
