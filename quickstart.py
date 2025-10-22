#!/usr/bin/env python3
"""
Quick Start Script for BackInsta
Provides an interactive menu for common tasks
"""

import os
import sys
import subprocess

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("⚠️  .env file not found!")
        print("\nCreating .env from .env.example...")
        
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ .env file created")
            print("\n📝 Please edit .env and add your credentials:")
            print("   - REACT_APP_ACCESS_TOKEN")
            print("   - REACT_APP_INSTAGRAM_BUSINESS_ACCOUNT_ID")
            print("\nThen run this script again.")
            return False
        else:
            print("❌ .env.example not found!")
            return False
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_header("📦 Installing Dependencies")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    print("\n✅ Dependencies installed")

def run_tests():
    """Run test suite"""
    print_header("🧪 Running Tests")
    subprocess.run([sys.executable, 'test.py'])

def start_server():
    """Start the BackInsta server"""
    print_header("🚀 Starting BackInsta Server")
    print("Press Ctrl+C to stop\n")
    try:
        subprocess.run([sys.executable, 'server.py'])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")

def show_stats():
    """Show posting statistics"""
    print_header("📊 Posting Statistics")
    try:
        from database import BackInstaDB
        from config import Config
        
        db = BackInstaDB(Config.MONGODB_URI)
        stats = db.get_stats()
        
        print(f"Total posts: {stats.get('total_posts', 0)}")
        print("\nPosts by section:")
        for section, count in stats.get('sections', {}).items():
            print(f"  - {section}: {count}")
        
        print("\nRecent posts:")
        recent = db.get_posted_articles(limit=5)
        for i, post in enumerate(recent, 1):
            print(f"\n{i}. {post.get('article_title', 'Unknown')[:60]}")
            print(f"   Posted: {post.get('posted_at')}")
            print(f"   Instagram: {post.get('instagram_url', 'N/A')}")
        
        db.close()
    except Exception as e:
        print(f"❌ Error fetching stats: {e}")

def show_config():
    """Show current configuration"""
    print_header("⚙️  Current Configuration")
    try:
        from config import Config
        Config.print_config()
    except Exception as e:
        print(f"❌ Error loading config: {e}")

def main():
    """Main menu"""
    print_header("🚀 BackInsta - News to Instagram Automation")
    
    # Check environment
    if not check_env_file():
        sys.exit(1)
    
    while True:
        print("\n📋 Main Menu:")
        print("  1) Install/Update Dependencies")
        print("  2) Show Configuration")
        print("  3) Run Tests")
        print("  4) Start Server (Live Posting)")
        print("  5) Show Statistics")
        print("  6) Exit")
        
        choice = input("\nEnter choice [1-6]: ").strip()
        
        if choice == '1':
            install_dependencies()
        elif choice == '2':
            show_config()
        elif choice == '3':
            run_tests()
        elif choice == '4':
            start_server()
        elif choice == '5':
            show_stats()
        elif choice == '6':
            print("\n👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please enter 1-6.")

if __name__ == '__main__':
    main()
