#!/usr/bin/env python3
"""Test article ID generation to ensure uniqueness"""

from database import generate_article_id

# Test articles
articles = [
    {
        'title': 'Pentagon Announces "Next Generation" Press Corps',
        'url': 'https://www.nytimes.com/2025/10/22/business/pentagon-press-corps.html'
    },
    {
        'title': 'Pentagon Announces "Next Generation" Press Corps',  # Same title
        'url': 'https://www.nytimes.com/2025/10/22/business/pentagon-press-corps-2.html'  # Different URL
    },
    {
        'title': 'How China Raced Ahead of the U.S. on Nuclear Power',
        'url': 'https://www.nytimes.com/2025/10/16/business/china-nuclear-power.html'
    },
    {
        'title': 'How China Raced Ahead of the U.S. on Nuclear Power',  # Same title
        'url': 'https://www.nytimes.com/2025/10/16/business/china-nuclear-power.html'  # Same URL
    },
]

print("Testing Article ID Generation")
print("=" * 60)

for i, article in enumerate(articles, 1):
    article_id = generate_article_id(
        title=article['title'],
        url=article['url']
    )
    print(f"\n{i}. {article['title'][:50]}...")
    print(f"   URL: {article['url']}")
    print(f"   Article ID: {article_id}")

# Test that same title+URL produces same ID
id1 = generate_article_id(articles[2]['title'], articles[2]['url'])
id2 = generate_article_id(articles[3]['title'], articles[3]['url'])
print(f"\n✅ Same article produces same ID: {id1 == id2}")

# Test that same title but different URL produces different ID
id3 = generate_article_id(articles[0]['title'], articles[0]['url'])
id4 = generate_article_id(articles[1]['title'], articles[1]['url'])
print(f"✅ Same title, different URL produces different ID: {id3 != id4}")
