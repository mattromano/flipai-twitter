#!/usr/bin/env python3
"""
Simple script to post to Twitter with text and image.
This is a template - you'll need to add your Twitter API credentials.
"""

import os
import sys
from datetime import datetime

def post_to_twitter(twitter_text, image_path=None):
    """
    Post to Twitter with text and optional image.
    
    Args:
        twitter_text (str): The text to post
        image_path (str): Path to the image file (optional)
    
    Returns:
        bool: True if successful, False otherwise
    """
    print("🐦 Twitter Posting Template")
    print("=" * 40)
    print(f"📝 Text: {twitter_text}")
    if image_path and os.path.exists(image_path):
        file_size = os.path.getsize(image_path)
        print(f"🖼️  Image: {image_path} ({file_size:,} bytes)")
    else:
        print("🖼️  Image: None")
    print("=" * 40)
    
    # TODO: Add actual Twitter API integration here
    # You would need to:
    # 1. Install tweepy: pip install tweepy
    # 2. Set up Twitter API credentials
    # 3. Use tweepy to post the tweet
    
    print("📋 To implement actual Twitter posting:")
    print("1. Install tweepy: pip install tweepy")
    print("2. Set up Twitter API credentials")
    print("3. Use tweepy.Client to post tweets")
    print("4. For images, use tweepy.API.media_upload()")
    
    return True

def main():
    """Main function to test Twitter posting."""
    # Read the latest Twitter text
    outputs_dir = "outputs"
    if not os.path.exists(outputs_dir):
        print("❌ No outputs directory found. Run complete_workflow.py first.")
        return
    
    # Find the latest Twitter text file
    twitter_files = [f for f in os.listdir(outputs_dir) if f.startswith("twitter_text_")]
    if not twitter_files:
        print("❌ No Twitter text files found. Run complete_workflow.py first.")
        return
    
    latest_twitter_file = sorted(twitter_files)[-1]
    twitter_file_path = os.path.join(outputs_dir, latest_twitter_file)
    
    # Read Twitter text
    with open(twitter_file_path, 'r', encoding='utf-8') as f:
        twitter_text = f.read().strip()
    
    # Find the latest PNG chart
    charts_dir = "charts"
    if os.path.exists(charts_dir):
        png_files = [f for f in os.listdir(charts_dir) if f.endswith(".png")]
        if png_files:
            latest_png_file = sorted(png_files)[-1]
            image_path = os.path.join(charts_dir, latest_png_file)
        else:
            image_path = None
    else:
        image_path = None
    
    # Post to Twitter
    success = post_to_twitter(twitter_text, image_path)
    
    if success:
        print("✅ Twitter posting template completed successfully!")
    else:
        print("❌ Twitter posting failed")

if __name__ == "__main__":
    main()
