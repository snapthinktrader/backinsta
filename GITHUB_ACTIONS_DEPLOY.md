# 🚀 GitHub Actions Deployment Guide

## ✅ What's Configured

- **Schedule**: Every 15 minutes (`*/15 * * * *`)
- **Platform**: GitHub Actions (100% FREE)
- **Manual Trigger**: Can trigger manually from Actions tab
- **No Server Needed**: Runs on GitHub's infrastructure

## 📦 Setup Steps

### 1. Push Code to GitHub (Already Done! ✅)

Your code is at: https://github.com/snapthinktrader/backinsta

### 2. Add GitHub Secrets

Go to your repository settings and add secrets:

**URL**: https://github.com/snapthinktrader/backinsta/settings/secrets/actions

Click **"New repository secret"** and add each of these:

| Secret Name | Value |
|-------------|-------|
| `REACT_APP_ACCESS_TOKEN` | Your Instagram access token |
| `REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID` | `17841477569192718` |
| `GROQ_API_KEY` | Your Groq API key |
| `IMGBB_API_KEY` | Your imgbb API key |
| `WEBSTORY_MONGODB_URI` | `mongodb+srv://ajay26:Ajtiwari26@cluster0.pfudopf.mongodb.net/webstory` |
| `MONGODB_URI` | `mongodb+srv://aj:aj@qpost.lk5htbl.mongodb.net/` |

### 3. Enable GitHub Actions

1. Go to: https://github.com/snapthinktrader/backinsta/actions
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. You should see the workflow: **"Instagram Auto-Poster"**

### 4. Test Manual Run (Optional)

Before waiting for the schedule, test it manually:

1. Go to: https://github.com/snapthinktrader/backinsta/actions
2. Click on **"Instagram Auto-Poster"** workflow
3. Click **"Run workflow"** button
4. Click **"Run workflow"** in the dropdown
5. Watch it run and check the logs

### 5. Monitor Automated Runs

The workflow will run automatically every 15 minutes:
- ⏰ Next run: Check the Actions tab for next scheduled time
- 📊 History: View all past runs in the Actions tab
- 🔍 Logs: Click any run to see detailed logs

## 🎯 How It Works

Every 15 minutes, GitHub Actions will:
1. ✅ Spin up a fresh Ubuntu VM
2. ✅ Install Python and dependencies
3. ✅ Fetch latest article from Webstory
4. ✅ Create text overlay (28% height, no branding)
5. ✅ Generate AI commentary
6. ✅ Post to Instagram
7. ✅ Save to database (prevent duplicates)
8. ✅ Try different sections if one fails

## 📊 GitHub Actions Limits (Free Tier)

- ✅ **2,000 minutes/month** of runtime (plenty for this!)
- ✅ **Unlimited public repositories**
- ✅ **No credit card required**
- ✅ Each run takes ~1-2 minutes = ~2,880 minutes/month needed
- ⚠️ You may hit the limit if running every 15 min 24/7

### If You Hit Limits:

**Option 1**: Reduce frequency (e.g., every 30 minutes)
- Edit `.github/workflows/instagram-poster.yml`
- Change `*/15 * * * *` to `*/30 * * * *`

**Option 2**: Run only during active hours
```yaml
# Run every 15 min from 8 AM to 8 PM UTC
- cron: '*/15 8-20 * * *'
```

**Option 3**: Use multiple repositories (each gets 2000 min)

## 🔧 Customize Schedule

Edit `.github/workflows/instagram-poster.yml`:

```yaml
# Every 15 minutes (current)
- cron: '*/15 * * * *'

# Every 30 minutes
- cron: '*/30 * * * *'

# Every hour
- cron: '0 * * * *'

# Every 2 hours
- cron: '0 */2 * * *'

# Every day at 9 AM UTC
- cron: '0 9 * * *'

# Every 15 min, 9 AM to 5 PM UTC, Mon-Fri
- cron: '*/15 9-17 * * 1-5'
```

[Cron syntax help](https://crontab.guru/)

## 🐛 Troubleshooting

### Workflow not running?
1. Check if Actions are enabled in repo settings
2. Verify secrets are set correctly
3. Check workflow file syntax (YAML is strict)
4. Look for errors in Actions tab

### Posts failing?
1. Click on failed run in Actions tab
2. Read the logs to see error
3. Common issues:
   - Instagram token expired
   - No articles available
   - MongoDB connection issues

### Hit GitHub Actions limits?
1. Check usage: Settings → Billing → Plans and usage
2. Reduce posting frequency
3. Or use Render/Railway instead

## 📈 Monitor Usage

Check your GitHub Actions usage:
1. Go to: https://github.com/settings/billing
2. Click "Plans and usage"
3. See "Actions" usage bar
4. Track minutes used vs limit

## ✅ Success Indicators

You'll know it's working when:
- ✅ Actions tab shows green checkmarks
- ✅ New Instagram posts every 15 minutes
- ✅ Workflow runs visible in Actions history
- ✅ Database tracking articles

## 🔄 Update Workflow

Make changes and push:
```bash
cd /Users/mahendrabahubali/Desktop/QPost/backinsta
# Edit .github/workflows/instagram-poster.yml
git add .github/workflows/instagram-poster.yml
git commit -m "Update workflow schedule"
git push origin main
```

Changes take effect immediately!

## 🎉 Advantages of GitHub Actions

- ✅ **100% Free** for public repos
- ✅ **No server needed** - runs in the cloud
- ✅ **Automatic updates** - just push to main
- ✅ **Built-in logging** - see all runs
- ✅ **Manual triggers** - test anytime
- ✅ **Reliable** - GitHub's infrastructure
- ✅ **Easy to pause** - disable workflow anytime

## 📞 Support

- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **Workflow Syntax**: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- **Cron Schedule**: https://crontab.guru/

## 🚀 You're All Set!

Just push this to GitHub and add your secrets. It will start posting automatically every 15 minutes! 🎊
