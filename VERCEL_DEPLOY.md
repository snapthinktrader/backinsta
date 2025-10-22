# 🚀 Deploy to Vercel - Complete Guide

## ✅ Prerequisites

The code is ready on GitHub: https://github.com/snapthinktrader/backinsta

## 📦 What's Configured

- **Vercel Cron Job**: Runs every 15 minutes (`*/15 * * * *`)
- **Serverless Function**: `/api/cron-post` endpoint
- **Python Runtime**: Automatic detection
- **Environment Variables**: Will be configured in Vercel dashboard

## 🚀 Deploy Steps

### Option 1: Using Vercel CLI (Recommended)

1. **Install Vercel CLI** (if not installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from backinsta directory**:
   ```bash
   cd /Users/mahendrabahubali/Desktop/QPost/backinsta
   vercel
   ```

4. **Follow prompts**:
   - Set up and deploy? `Y`
   - Which scope? Select your account
   - Link to existing project? `N`
   - Project name? `instagram-auto-poster` (or your choice)
   - In which directory is your code located? `./`
   - Want to override settings? `N`

5. **Deploy to production**:
   ```bash
   vercel --prod
   ```

### Option 2: Using Vercel Dashboard

1. **Go to**: https://vercel.com/new

2. **Import Git Repository**:
   - Click "Import Git Repository"
   - Connect GitHub if not connected
   - Select: `snapthinktrader/backinsta`

3. **Configure Project**:
   - **Project Name**: `instagram-auto-poster`
   - **Framework Preset**: Other
   - **Root Directory**: `./`
   - **Build Command**: Leave empty (serverless functions)
   - **Output Directory**: Leave empty

4. **Add Environment Variables** (before deploying):
   Click "Environment Variables" and add:

   ```
   REACT_APP_ACCESS_TOKEN=<your_instagram_token>
   REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID=17841477569192718
   GROQ_API_KEY=<your_groq_api_key>
   IMGBB_API_KEY=<your_imgbb_api_key>
   WEBSTORY_MONGODB_URI=mongodb+srv://ajay26:Ajtiwari26@cluster0.pfudopf.mongodb.net/webstory
   MONGODB_URI=mongodb+srv://aj:aj@qpost.lk5htbl.mongodb.net/
   ```

5. **Click "Deploy"**

## 🔧 Configure Environment Variables (CLI Method)

After deployment, set environment variables:

```bash
vercel env add REACT_APP_ACCESS_TOKEN
# Paste your token when prompted

vercel env add REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID
# Enter: 17841477569192718

vercel env add GROQ_API_KEY
# Paste your Groq API key

vercel env add IMGBB_API_KEY
# Paste your imgbb API key

vercel env add WEBSTORY_MONGODB_URI
# Enter: mongodb+srv://ajay26:Ajtiwari26@cluster0.pfudopf.mongodb.net/webstory

vercel env add MONGODB_URI
# Enter: mongodb+srv://aj:aj@qpost.lk5htbl.mongodb.net/
```

Then redeploy:
```bash
vercel --prod
```

## ⏰ Vercel Cron Configuration

The cron job is configured in `vercel.json`:
```json
"crons": [
  {
    "path": "/api/cron-post",
    "schedule": "*/15 * * * *"  // Every 15 minutes
  }
]
```

**Note**: Cron jobs are only available on:
- ✅ **Hobby Plan**: Up to 2 cron jobs (FREE)
- ✅ **Pro Plan**: Unlimited cron jobs

## 📊 Monitor Deployment

### View Logs:
```bash
vercel logs instagram-auto-poster
```

### Or in Dashboard:
1. Go to https://vercel.com/dashboard
2. Select your project
3. Click "Deployments"
4. Click on latest deployment
5. View "Functions" tab for cron execution logs

## 🧪 Test Cron Job Manually

You can trigger the cron job manually to test:

```bash
curl https://your-project.vercel.app/api/cron-post
```

## 🔍 Verify It's Working

After deployment, check:
1. ✅ Deployment successful (green checkmark)
2. ✅ Function `/api/cron-post` exists
3. ✅ Cron job scheduled (visible in project settings)
4. ✅ Environment variables set
5. ✅ Instagram posts appearing every 15 minutes

## 📝 Important Notes

### Cron Job Limits (Free Hobby Plan):
- **Max 2 cron jobs** per project
- **1 minute minimum interval** (we use 15 minutes)
- **10 second max execution time** per invocation (we set 300s)

### If You Hit Limits:
Upgrade to Pro plan or use alternative:
- Run cron on your local machine
- Use GitHub Actions for scheduled posting
- Use other platforms like Railway, Fly.io

## 🚨 Troubleshooting

### Function timeout:
- Increase `maxDuration` in `vercel.json` (requires Pro plan for >10s)

### Environment variables not loading:
```bash
vercel env ls
vercel env pull .env.local
```

### Cron not triggering:
- Check project settings → Cron Jobs
- Verify you're on Hobby or Pro plan
- Check function logs for errors

## 🎯 Expected Behavior

Once deployed:
1. ✅ Vercel cron runs every 15 minutes
2. ✅ Fetches latest article from Webstory MongoDB
3. ✅ Creates text overlay with improved spacing
4. ✅ Generates AI commentary
5. ✅ Posts to Instagram
6. ✅ Saves to database to prevent duplicates
7. ✅ Tries different sections if one fails

## 🔄 Update Deployment

Make changes and redeploy:
```bash
git add .
git commit -m "Update message"
git push origin main

# Vercel auto-deploys on push, or manually:
vercel --prod
```

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Green deployment status on Vercel
- ✅ New Instagram posts every 15 minutes
- ✅ Function logs show successful execution
- ✅ Database shows tracked articles

## 📞 Support

- **Vercel Docs**: https://vercel.com/docs/cron-jobs
- **Project URL**: Check in Vercel dashboard
- **Logs**: `vercel logs` or dashboard
