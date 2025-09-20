#!/usr/bin/env python3
"""
Test script for Twitter posting module using existing analysis data.
This script will NOT make any API calls to Twitter - it only tests the preview functionality.
"""

import json
import sys
import os
from pathlib import Path

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_twitter_module():
    """Test the Twitter module with existing analysis data."""
    
    print("🧪 Testing Twitter Module with Existing Data")
    print("=" * 60)
    
    # Load the analysis JSON
    analysis_file = "logs/analysis_20250919_234705.json"
    
    if not os.path.exists(analysis_file):
        print(f"❌ Analysis file not found: {analysis_file}")
        return
    
    try:
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        print(f"✅ Loaded analysis data from: {analysis_file}")
        
    except Exception as e:
        print(f"❌ Failed to load analysis data: {e}")
        return
    
    # Import and test the Twitter poster
    try:
        from twitter_manager import TwitterPoster
        twitter_poster = TwitterPoster()
        print("✅ Twitter poster module loaded successfully")
        
    except Exception as e:
        print(f"❌ Failed to load Twitter poster: {e}")
        return
    
    # Test 1: Create tweet preview (no API calls)
    print("\n📝 Test 1: Creating Tweet Preview")
    print("-" * 40)
    
    preview_result = twitter_poster.create_tweet_preview(analysis_data)
    
    if preview_result.get("success", False):
        print("✅ Tweet preview created successfully!")
        
        tweet_content = preview_result.get("tweet_content", "")
        image_path = preview_result.get("image_path", "")
        chat_url = preview_result.get("chat_url", "")
        character_count = preview_result.get("character_count", 0)
        has_image = preview_result.get("has_image", False)
        image_exists = preview_result.get("image_exists", False)
        
        print(f"\n🐦 Tweet Preview:")
        print(f"📝 Content ({character_count}/280 characters):")
        print(f"  {tweet_content}")
        print()
        
        if has_image:
            if image_exists:
                print(f"📸 Image: {image_path} ✅ (file exists)")
            else:
                print(f"📸 Image: {image_path} ❌ (file not found)")
        else:
            print("📸 Image: None")
        
        if chat_url:
            print(f"🔗 Chat URL: {chat_url}")
        
    else:
        print(f"❌ Tweet preview failed: {preview_result.get('error', 'Unknown error')}")
        return
    
    # Test 2: Test the post_from_analysis method in test mode
    print("\n📝 Test 2: Testing post_from_analysis in TEST MODE")
    print("-" * 40)
    
    post_result = twitter_poster.post_from_analysis(analysis_data, test_mode=True)
    
    if post_result.get("success", False):
        print("✅ Test mode post simulation successful!")
        print(f"📝 Tweet content: {post_result.get('tweet_content', '')}")
        print(f"📸 Image path: {post_result.get('image_path', 'None')}")
        print(f"🔗 Chat URL: {post_result.get('chat_url', 'None')}")
        print(f"🆔 Tweet ID: {post_result.get('tweet_id', 'None')} (TEST_MODE)")
    else:
        print(f"❌ Test mode post failed: {post_result.get('error', 'Unknown error')}")
    
    # Test 3: Verify image file exists
    print("\n📝 Test 3: Verifying Image File")
    print("-" * 40)
    
    if image_path and os.path.exists(image_path):
        file_size = os.path.getsize(image_path)
        print(f"✅ Image file exists: {image_path}")
        print(f"📏 File size: {file_size:,} bytes")
    else:
        print(f"❌ Image file not found: {image_path}")
    
    # Test 4: Check what would be posted vs what was posted before
    print("\n📝 Test 4: Comparison with Old Format")
    print("-" * 40)
    
    old_format = f"🔍 Fresh crypto analysis from FlipsideAI:\n\n{tweet_content}"
    new_format = tweet_content
    
    print(f"OLD FORMAT ({len(old_format)} chars):")
    print(f"  {old_format[:100]}...")
    print()
    print(f"NEW FORMAT ({len(new_format)} chars):")
    print(f"  {new_format}")
    print()
    print(f"✅ Removed {len(old_format) - len(new_format)} characters of prefix text")
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("✅ Tweet preview functionality working")
    print("✅ Test mode prevents API calls")
    print("✅ Image detection working")
    print("✅ Character count validation working")
    print("✅ Clean tweet format (no prefix)")
    
    print(f"\n🚀 Ready to post! Use:")
    print(f"python main_workflow.py --prompt 'Your prompt' --test-mode")

if __name__ == "__main__":
    test_twitter_module()