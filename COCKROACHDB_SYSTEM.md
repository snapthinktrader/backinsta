# CockroachDB-Based Posting System

## Overview

This system separates reel generation (local) from posting (Render server), solving the ElevenLabs free tier issue and providing better control over content.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    LOCAL (Your Mac)                      │
│                                                           │
│  generate_reels_local.py                                 │
│  • Fetch NYT articles (12-15 at a time)                  │
│  • Generate AI analysis                                  │
│  • Create voice narration (ElevenLabs)                   │
│  • Generate image with text overlay                      │
│  • Create video reel with voice                          │
│  • Save to CockroachDB                                   │
└─────────────────────────────────────────────────────────┘
                            │
                            │ Store reels
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    CockroachDB                           │
│                                                           │
│  reels table:                                            │
│  • video_data (BYTEA, 2-3MB each)                        │
│  • headline, caption, ai_analysis                        │
│  • article_id, article_url                               │
│  • status (pending/posted/failed)                        │
│  • instagram_post_id, youtube_video_id                   │
│  • created_at, posted_at                                 │
└─────────────────────────────────────────────────────────┘
                            │
                            │ Fetch one reel/hour
                            ▼
┌─────────────────────────────────────────────────────────┐
│                 RENDER SERVER (Production)               │
│                                                           │
│  scheduled_poster_cockroach.py                           │
│  • Fetch next pending reel from database                 │
│  • Upload video to hosting (Catbox/file.io)              │
│  • Post to Instagram                                     │
│  • Post to YouTube Shorts                                │
│  • Mark as posted in database                            │
│  • Repeat every 60 minutes                               │
└─────────────────────────────────────────────────────────┘
```

## Benefits

✅ **No API quotas on Render** - Voice generation happens locally  
✅ **Faster posting** - Just fetch and upload (no video processing)  
✅ **Pre-approved content** - Review reels before they go live  
✅ **Consistent quality** - All videos generated in controlled environment  
✅ **Cost effective** - Use ElevenLabs free tier locally without restrictions  
✅ **Better error handling** - Retry logic only affects posting, not generation  

## Setup

### 1. CockroachDB Setup

```bash
# Download SSL certificate
curl --create-dirs -o $HOME/.postgresql/root.crt \
  'https://cockroachlabs.cloud/clusters/4e0837d0-5b4a-4eb2-a1ec-f9531fe6247c/cert'

# Create schema
python database/cockroach_setup.py
```

### 2. Environment Variables

Add to `.env`:
```properties
# CockroachDB
COCKROACHDB_URI=postgresql://snap:zY7iXb69bunWURtTeASzhg@backinsta-17456.j77.aws-ap-south-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full

# Voice narration (local only)
USE_VOICE_NARRATION=true
elevenlabspaliapi=sk_5eb5524dc1fd9c23b383ed85b6de26448ac46a010ec0882b
ELEVENLABS_VOICE_ID=pMsXgVXv3BLzUgSXRplE

