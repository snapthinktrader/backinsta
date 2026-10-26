# testscript/check_mongodb_idle_reels.py
# Check how many reels are idle/pending for next posting in MongoDB

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "qpost")

def check_reels():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    reels_coll = db["reels"]

    total = reels_coll.count_documents({})
    pending_reels = list(reels_coll.find({"status": "pending"}))
    posted_count = reels_coll.count_documents({"status": "posted"})
    failed_count = reels_coll.count_documents({"status": "failed"})

    print(f"MongoDB ({DB_NAME}.reels) summary:")
    print(f" - Total reels: {total}")
    print(f" - Pending / idle reels: {len(pending_reels)}")
    print(f" - Posted reels: {posted_count}")
    print(f" - Failed reels: {failed_count}")

    print("\nRecent 5 reels in MongoDB:")
    for r in reels_coll.find().sort("_id", -1).limit(5):
        print(f"   * ID: {r.get('_id')} | Status: {r.get('status')} | Topic: {r.get('topic') or r.get('title')} | Created: {r.get('created_at')} | IG: {r.get('instagram_url')}")

if __name__ == "__main__":
    check_reels()
