import os
import sys
import logging
from bson.objectid import ObjectId
from pymongo import MongoClient
from dotenv import dotenv_values

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AttachCovers")

# Load environment
env_path = "/Users/ajaytiwari/Desktop/Projects/backinsta/.env"
env_vars = dotenv_values(env_path)
mongo_uri = env_vars.get("MONGODB_URI") or env_vars.get("MONGO_URI") or os.getenv("MONGODB_URI")

if not mongo_uri:
    logger.error("❌ MongoDB URI not found")
    sys.exit(1)

client = MongoClient(mongo_uri)
db = client["qpost"]
reels_coll = db["reels"]

# Ensure anchor is in path to use its public host uploader
sys.path.insert(0, "/Users/ajaytiwari/Desktop/Projects/anchor")
from uploader import upload_file_to_public_host

updates = [
    {
        "id": "6ad361d5b0b0f93cb38580b0",
        "name": "Taxes & AI",
        "cover_path": "/Users/ajaytiwari/Desktop/Projects/anchor/output/cover_reel_taxes_ai_9_16.jpg"
    },
    {
        "id": "6ad363dbb0b0f93cb38580b2",
        "name": "France Protests",
        "cover_path": "/Users/ajaytiwari/Desktop/Projects/anchor/output/cover_reel_france_protests_9_16.jpg"
    }
]

for item in updates:
    obj_id = ObjectId(item["id"])
    doc = reels_coll.find_one({"_id": obj_id})
    if not doc:
        logger.warning(f"⚠️ Document {item['id']} not found in qpost.reels")
        continue

    cover_path = item["cover_path"]
    if not os.path.exists(cover_path):
        logger.error(f"❌ Cover file not found: {cover_path}")
        continue

    logger.info(f"🖼️ Reading cover for {item['name']}: {cover_path}")
    with open(cover_path, "rb") as cf:
        cover_bytes = cf.read()

    logger.info(f"📤 Hosting cover image for {item['name']}...")
    cover_url = upload_file_to_public_host(cover_path)
    logger.info(f"   ✅ Hosted at: {cover_url}")

    update_fields = {
        "thumbnail_data": cover_bytes,
        "thumbnail_path": cover_path,
        "cover_url": cover_url,
        "has_thumbnail": True
    }

    res = reels_coll.update_one({"_id": obj_id}, {"$set": update_fields})
    logger.info(f"✅ Updated {item['name']} ({item['id']}): matched={res.matched_count}, modified={res.modified_count}")

# Verification
logger.info("\n🔍 Verifying pending reels in MongoDB:")
for item in updates:
    doc = reels_coll.find_one({"_id": ObjectId(item["id"])}, {"video_data": 0})
    if doc:
        logger.info(f"   ID: {doc['_id']} | Headline: {doc.get('headline')[:40]} | Has Thumbnail: {doc.get('has_thumbnail')} | Cover URL: {doc.get('cover_url')}")
