#!/usr/bin/env python3
"""
Test the exact Groq multi-key pool and model logic from server.py directly with requests.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_ai_logic():
    raw_keys = os.getenv('GROQ_API_KEYS', '')
    keys_list = [k.strip() for k in raw_keys.split(',') if k.strip()]
    single_key = os.getenv('GROQ_API_KEY')
    if single_key and single_key not in keys_list:
        keys_list.insert(0, single_key.strip())

    print(f"Loaded {len(keys_list)} active Groq keys.")
    model_name = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
    print(f"Target Groq Model: {model_name}")

    mock_article = {
        "title": "Fed Signals Rate Pause as Inflation Cools Across Key Sectors",
        "abstract": "Federal Reserve officials indicated interest rates will remain steady as core inflation readings showed continuing moderation."
    }

    prompt = f"""You are a news analyst. Provide a brief, engaging 2-3 sentence analysis of this news article for social media.
Focus on key insights, implications, or interesting angles. Keep it conversational and engaging.

Title: {mock_article['title']}
Summary: {mock_article['abstract']}

Provide ONLY the analysis, no extra labels or formatting:"""

    for idx, key in enumerate(keys_list[:2], 1):
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are an expert news analyst."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 300,
            "temperature": 0.7
        }
        
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"Key [{idx}/{len(keys_list)}] Status: {resp.status_code}")
        if resp.status_code == 200:
            analysis = resp.json()["choices"][0]["message"]["content"].strip()
            print(f"✅ Generated Analysis:\n{analysis}")
            break
        else:
            print(f"⚠️ Failed: {resp.text}")

if __name__ == "__main__":
    test_ai_logic()
