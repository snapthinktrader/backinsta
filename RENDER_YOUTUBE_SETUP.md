# YouTube Setup on Render

## Step 1: Upload YouTube Files to Render

You need to upload 2 files manually to Render (they're not in git for security):

### Files to Upload:
1. **youtube_credentials.json** - OAuth2 client credentials from Google Cloud
2. **youtube_token.pickle** - Your authenticated session (already working locally)

### How to Upload to Render:

#### Option A: Using Render Shell (After Deployment)
1. Deploy your app to Render first
2. Go to Render Dashboard → Your Service → Shell tab
3. Run these commands:

```bash
# Create the files using cat (paste content when prompted)
cat > youtube_credentials.json << 'EOF'
# Paste content of youtube_credentials.json here
EOF

cat > youtube_token.pickle << 'EOF'
# Paste content of youtube_token.pickle here (binary file - may not work)
EOF
```

#### Option B: Use Environment Variables (Recommended)
Store the credentials as base64-encoded environment variables:

```bash
# On your local machine, encode the files:
cd /Users/mahendrabahubali/Desktop/QPost/backinsta

# Encode youtube_credentials.json
base64 -i youtube_credentials.json > youtube_credentials_base64.txt
cat youtube_credentials_base64.txt

# Encode youtube_token.pickle
base64 -i youtube_token.pickle > youtube_token_base64.txt
cat youtube_token_base64.txt
```

Then add to Render Environment Variables:
- `YOUTUBE_CREDENTIALS_BASE64` = (paste content from youtube_credentials_base64.txt)
- `YOUTUBE_TOKEN_BASE64` = (paste content from youtube_token_base64.txt)

## Step 2: Update Code to Decode Files on Render

The code will automatically decode these base64 strings and create the files when running on Render.

## Step 3: Render Environment Variables

Set these in Render Dashboard → Environment:

```bash
# Instagram
REACT_APP_ACCESS_TOKEN=your_instagram_token
REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID=17841477569192718

# MongoDB
MONGODB_URI=mongodb+srv://aj:aj@qpost.lk5htbl.mongodb.net/?retryWrites=true&w=majority&appName=qpost

# NYT API
NYT_API_KEY=your_nyt_api_key_here

# Groq AI
GROQ_API_KEY=your_groq_api_key_here

# Image Hosting
IMGBB_API_KEY=your_imgbb_api_key_here

# Feature Flags
USE_INSTAGRAM_REELS=true
USE_YOUTUBE_SHORTS=true
USE_BACKGROUND_AUDIO=false

# Posting Schedule
POST_INTERVAL_MINUTES=30

# YouTube Credentials (Base64 encoded)
YOUTUBE_CREDENTIALS_BASE64=(will be generated in next step)
YOUTUBE_TOKEN_BASE64=(will be generated in next step)
```

## Step 4: Render Service Configuration

```yaml
# Build Command
pip install -r requirements.txt

# Start Command
python scheduled_poster.py

# Service Type
Web Service (for health check)

# Environment
Python 3.9
```

## Step 5: Deploy

1. Push code to GitHub (already done ✅)
2. Create new Web Service on Render
3. Connect to GitHub repo: `snapthinktrader/backinsta`
4. Set environment variables
5. Deploy!

## Testing

After deployment:
1. Check Render logs for "✅ YouTube API authenticated"
2. Look for "✅ YouTube Shorts uploader initialized"
3. Watch for successful posts with video IDs

## Troubleshooting

If YouTube authentication fails:
1. Check if token.pickle is expired (refresh needed)
2. Verify YOUTUBE_CREDENTIALS_BASE64 is correctly set
3. Check Render logs for specific OAuth errors

## Alternative: Keep YouTube Local

If Render YouTube setup is too complex:
- Set `USE_YOUTUBE_SHORTS=false` on Render
- Keep YouTube running on your local Mac
- Render handles Instagram only (24/7)
- Local handles YouTube (when Mac is on)
