#!/usr/bin/env python3
"""
View all tweet previews in the tweet_previews folder.
"""

import os
import json
from pathlib import Path
from datetime import datetime

def list_tweet_previews():
    """List all tweet previews."""
    
    previews_dir = Path("tweet_previews")
    if not previews_dir.exists():
        print("❌ No tweet_previews folder found")
        return
    
    # Find all JSON files
    json_files = list(previews_dir.glob("*_tweet_*.json"))
    
    if not json_files:
        print("❌ No tweet preview files found")
        return
    
    print("🐦 Tweet Previews")
    print("=" * 60)
    
    # Sort by modification time (newest first)
    json_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    for i, json_file in enumerate(json_files, 1):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                tweet_data = json.load(f)
            
            # Extract info from filename
            filename_parts = json_file.stem.split('_')
            analysis_date = filename_parts[1] if len(filename_parts) > 1 else "unknown"
            preview_time = filename_parts[-1] if len(filename_parts) > 2 else "unknown"
            
            print(f"\n📊 Preview #{i}: {analysis_date} at {preview_time}")
            print(f"   📄 File: {json_file.name}")
            print(f"   📏 Characters: {tweet_data['character_count']}/280")
            print(f"   📅 Timestamp: {tweet_data['timestamp']}")
            print(f"   🔗 Chat URL: {tweet_data['chat_url']}")
            
            # Show tweet content (truncated)
            content = tweet_data['tweet_content']
            if len(content) > 100:
                content = content[:100] + "..."
            print(f"   📝 Content: {content}")
            
            # Status
            status = "✅ Ready" if tweet_data['character_count'] <= 280 else "⚠️ Too long"
            print(f"   📊 Status: {status}")
            
        except Exception as e:
            print(f"❌ Error reading {json_file.name}: {e}")

def view_specific_preview():
    """View a specific preview in detail."""
    
    previews_dir = Path("tweet_previews")
    if not previews_dir.exists():
        print("❌ No tweet_previews folder found")
        return
    
    # Find all JSON files
    json_files = list(previews_dir.glob("*_tweet_*.json"))
    
    if not json_files:
        print("❌ No tweet preview files found")
        return
    
    # Sort by modification time (newest first)
    json_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    print("🐦 Available Tweet Previews:")
    print("=" * 40)
    
    for i, json_file in enumerate(json_files, 1):
        filename_parts = json_file.stem.split('_')
        analysis_date = filename_parts[1] if len(filename_parts) > 1 else "unknown"
        preview_time = filename_parts[-1] if len(filename_parts) > 2 else "unknown"
        print(f"{i}. {analysis_date} at {preview_time}")
    
    try:
        choice = input(f"\nEnter preview number (1-{len(json_files)}) or 'all' for summary: ").strip()
        
        if choice.lower() == 'all':
            list_tweet_previews()
            return
        
        choice_num = int(choice)
        if 1 <= choice_num <= len(json_files):
            selected_file = json_files[choice_num - 1]
            
            with open(selected_file, 'r', encoding='utf-8') as f:
                tweet_data = json.load(f)
            
            print(f"\n🐦 Tweet Preview Details")
            print("=" * 50)
            print(f"📄 File: {selected_file.name}")
            print(f"📅 Timestamp: {tweet_data['timestamp']}")
            print(f"📏 Characters: {tweet_data['character_count']}/280")
            print(f"🔗 Chat URL: {tweet_data['chat_url']}")
            
            print(f"\n📝 Full Tweet Content:")
            print("-" * 50)
            print(tweet_data['tweet_content'])
            print("-" * 50)
            
            print(f"\n📊 Twitter Text Only:")
            print("-" * 30)
            print(tweet_data['twitter_text'])
            print("-" * 30)
            
            # Check for HTML preview
            html_file = selected_file.with_suffix('.html').with_name(
                selected_file.stem.replace('_tweet_', '_preview_') + '.html'
            )
            if html_file.exists():
                print(f"\n🌐 HTML Preview: {html_file}")
            
            # Check for Markdown preview
            md_file = selected_file.with_suffix('.md').with_name(
                selected_file.stem.replace('_tweet_', '_preview_') + '.md'
            )
            if md_file.exists():
                print(f"📝 Markdown Preview: {md_file}")
            
        else:
            print("❌ Invalid choice")
            
    except ValueError:
        print("❌ Invalid input")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

def main():
    """Main function."""
    print("🐦 Tweet Preview Viewer")
    print("=" * 30)
    
    if len(os.sys.argv) > 1 and os.sys.argv[1] == '--list':
        list_tweet_previews()
    else:
        view_specific_preview()

if __name__ == "__main__":
    main()
