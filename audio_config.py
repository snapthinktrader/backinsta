"""
Audio configuration for Instagram Reels
Manages trending background music tracks
"""

import os
import random
from typing import Optional

# Trending royalty-free music URLs or local paths
# You can add your own music files here or use URLs from royalty-free sources
TRENDING_AUDIO_TRACKS = [
    {
        "name": "Upbeat News Theme",
        "url": "https://cdn.pixabay.com/audio/2022/03/15/audio_1234567890abcdef.mp3",  # Example
        "local_path": None,  # Will be set after download
        "duration": 10,  # seconds
        "category": "news"
    },
    {
        "name": "Dynamic Intro",
        "url": "https://cdn.pixabay.com/audio/2022/05/20/audio_abcdef1234567890.mp3",  # Example
        "local_path": None,
        "duration": 8,
        "category": "general"
    },
    # Add more tracks here
]

def get_random_audio_track(category: str = "general") -> Optional[dict]:
    """
    Get a random audio track for the specified category
    
    Args:
        category: Track category (news, general, sports, etc.)
        
    Returns:
        Track dictionary or None
    """
    matching_tracks = [t for t in TRENDING_AUDIO_TRACKS if t.get("category") == category]
    
    if not matching_tracks:
        # Fallback to any track
        matching_tracks = TRENDING_AUDIO_TRACKS
    
    if matching_tracks:
        return random.choice(matching_tracks)
    
    return None

def get_audio_path() -> Optional[str]:
    """
    Get path to a default background audio file
    Looks in audio_tracks directory for any .mp3 file
    
    Returns:
        Path to audio file or None
    """
    audio_dir = os.path.join(os.path.dirname(__file__), 'audio_tracks')
    
    if not os.path.exists(audio_dir):
        return None
    
    # Find any .mp3 file
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
    
    if audio_files:
        return os.path.join(audio_dir, random.choice(audio_files))
    
    return None

# Note: Since Instagram API doesn't support their music library,
# we recommend using royalty-free music or posting silent Reels
# and manually adding Instagram music through the app
USE_AUDIO = os.getenv('USE_BACKGROUND_AUDIO', 'false').lower() == 'true'
