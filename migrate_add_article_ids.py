#!/usr/bin/env python3
"""
Migration script to add article_id to existing documents
Run this once to update all old articles in the database
"""

import os
from pymongo import MongoClient
from database import generate_article_id
from config import Config

print("=" * 60)
print("Migration: Adding article_id to existing documents")
print("=" * 60)

# Connect to MongoDB
client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=5000, tlsAllowInvalidCertificates=True)
db = client.backinsta
collection = db.posted_articles

# Find all documents without article_id
documents_without_id = collection.find({'article_id': {'$exists': False}})
count = collection.count_documents({'article_id': {'$exists': False}})

print(f"\n📊 Found {count} documents without article_id")

if count == 0:
    print("✅ All documents already have article_id!")
    client.close()
    exit(0)

print("\n🔄 Updating documents...")

updated = 0
errors = 0

for doc in documents_without_id:
    try:
        # Generate article_id from title and URL
        title = doc.get('article_title', '')
        url = doc.get('article_url', '')
        
        if not title and not url:
            print(f"⚠️ Skipping document {doc['_id']} - no title or URL")
            errors += 1
            continue
        
        article_id = generate_article_id(title=title, url=url)
        
        # Update the document
        collection.update_one(
            {'_id': doc['_id']},
            {'$set': {'article_id': article_id}}
        )
        
        updated += 1
        print(f"✅ Updated: {title[:50]}... -> {article_id}")
        
    except Exception as e:
        print(f"❌ Error updating {doc.get('_id')}: {e}")
        errors += 1

print("\n" + "=" * 60)
print(f"✅ Migration complete!")
print(f"   Updated: {updated} documents")
print(f"   Errors: {errors} documents")
print("=" * 60)

client.close()
