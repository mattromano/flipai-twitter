#!/usr/bin/env python3
"""
Generate Twitter content from actual analysis results.
"""

import os
import sys
import json
from pathlib import Path
from src.twitter_generator import TwitterGenerator
from src.results_logger import ResultsLogger

def find_latest_analysis():
    """Find the most recent analysis result."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return None
    
    # Look for analysis files
    analysis_files = list(logs_dir.glob("analysis_*.json"))
    if not analysis_files:
        return None
    
    # Sort by modification time (newest first)
    analysis_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return analysis_files[0]

def load_analysis_data(file_path: Path):
    """Load analysis data from file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading analysis data: {e}")
        return None

def generate_tweet_from_latest():
    """Generate tweet from the latest analysis results."""
    print("🐦 Generating Tweet from Latest Analysis")
    print("=" * 50)
    
    # Find latest analysis
    latest_file = find_latest_analysis()
    if not latest_file:
        print("❌ No analysis results found in logs/ directory")
        print("   Run the automation first: python src/chat_automation.py")
        return
    
    print(f"📁 Using analysis file: {latest_file.name}")
    
    # Load analysis data
    analysis_data = load_analysis_data(latest_file)
    if not analysis_data:
        print("❌ Failed to load analysis data")
        return
    
    # Generate tweet
    generator = TwitterGenerator()
    tweet_result = generator.generate_tweet_from_analysis(analysis_data)
    
    if tweet_result["success"]:
        print("✅ Tweet generated successfully!")
        print("\n" + generator.format_tweet_for_display(tweet_result))
        
        # Save preview
        preview_path = generator.save_tweet_preview(tweet_result)
        if preview_path:
            print(f"\n💾 Tweet preview saved to: {preview_path}")
        
        # Show the actual tweet content
        print("\n" + "="*50)
        print("🐦 FINAL TWEET CONTENT:")
        print("="*50)
        print(tweet_result["content"])
        print("="*50)
        
        if tweet_result["image"]:
            print(f"\n🖼️  Tweet Image: {tweet_result['image']}")
        else:
            print("\n🖼️  No image available for this tweet")
            
    else:
        print("❌ Tweet generation failed")
        print(f"Error: {tweet_result.get('metadata', {}).get('error', 'Unknown error')}")

def generate_tweet_from_file(file_path: str):
    """Generate tweet from a specific analysis file."""
    print(f"🐦 Generating Tweet from: {file_path}")
    print("=" * 50)
    
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return
    
    # Load analysis data
    analysis_data = load_analysis_data(file_path)
    if not analysis_data:
        print("❌ Failed to load analysis data")
        return
    
    # Generate tweet
    generator = TwitterGenerator()
    tweet_result = generator.generate_tweet_from_analysis(analysis_data)
    
    if tweet_result["success"]:
        print("✅ Tweet generated successfully!")
        print("\n" + generator.format_tweet_for_display(tweet_result))
        
        # Save preview
        preview_path = generator.save_tweet_preview(tweet_result)
        if preview_path:
            print(f"\n💾 Tweet preview saved to: {preview_path}")
    else:
        print("❌ Tweet generation failed")

def list_available_analyses():
    """List available analysis files."""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("❌ No logs directory found")
        return
    
    analysis_files = list(logs_dir.glob("analysis_*.json"))
    if not analysis_files:
        print("❌ No analysis files found")
        return
    
    print("📁 Available Analysis Files:")
    print("-" * 30)
    
    for i, file_path in enumerate(analysis_files, 1):
        # Get file modification time
        mtime = file_path.stat().st_mtime
        from datetime import datetime
        mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"{i}. {file_path.name}")
        print(f"   Modified: {mtime_str}")
        
        # Try to load and show basic info
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                success = data.get("success", False)
                status = "✅" if success else "❌"
                print(f"   Status: {status}")
                
                if success and "data" in data:
                    response_length = len(data["data"].get("response_text", ""))
                    artifact_count = len(data["data"].get("artifacts", []))
                    print(f"   Response: {response_length} chars, {artifact_count} artifacts")
        except:
            print("   Status: ⚠️  (Error reading file)")
        print()

def main():
    """Main function."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_available_analyses()
        elif command == "file" and len(sys.argv) > 2:
            generate_tweet_from_file(sys.argv[2])
        elif command == "latest":
            generate_tweet_from_latest()
        else:
            print("Usage:")
            print("  python generate_tweet.py                    # Generate from latest analysis")
            print("  python generate_tweet.py latest             # Generate from latest analysis")
            print("  python generate_tweet.py list               # List available analyses")
            print("  python generate_tweet.py file <filename>    # Generate from specific file")
    else:
        # Default: generate from latest
        generate_tweet_from_latest()

if __name__ == "__main__":
    main()
