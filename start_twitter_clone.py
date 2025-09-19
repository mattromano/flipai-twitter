#!/usr/bin/env python3
"""
Start the Twitter clone frontend from the main directory.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start the Twitter clone frontend."""
    
    print("🐦 Starting Twitter Clone Frontend...")
    print("=" * 40)
    
    # Check if tweet previews exist
    previews_dir = Path("tweet_previews")
    if not previews_dir.exists():
        print("❌ No tweet_previews folder found!")
        print("💡 Run 'python tweet_preview_generator.py' first to generate some tweets.")
        return
    
    json_files = list(previews_dir.glob("*_tweet_*.json"))
    if not json_files:
        print("❌ No tweet preview files found!")
        print("💡 Run 'python tweet_preview_generator.py' first to generate some tweets.")
        return
    
    print(f"📊 Found {len(json_files)} tweet previews")
    print("🌐 Starting server on http://localhost:8080")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    try:
        # Change to twitter_clone directory and start the server
        os.chdir("twitter_clone")
        subprocess.run([sys.executable, "twitter_clone_frontend.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Twitter clone stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()