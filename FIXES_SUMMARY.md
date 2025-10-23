# Fixes Applied - Article Duplication Prevention

## Problems Fixed

### 1. **Same Article Posting Repeatedly** ✅
**Issue:** Articles were being posted multiple times because the system wasn't properly tracking which articles had been posted.

**Root Cause:**
- Instagram token was invalid, causing posts to fail
- Failed posts weren't being marked as "attempted" in the database
- System would retry the same article in the next cycle

**Solution:**
- Added `article_id` generation based on title and URL using MD5 hash
- Created unique article ID for each article (e.g., `79a1db1a3dc8e58d`)
- Articles are now checked by both URL and article_id to prevent duplicates
- Rate-limited Instagram posts are marked as "attempted" to prevent retries

### 2. **Duplicate Instagram Posts (One with Overlay, One Without)** ✅
**Issue:** When overlay image failed to upload to Instagram, the system would retry with the original image, creating TWO media objects and potentially TWO posts for the same article.

**Evidence from logs:**
```
2025-10-23 07:36:36,333 - INFO - ✅ Media object created: 17847948204585640  (with overlay)
...
2025-10-23 07:37:12,858 - INFO - ✅ Media object created: 17847948264585640  (without overlay)
```

**Solution:**
- Removed the "retry with original image" fallback logic
- System now only attempts posting once with the best available image (overlay if successful, original if overlay failed to create)
- No more duplicate media objects on Instagram

## Code Changes

### 1. database.py
**Added:**
- `generate_article_id()` function - Creates unique ID from title + URL
- Article ID tracking in database schema
- Sparse unique index on `article_id` field (allows old documents without it)
- Enhanced `is_already_posted()` to check both URL and article_id
- Upsert logic in `mark_as_posted()` to prevent duplicates

**New Schema:**
```python
{
    'article_id': '79a1db1a3dc8e58d',  # NEW: Unique hash
    'article_url': 'https://...',
    'article_title': 'Pentagon Announces...',
    'section': 'business',
    'instagram_post_id': '...',
    'youtube_video_id': '...',
    'posted_at': datetime
}
```

### 2. server.py
**Removed:**
```python
# DELETED: This caused duplicate posts
if not result['success'] and processed_image_url:
    logger.warning("⚠️ Retrying with original image...")
    result = self.post_to_instagram_direct(image_url, caption)
```

**Added:**
- Article ID check when filtering articles
- Rate limit detection (error code 4, HTTP 403)
- Mark articles as "attempted" even when rate limited
- Import `generate_article_id` to check duplicates during fetch

### 3. migrate_add_article_ids.py (NEW)
- Migration script to update 79 existing articles with article_id
- Ran successfully - all old articles now have unique IDs
- Prevents re-posting of historical content

## Testing Results

### Before Fix:
- ❌ Same article posted multiple times
- ❌ Two Instagram media objects created (17847948204585640, 17847948264585640)
- ❌ Database didn't prevent duplicates effectively

### After Fix:
- ✅ 79 old articles migrated with unique article_ids
- ✅ Database finds "80 already posted articles"
- ✅ "0 FRESH articles from business" (correct - no duplicates)
- ✅ System moves to next section instead of re-posting
- ✅ No retry with original image (single post attempt only)

## Migration Status

```
Migration: Adding article_id to existing documents
📊 Found 79 documents without article_id
✅ Updated: 79 documents
❌ Errors: 0 documents
```

All historical articles now protected from re-posting.

## Database Indexes

```python
article_url: unique=True          # Original URL-based tracking
article_id: unique=True, sparse=True  # NEW: Hash-based tracking
posted_at: indexed                # Performance
section: indexed                  # Performance
```

The `sparse=True` allows old documents without article_id while enforcing uniqueness for new ones.

## Current System Status

✅ **Ready for production**
- Instagram: Rate limited (temporary, will reset in 1-2 hours)
- YouTube: Fully operational
- Database: 80 articles tracked with article_ids
- Duplicate Prevention: Active and tested
- Multi-platform posting: Working independently

## Future Recommendations

1. **Monitor article_id collisions** - Extremely unlikely with MD5 but log any duplicates
2. **Consider rate limit backoff** - Increase interval to 30-45 min when Instagram is frequently limited
3. **Periodic database cleanup** - Remove articles older than 30 days to save space
