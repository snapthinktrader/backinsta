#!/usr/bin/env python3
"""
Check for duplicate article_id entries in reels table
"""
from database.mongodb_setup import get_connection

def find_duplicates():
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT article_id, COUNT(*) as cnt
            FROM reels
            GROUP BY article_id
            HAVING COUNT(*) > 1
            ORDER BY cnt DESC
        """)
        rows = cur.fetchall()
        if not rows:
            print("✅ No duplicate article_id entries found.")
            return []
        else:
            print("⚠️ Duplicates found:")
            for r in rows:
                print(f"  article_id={r[0]}  count={r[1]}")
            return rows
    except Exception as e:
        print(f"❌ Error while checking duplicates: {e}")
        return None
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    find_duplicates()
