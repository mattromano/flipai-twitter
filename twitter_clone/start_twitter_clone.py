#!/usr/bin/env python3
"""
Simple script to start the Twitter clone frontend.
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def main():
    """Start the Twitter clone frontend."""
    
    print("🐦 Starting Twitter Clone Frontend...")
    print("=" * 40)
    
    # Check if tweet previews exist (in parent directory)
    previews_dir = Path("../tweet_previews")
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
        # Start the server
        subprocess.run([sys.executable, "twitter_clone_frontend.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Twitter clone stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
