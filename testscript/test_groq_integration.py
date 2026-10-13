#!/usr/bin/env python3
"""
Test script to verify server.py generate_ai_analysis with GROQ_MODEL and GROQ_API_KEYS pool.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import InstagramBackServer

def test_ai_analysis():
    print("Testing generate_ai_analysis from server.py...")
    server = InstagramBackServer()
    
    mock_article = {
        "title": "Fed Signals Rate Pause as Inflation Cools Across Key Sectors",
        "abstract": "Federal Reserve officials indicated interest rates will remain steady as core inflation readings showed continuing moderation.",
        "content": "Federal Reserve officials indicated interest rates will remain steady as core inflation readings showed continuing moderation."
    }
    
    analysis = server.generate_ai_analysis(mock_article)
    print(f"\nResulting AI Analysis:\n{analysis}")
    assert len(analysis) > 10, "Analysis is too short or empty"
    print("\n✅ generate_ai_analysis successfully generated with Groq!")

if __name__ == "__main__":
    test_ai_analysis()
