#!/usr/bin/env python3
"""
Configuration management for BackInsta
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for BackInsta"""
    
    # Webstory Backend
    WEBSTORY_API_URL = os.getenv('WEBSTORY_API_URL', 'https://webstory-frontend.vercel.app/api')
    WEBSTORY_SECTIONS = ['home', 'technology', 'business', 'politics', 'sports', 'entertainment']
    
    # Webstory MongoDB (for direct article fetching)
    WEBSTORY_MONGODB_URI = os.getenv('WEBSTORY_MONGODB_URI', 'mongodb+srv://ajay26:Ajtiwari26@cluster0.pfudopf.mongodb.net/webstory?retryWrites=true&w=majority&appName=Cluster0')
    
    # QPost Backend
    QPOST_API_URL = os.getenv('QPOST_API_URL', 'http://localhost:8000/api')
    
    # Instagram API
    INSTAGRAM_ACCESS_TOKEN = os.getenv('REACT_APP_ACCESS_TOKEN')
    INSTAGRAM_ACCOUNT_ID = os.getenv('REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID', '17841474412696876')
    
    # MongoDB (for BackInsta tracking)
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://aj:aj@qpost.lk5htbl.mongodb.net/?retryWrites=true&w=majority&appName=qpost')
    
    # Image Hosting
    IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')
    
    # Posting Configuration
    MAX_POSTS_PER_CYCLE = int(os.getenv('MAX_POSTS_PER_CYCLE', '2'))
    POST_INTERVAL_SECONDS = int(os.getenv('POST_INTERVAL_SECONDS', '60'))
    
    # Caption Configuration
    MAX_CAPTION_LENGTH = int(os.getenv('MAX_CAPTION_LENGTH', '500'))
    MAX_ABSTRACT_LENGTH = int(os.getenv('MAX_ABSTRACT_LENGTH', '150'))
    
    # Scheduling (in hours)
    SCHEDULE_HOME_HOURS = int(os.getenv('SCHEDULE_HOME_HOURS', '4'))
    SCHEDULE_TECH_HOURS = int(os.getenv('SCHEDULE_TECH_HOURS', '6'))
    SCHEDULE_BUSINESS_HOURS = int(os.getenv('SCHEDULE_BUSINESS_HOURS', '8'))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.INSTAGRAM_ACCESS_TOKEN:
            errors.append("REACT_APP_ACCESS_TOKEN is required")
        
        if not cls.INSTAGRAM_ACCOUNT_ID:
            errors.append("REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID is required")
        
        return errors
    
    @classmethod
    def print_config(cls):
        """Print current configuration (excluding sensitive data)"""
        print("=" * 60)
        print("BackInsta Configuration")
        print("=" * 60)
        print(f"Webstory API: {cls.WEBSTORY_API_URL}")
        print(f"QPost API: {cls.QPOST_API_URL}")
        print(f"Instagram Account ID: {cls.INSTAGRAM_ACCOUNT_ID}")
        print(f"Access Token: {'***' + cls.INSTAGRAM_ACCESS_TOKEN[-10:] if cls.INSTAGRAM_ACCESS_TOKEN else 'Not Set'}")
        print(f"Max Posts per Cycle: {cls.MAX_POSTS_PER_CYCLE}")
        print(f"Post Interval: {cls.POST_INTERVAL_SECONDS}s")
        print(f"Schedule - Home: Every {cls.SCHEDULE_HOME_HOURS}h")
        print(f"Schedule - Tech: Every {cls.SCHEDULE_TECH_HOURS}h")
        print(f"Schedule - Business: Every {cls.SCHEDULE_BUSINESS_HOURS}h")
        print("=" * 60)
