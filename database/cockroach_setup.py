"""
CockroachDB Setup and Schema for Instagram Reels
Creates tables and provides connection utilities
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

COCKROACHDB_URI = os.getenv('COCKROACHDB_URI')

def get_connection():
    """
    Get a connection to CockroachDB
    
    Returns:
        psycopg2.connection: Database connection
    """
    try:
        # Fix SSL certificate issue on Render by using system certificates
        uri = COCKROACHDB_URI
        if 'sslmode=verify-full' in uri and '/opt/render' in os.getcwd():
            # Running on Render - use system certificates
            uri = uri.replace('sslmode=verify-full', 'sslmode=require')
        
        conn = psycopg2.connect(uri)
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to CockroachDB: {e}")
        raise

def create_schema():
    """
    Create the reels table schema in CockroachDB
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        print("🔧 Creating reels table schema...")
        
        # Create reels table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reels (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                headline TEXT NOT NULL,
                caption TEXT NOT NULL,
                article_url TEXT,
                article_id TEXT UNIQUE NOT NULL,
                video_data BYTEA,
                thumbnail_url TEXT,
                ai_analysis TEXT,
                duration FLOAT,
                file_size INT,
                created_at TIMESTAMP DEFAULT now(),
                posted_at TIMESTAMP,
                status TEXT DEFAULT 'pending',
                instagram_post_id TEXT,
                youtube_video_id TEXT,
                error_message TEXT,
                retry_count INT DEFAULT 0,
                CONSTRAINT status_check CHECK (status IN ('pending', 'posted', 'failed', 'processing'))
            )
        """)
        
        # Create indexes for efficient queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON reels(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON reels(created_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_article_id ON reels(article_id)
        """)
        
        conn.commit()
        print("✅ Schema created successfully!")
        
        # Show table info
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'reels'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("\n📊 Reels Table Schema:")
        for col in columns:
            print(f"   {col[0]}: {col[1]} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def test_connection():
    """
    Test the connection to CockroachDB
    """
    conn = None
    try:
        print("🔌 Testing CockroachDB connection...")
        conn = get_connection()
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ Connected to CockroachDB!")
        print(f"   Version: {version}")
        
        # Check if reels table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'reels'
            )
        """)
        table_exists = cursor.fetchone()[0]
        
        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM reels")
            count = cursor.fetchone()[0]
            print(f"✅ Reels table exists with {count} records")
        else:
            print("⚠️  Reels table does not exist yet")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
    finally:
        if conn:
            conn.close()

def insert_reel(headline, caption, article_url, article_id, video_data, 
                thumbnail_url, ai_analysis, duration, file_size):
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
        
    Returns:
        UUID: ID of inserted reel or None if failed
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reels (
                headline, caption, article_url, article_id, video_data,
                thumbnail_url, ai_analysis, duration, file_size
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (headline, caption, article_url, article_id, psycopg2.Binary(video_data),
              thumbnail_url, ai_analysis, duration, file_size))
        
        reel_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        
        print(f"✅ Reel inserted: {reel_id}")
        return reel_id
        
    except psycopg2.IntegrityError as e:
        print(f"⚠️  Reel already exists (article_id: {article_id})")
        if conn:
            conn.rollback()
        return None
    except Exception as e:
        print(f"❌ Failed to insert reel: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def get_pending_reel():
    """
    Get the oldest pending reel from database
    
    Returns:
        dict: Reel data or None if no pending reels
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT * FROM reels
            WHERE status = 'pending'
            ORDER BY created_at ASC
            LIMIT 1
        """)
        
        reel = cursor.fetchone()
        cursor.close()
        
        if reel:
            # Convert to dict and handle binary data
            reel_dict = dict(reel)
            if reel_dict.get('video_data'):
                reel_dict['video_data'] = bytes(reel_dict['video_data'])
            return reel_dict
        return None
        
    except Exception as e:
        print(f"❌ Failed to get pending reel: {e}")
        raise
    finally:
        if conn:
            conn.close()

def mark_reel_posted(reel_id, instagram_post_id=None, youtube_video_id=None):
    """
    Mark a reel as posted
    
    Args:
        reel_id: UUID of the reel
        instagram_post_id: Instagram post ID (optional)
        youtube_video_id: YouTube video ID (optional)
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE reels
            SET status = 'posted',
                posted_at = now(),
                instagram_post_id = %s,
                youtube_video_id = %s
            WHERE id = %s
        """, (instagram_post_id, youtube_video_id, reel_id))
        
        conn.commit()
        cursor.close()
        print(f"✅ Reel marked as posted: {reel_id}")
        
    except Exception as e:
        print(f"❌ Failed to mark reel as posted: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def mark_reel_failed(reel_id, error_message):
    """
    Mark a reel as failed
    
    Args:
        reel_id: UUID of the reel
        error_message: Error description
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE reels
            SET status = 'failed',
                error_message = %s,
                retry_count = retry_count + 1
            WHERE id = %s
        """, (error_message, reel_id))
        
        conn.commit()
        cursor.close()
        print(f"⚠️  Reel marked as failed: {reel_id}")
        
    except Exception as e:
        print(f"❌ Failed to mark reel as failed: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def get_stats():
    """
    Get statistics about reels in database
    
    Returns:
        dict: Statistics
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'posted' THEN 1 ELSE 0 END) as posted,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                SUM(file_size) as total_size_bytes,
                AVG(duration) as avg_duration_seconds
            FROM reels
        """)
        
        stats = dict(cursor.fetchone())
        cursor.close()
        
        return stats
        
    except Exception as e:
        print(f"❌ Failed to get stats: {e}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🗄️  CockroachDB Setup for Instagram Reels")
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