# Posting interval (Render)
POST_INTERVAL_MINUTES=60  # 1 hour between posts
```

### 3. Render Environment Variables

Add to Render dashboard:
```
COCKROACHDB_URI=postgresql://snap:zY7iXb69bunWURtTeASzhg@backinsta-17456.j77.aws-ap-south-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full
POST_INTERVAL_MINUTES=60
```

**Note:** Do NOT add ElevenLabs API key to Render (not needed anymore)

## Usage

### Local: Generate Reels

Run whenever you want to queue up content:

```bash
python generate_reels_local.py
```

This will:
1. Ask how many reels to generate (default 12)
2. Fetch fresh NYT articles
3. Generate voice narration for each
4. Create videos with voice
5. Save to CockroachDB as "pending"

**Recommended:** Generate 12-15 reels 1-2 times per week

### Render: Auto-Post Reels

The Render server runs automatically:

```bash
python scheduled_poster_cockroach.py
```

This will:
1. Fetch oldest pending reel from database
2. Post to Instagram and YouTube
3. Mark as posted (or failed)
4. Wait 60 minutes
5. Repeat

## Database Schema

```sql
CREATE TABLE reels (
    id UUID PRIMARY KEY,
    headline TEXT NOT NULL,
    caption TEXT NOT NULL,
    article_url TEXT,
    article_id TEXT UNIQUE NOT NULL,
    video_data BYTEA,              -- 2-3MB per video
    thumbnail_url TEXT,
    ai_analysis TEXT,
    duration FLOAT,
    file_size INT,
    created_at TIMESTAMP,
    posted_at TIMESTAMP,
    status TEXT,                   -- pending/posted/failed
    instagram_post_id TEXT,
    youtube_post_id TEXT,
    error_message TEXT,
    retry_count INT
);
```

## Monitoring

### Check Database Stats

```bash
python database/cockroach_setup.py
```

Shows:
- Total reels
- Pending (ready to post)
- Posted (successfully posted)
- Failed (posting failed)
- Total size (MB)
- Average duration

### Test Local Generation

```bash
python generate_reels_local.py
# Enter: 1 (generate just 1 reel for testing)
```

### Test Posting

```bash
python cockroach_poster.py
# Confirm: y (post next pending reel)
```

## Workflow Examples

### Weekly Content Generation (Recommended)

```bash
# Monday morning: Generate 12 reels
python generate_reels_local.py
# Enter: 12

# Render will auto-post 1 reel every hour
# 12 reels = 12 hours of content
# Generate more reels mid-week if needed
```

### Batch Generation for Vacation

```bash
# Generate 30 reels before vacation
python generate_reels_local.py
# Enter: 30

# Render will auto-post for 30 hours (1.25 days)
# Generate more before you leave if needed
```

## Storage Limits

**CockroachDB Free Tier:**
- Storage: 5GB
- Videos: ~2.5MB each
- Capacity: ~2000 videos (plenty!)

**Recommended:**
- Keep 20-30 pending reels at all times
- Delete old posted reels periodically (TODO: add cleanup script)

## Troubleshooting

### No pending reels

```bash
# Generate more reels locally
python generate_reels_local.py
```

### Posting failures

Check Render logs:
- Instagram rate limited → Will retry next hour
- YouTube quota exceeded → Already using 60-min interval
- Video upload failed → Catbox/file.io timeout (temporary)

### Database connection issues

```bash
# Test connection
python database/cockroach_setup.py

# Check SSL certificate
ls -la ~/.postgresql/root.crt
```

## Migration from Old System

The old system (`scheduled_poster.py`) still works but:
- ❌ Generates reels on Render (uses ElevenLabs, which is rate limited)
- ❌ Slower posting (video processing + uploading)
- ❌ No content review

New system (`scheduled_poster_cockroach.py`):
- ✅ Fetches pre-generated reels from database
- ✅ Faster posting (just upload)
- ✅ Content review before posting
- ✅ No ElevenLabs quota issues

## Files

### Local Scripts (Run on Mac)
- `generate_reels_local.py` - Generate reels with voice narration
- `database/cockroach_setup.py` - Database setup and utilities
- `test_voice_narration.py` - Test voice generation

### Production Scripts (Run on Render)
- `scheduled_poster_cockroach.py` - Main posting loop (NEW)
- `cockroach_poster.py` - Posting logic for database reels
- `scheduled_poster.py` - Legacy system (still works)

### Database Utilities
- `database/cockroach_setup.py`:
  - `get_pending_reel()` - Fetch next reel to post
  - `mark_reel_posted()` - Mark as posted
  - `mark_reel_failed()` - Mark as failed
  - `get_stats()` - Database statistics
  - `insert_reel()` - Save new reel

## Next Steps

1. ✅ Generate 12 reels locally to test
2. ✅ Update Render to use `scheduled_poster_cockroach.py`
3. ✅ Add COCKROACHDB_URI to Render environment
4. ✅ Monitor first few posts
5. ✅ Set up weekly reel generation schedule

## Questions?

- Database stats: `python database/cockroach_setup.py`
- Test generation: `python generate_reels_local.py` (enter 1)
- Test posting: `python cockroach_poster.py`
