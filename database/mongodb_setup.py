"""
MongoDB Setup and Schema for Instagram Reels
Creates collections and provides connection utilities
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from bson.binary import Binary
import gridfs

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI')

def get_connection():
    """
    Get a connection to MongoDB
    
    Returns:
        pymongo.MongoClient: Database client
    """
    try:
        client = MongoClient(MONGODB_URI, tlsAllowInvalidCertificates=True)
        # Test connection
        client.server_info()
        return client
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise

def create_schema():
    """
    Create the reels collection schema and indexes in MongoDB
    """
    client = None
    try:
        client = get_connection()
        db = client['qpost']
        
        print("🔧 Creating reels collection schema...")
        
        # Create indexes for reels collection
        db.reels.create_index('status')
        db.reels.create_index([('created_at', -1)])
        db.reels.create_index('article_id', unique=True)
        db.reels.create_index('posted_at')
        db.reels.create_index('instagram_post_id')
        db.reels.create_index('youtube_video_id')
        
        print("✅ Indexes created successfully!")
        
        # Show collection info
        print("\n📊 Reels Collection Schema:")
        print("   Fields:")
        print("   - _id: Unique identifier (auto-generated)")
        print("   - headline: Article headline (text)")
        print("   - caption: Instagram/YouTube caption (text)")
        print("   - article_url: Source article URL (text)")
        print("   - article_id: Unique article identifier (text, unique index)")
        print("   - video_data: Video file as binary (GridFS for large files)")
        print("   - thumbnail_url: URL to thumbnail image (text)")
        print("   - ai_analysis: Generated AI analysis text (text)")
        print("   - duration: Video duration in seconds (float)")
        print("   - file_size: Video file size in bytes (int)")
        print("   - created_at: Creation timestamp (datetime)")
        print("   - posted_at: Posting timestamp (datetime)")
        print("   - status: pending/posted/failed/processing (text, indexed)")
        print("   - instagram_post_id: Instagram post ID (text)")
        print("   - youtube_video_id: YouTube video ID (text)")
        print("   - error_message: Error description (text)")
        print("   - retry_count: Number of retry attempts (int)")
        print("   - section: News section (text)")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        raise
    finally:
        if client:
            client.close()

def test_connection():
    """
    Test the connection to MongoDB
    """
    client = None
    try:
        print("🔌 Testing MongoDB connection...")
        client = get_connection()
        db = client['qpost']
        
        # Test query
        server_info = client.server_info()
        print(f"✅ Connected to MongoDB!")
        print(f"   Version: {server_info.get('version', 'unknown')}")
        
        # Check if reels collection exists and get count
        count = db.reels.count_documents({})
        print(f"✅ Reels collection exists with {count} records")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
    finally:
        if client:
            client.close()

def insert_reel(headline, caption, article_url, article_id, video_data, 
                thumbnail_url, ai_analysis, duration, file_size, section=None):
    """
    Insert a new reel into the database
    
    Args:
        headline: Article headline
        caption: Instagram/YouTube caption
        article_url: Source article URL
        article_id: Unique article identifier
        video_data: Video file as bytes
        thumbnail_url: URL to thumbnail image
        ai_analysis: Generated AI analysis text
        duration: Video duration in seconds
        file_size: Video file size in bytes
        section: News section (optional)
        
    Returns:
        str: ID of inserted reel or None if failed
    """
    client = None
    try:
        client = get_connection()
        db = client['qpost']
        fs = gridfs.GridFS(db)
        
        # For large files (>16MB), use GridFS
        video_data_field = None
        gridfs_id = None
        
        if len(video_data) > 15 * 1024 * 1024:  # > 15MB
            # Store in GridFS
            gridfs_id = fs.put(
                video_data,
                filename=f"{article_id}.mp4",
                content_type="video/mp4"
            )
            video_data_field = None  # Store GridFS reference instead
        else:
            # Store directly as binary
            video_data_field = Binary(video_data)
            gridfs_id = None
        
        reel_doc = {
            'headline': headline,
            'caption': caption,
            'article_url': article_url,
            'article_id': article_id,
            'video_data': video_data_field,
            'gridfs_id': str(gridfs_id) if gridfs_id else None,
            'thumbnail_url': thumbnail_url,
            'ai_analysis': ai_analysis,
            'duration': duration,
            'file_size': file_size,
            'section': section,
            'created_at': datetime.now(),
            'posted_at': None,
            'status': 'pending',
            'instagram_post_id': None,
            'youtube_video_id': None,
            'error_message': None,
            'retry_count': 0
        }
        
        result = db.reels.insert_one(reel_doc)
        reel_id = str(result.inserted_id)
        
        client.close()
        print(f"✅ Reel inserted: {reel_id}")
        return reel_id
        
    except Exception as e:
        if 'duplicate key' in str(e):
            print(f"⚠️  Reel already exists (article_id: {article_id})")
            return None
        else:
            print(f"❌ Failed to insert reel: {e}")
            raise
    finally:
        if client:
            client.close()

def get_pending_reel():
    """
    Get the oldest pending reel from database
    Retrieves video data from GridFS if stored there
    
    Returns:
        dict: Reel data or None if no pending reels
    """
    client = None
    try:
        client = get_connection()
        db = client['qpost']
        fs = gridfs.GridFS(db)
        
        reel = db.reels.find_one(
            {'status': 'pending'},
            sort=[('created_at', 1)]
        )
        
        if reel:
            # If video is in GridFS, retrieve it
            if reel.get('gridfs_id') and not reel.get('video_data'):
                from bson import ObjectId
                video_file = fs.get(ObjectId(reel['gridfs_id']))
                reel['video_data'] = video_file.read()
            elif reel.get('video_data'):
                # Convert Binary to bytes
                reel['video_data'] = bytes(reel['video_data'])
            
            # Convert _id to string for compatibility
            reel['id'] = str(reel['_id'])
            
            client.close()
            return reel
        
        client.close()
        return None
        
    except Exception as e:
        print(f"❌ Failed to get pending reel: {e}")
        raise
    finally:
        if client:
            client.close()

def mark_reel_posted(reel_id, instagram_post_id=None, youtube_video_id=None):
    """
    Mark a reel as posted
    
    Args:
        reel_id: ID of the reel (string)
        instagram_post_id: Instagram post ID (optional)
        youtube_video_id: YouTube video ID (optional)
    """
    client = None
    try:
        from bson import ObjectId
        client = get_connection()
        db = client['qpost']
        
        db.reels.update_one(
            {'_id': ObjectId(reel_id)},
            {
                '$set': {
                    'status': 'posted',
                    'posted_at': datetime.now(),
                    'instagram_post_id': instagram_post_id,
                    'youtube_video_id': youtube_video_id
                }
            }
        )
        
        client.close()
        print(f"✅ Reel marked as posted: {reel_id}")
        
    except Exception as e:
        print(f"❌ Failed to mark reel as posted: {e}")
        raise
    finally:
        if client:
            client.close()

def mark_reel_failed(reel_id, error_message):
    """
    Mark a reel as failed
    
    Args:
        reel_id: ID of the reel (string)
        error_message: Error description
    """
    client = None
    try:
        from bson import ObjectId
        client = get_connection()
        db = client['qpost']
        
        db.reels.update_one(
            {'_id': ObjectId(reel_id)},
            {
                '$set': {
                    'status': 'failed',
                    'error_message': error_message
                },
                '$inc': {'retry_count': 1}
            }
        )
        
        client.close()
        print(f"⚠️  Reel marked as failed: {reel_id}")
        
    except Exception as e:
        print(f"❌ Failed to mark reel as failed: {e}")
        raise
    finally:
        if client:
            client.close()

def get_stats():
    """
    Get statistics about reels in database
    
    Returns:
        dict: Statistics
    """
    client = None
    try:
        client = get_connection()
        db = client['qpost']
        
        total = db.reels.count_documents({})
        pending = db.reels.count_documents({'status': 'pending'})
        posted = db.reels.count_documents({'status': 'posted'})
        failed = db.reels.count_documents({'status': 'failed'})
        
        # Aggregate for size and duration
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_size': {'$sum': '$file_size'},
                    'avg_duration': {'$avg': '$duration'}
                }
            }
        ]
        
        agg_result = list(db.reels.aggregate(pipeline))
        
        stats = {
            'total': total,
            'pending': pending,
            'posted': posted,
            'failed': failed,
            'total_size_bytes': agg_result[0]['total_size'] if agg_result else 0,
            'avg_duration_seconds': agg_result[0]['avg_duration'] if agg_result else 0
        }
        
        client.close()
        return stats
        
    except Exception as e:
        print(f"❌ Failed to get stats: {e}")
        raise
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🗄️  MongoDB Setup for Instagram Reels")
    print("=" * 60)
    
    # Test connection
    if test_connection():
        print("\n" + "=" * 60)
        
        # Create schema
        response = input("Create/update schema? (y/n): ")
        if response.lower() == 'y':
            create_schema()
            print("\n✅ Setup complete!")
        
        # Show stats
        try:
            stats = get_stats()
            print("\n📊 Database Statistics:")
            print(f"   Total reels: {stats['total']}")
            print(f"   Pending: {stats['pending']}")
            print(f"   Posted: {stats['posted']}")
            print(f"   Failed: {stats['failed']}")
            if stats['total_size_bytes']:
                total_mb = stats['total_size_bytes'] / (1024 * 1024)
                print(f"   Total size: {total_mb:.2f} MB")
            if stats['avg_duration_seconds']:
                print(f"   Avg duration: {stats['avg_duration_seconds']:.1f}s")
        except:
            pass
