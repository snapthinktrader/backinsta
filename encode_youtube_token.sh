#!/bin/bash
# Encode YouTube token files to base64 for environment variables
# Use this after regenerating the token locally

echo "=================================================="
echo "YouTube Token Base64 Encoder"
echo "=================================================="
echo ""

# Check if files exist
if [ ! -f "youtube_credentials.json" ]; then
    echo "❌ Error: youtube_credentials.json not found"
    exit 1
fi

if [ ! -f "youtube_token.pickle" ]; then
    echo "❌ Error: youtube_token.pickle not found"
    echo "💡 Run: python3 regenerate_youtube_token.py first"
    exit 1
fi

echo "✅ Found youtube_credentials.json"
echo "✅ Found youtube_token.pickle"
echo ""

# Encode credentials
echo "📦 Encoding youtube_credentials.json..."
CREDENTIALS_BASE64=$(base64 -i youtube_credentials.json)
echo "YOUTUBE_CREDENTIALS_BASE64=${CREDENTIALS_BASE64}"
echo ""

# Encode token
echo "📦 Encoding youtube_token.pickle..."
TOKEN_BASE64=$(base64 -i youtube_token.pickle)
echo "YOUTUBE_TOKEN_BASE64=${TOKEN_BASE64}"
echo ""

# Save to file
echo "💾 Saving to youtube_env_vars.txt..."
cat > youtube_env_vars.txt << EOF
# Copy these to your Render/deployment environment variables
YOUTUBE_CREDENTIALS_BASE64=${CREDENTIALS_BASE64}
YOUTUBE_TOKEN_BASE64=${TOKEN_BASE64}
EOF

echo "=================================================="
echo "✅ SUCCESS! Environment variables saved to:"
echo "   youtube_env_vars.txt"
echo ""
echo "📋 Next steps:"
echo "   1. Open youtube_env_vars.txt"
echo "   2. Copy the values to your deployment platform"
echo "   3. Restart your deployment"
echo "=================================================="
