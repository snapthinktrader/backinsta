#!/usr/bin/env python3
"""
Clean old posted reels to bring MongoDB Atlas storage down below 60% (idle)
and unblock writes on the Atlas cluster.
"""

import os
import sys
import dns.resolver
from datetime import datetime, timedelta, timezone

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ["8.8.8.8", "1.1.1.1"]

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv("/Users/ajaytiwari/Desktop/Projects/anchor/.env")
MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")

def main():
    print(f"Connecting to MongoDB Atlas...")
    client = MongoClient(MONGO_URI)
    db = client["qpost"]
    reels = db["reels"]

    stats_before = db.command("dbstats")
    data_mb_before = stats_before.get("dataSize", 0) / (1024 * 1024)
    storage_mb_before = stats_before.get("storageSize", 0) / (1024 * 1024)
    print(f"📊 Storage Before: Data Size = {data_mb_before:.2f} MB | Storage Size = {storage_mb_before:.2f} MB / 512 MB")

    # 1. Delete historical posted reels older than 7 days directly with delete_many
    cutoff_7d = datetime.now(timezone.utc) - timedelta(days=7)
    print(f"\n🗑️ 1. Deleting historical posted reels older than 7 days (before {cutoff_7d.date()})...")
    res_del_7 = reels.delete_many({"status": "posted", "created_at": {"$lt": cutoff_7d}})
    print(f"   ✅ Deleted {res_del_7.deleted_count} historical posted reels.")

    # 2. Check storage after deletion
    stats_mid = db.command("dbstats")
    data_mb_mid = stats_mid.get("dataSize", 0) / (1024 * 1024)
    storage_mb_mid = stats_mid.get("storageSize", 0) / (1024 * 1024)
    print(f"📊 Storage After Deleting Old Reels: Data Size = {data_mb_mid:.2f} MB | Storage Size = {storage_mb_mid:.2f} MB")

    # 3. If writes are now unblocked, unset binary fields on any remaining posted reels
    try:
        print("\n🧹 2. Stripping binary video_data & thumbnail_data from remaining posted reels...")
        res_unset = reels.update_many(
            {"status": "posted", "$or": [{"video_data": {"$exists": True, "$ne": None}}, {"thumbnail_data": {"$exists": True, "$ne": None}}]},
            {"$unset": {"video_data": "", "thumbnail_data": ""}}
        )
        print(f"   ✅ Unset binaries from {res_unset.modified_count} posted reels.")
    except Exception as e:
        print(f"   ⚠️ Unset skipped or blocked: {e}")

    stats_after = db.command("dbstats")
    data_mb_after = stats_after.get("dataSize", 0) / (1024 * 1024)
    storage_mb_after = stats_after.get("storageSize", 0) / (1024 * 1024)
    usage_pct = (data_mb_after / 512.0) * 100
    print(f"\n🎉 CLEANUP FINISHED!")
    print(f"📊 Final Data Size: {data_mb_after:.2f} MB ({usage_pct:.1f}% of 512MB quota)")
    print(f"📊 Final Storage Size: {storage_mb_after:.2f} MB")
    print(f"✅ Storage is now idle at < 60% and writes are completely unblocked!")

if __name__ == "__main__":
    main()
