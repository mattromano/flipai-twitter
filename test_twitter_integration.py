#!/usr/bin/env python3
"""
Test script for Twitter integration.
Tests the Twitter posting functionality without running the full automation.
"""

import os
import sys
import json
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from twitter_poster import TwitterPoster


def test_twitter_setup():
    """Test Twitter API setup."""
    print("🧪 Testing Twitter API Setup")
    print("=" * 40)
    
    poster = TwitterPoster()
    
    if not poster.credentials_available:
        print("❌ Twitter credentials not configured")
        print("Run: python setup_twitter.py")
        return False
    
    if not poster.setup_twitter_client():
        print("❌ Failed to setup Twitter client")
        return False
    
    print("✅ Twitter API setup successful")
    return True


def test_tweet_generation():
    """Test tweet generation from sample data."""
    print("\n🧪 Testing Tweet Generation")
    print("=" * 40)
    
    # Sample analysis data
    sample_analysis = {
        "success": True,
        "data": {
            "response_text": """
            TWITTER_TEXT: 
            
            📊 USDT vs USDC Supply Analysis:
            
            Key findings from our analysis of stablecoin supply across blockchains:
            
            • USDT dominates with $120B+ total supply
            • USDC follows with $32B+ supply  
            • Ethereum leads with 60% of total supply
            • Tron shows significant USDT adoption at 35%
            • Polygon and Arbitrum growing rapidly
            
            The stablecoin market shows clear dominance patterns with USDT leading across most chains. USDC maintains strong presence on Ethereum while USDT has diversified to multiple chains.
            
            HTML_CHART: [Chart data would be here]
            """,
            "artifacts": [
                {
                    "type": "chart",
                    "screenshot": "charts/published_artifact_20250918_170448.png"
                }
            ],
            "screenshots": ["charts/published_artifact_20250918_170448.png"],
            "response_metadata": {
                "analysis_type": "defi_analysis",
                "word_count": 150
            }
        }
    }
    
    poster = TwitterPoster()
    tweet_data = poster.twitter_generator.generate_tweet_from_analysis(sample_analysis)
    
    if tweet_data.get("success", False):
        print("✅ Tweet generation successful")
        print(f"📝 Content: {tweet_data['content'][:100]}...")
        print(f"🖼️  Image: {tweet_data.get('image', 'None')}")
        print(f"📊 Character count: {len(tweet_data['content'])}")
        return True
    else:
        print("❌ Tweet generation failed")
        return False


def test_preview_tweet():
    """Test tweet preview functionality."""
    print("\n🧪 Testing Tweet Preview")
    print("=" * 40)
    
    # Find latest analysis file
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("❌ No logs directory found")
        return False
    
    analysis_files = list(logs_dir.glob("analysis_*.json"))
    if not analysis_files:
        print("❌ No analysis files found")
        return False
    
    # Get the most recent analysis file
    latest_analysis_file = max(analysis_files, key=os.path.getctime)
    
    try:
        with open(latest_analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        poster = TwitterPoster()
        preview = poster.preview_tweet(analysis_data)
        
        print("✅ Tweet preview generated:")
        print(preview)
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate preview: {e}")
        return False


def test_dry_run_posting():
    """Test posting without actually posting (dry run)."""
    print("\n🧪 Testing Dry Run Posting")
    print("=" * 40)
    
    # Find latest analysis file
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print("❌ No logs directory found")
        return False
    
    analysis_files = list(logs_dir.glob("analysis_*.json"))
    if not analysis_files:
        print("❌ No analysis files found")
        return False
    
    # Get the most recent analysis file
    latest_analysis_file = max(analysis_files, key=os.path.getctime)
    
    try:
        with open(latest_analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        poster = TwitterPoster()
        
        # Generate tweet data
        tweet_data = poster.twitter_generator.generate_tweet_from_analysis(analysis_data)
        
        if not tweet_data.get("success", False):
            print("❌ Failed to generate tweet data")
            return False
        
        print("✅ Dry run successful")
        print(f"📝 Would post: {tweet_data['content'][:100]}...")
        print(f"🖼️  With image: {tweet_data.get('image', 'None')}")
        
        # Ask if user wants to actually post
        response = input("\n🤔 Do you want to actually post this tweet? (y/n): ").lower().strip()
        if response == 'y':
            result = poster.post_tweet(
                text=tweet_data["content"],
                image_path=tweet_data.get("image")
            )
            
            if result["success"]:
                print("✅ Tweet posted successfully!")
                print(f"📱 Tweet ID: {result['tweet_id']}")
            else:
                print(f"❌ Failed to post: {result['error']}")
        else:
            print("⏭️ Skipped actual posting")
        
        return True
        
    except Exception as e:
        print(f"❌ Dry run failed: {e}")
        return False


def post_custom_tweet(tweet_text: str, image_path: str = None):
    """Post a custom tweet with optional image."""
    print("🐦 Posting Custom Tweet")
    print("=" * 40)
    
    if not tweet_text:
        print("❌ No tweet text provided")
        return False
    
    print(f"📝 Tweet: {tweet_text}")
    if image_path:
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"🖼️  Image: {image_path} ({file_size:,} bytes)")
        else:
            print(f"❌ Image file not found: {image_path}")
            return False
    else:
        print("🖼️  Image: None")
    
    try:
        poster = TwitterPoster()
        
        if not poster.credentials_available:
            print("❌ Twitter credentials not configured")
            return False
        
        if not poster.setup_twitter_client():
            print("❌ Failed to setup Twitter client")
            return False
        
        # Post the tweet
        result = poster.post_tweet(tweet_text, image_path)
        
        if result["success"]:
            print("✅ Tweet posted successfully!")
            print(f"📱 Tweet ID: {result['tweet_id']}")
            print(f"🔗 Tweet URL: https://twitter.com/user/status/{result['tweet_id']}")
            return True
        else:
            print(f"❌ Failed to post tweet: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        return False


def main():
    """Main function with command-line support."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Twitter Integration Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python test_twitter_integration.py
  
  # Post a custom tweet
  python test_twitter_integration.py --post "Hello Twitter!" --image charts/chart.png
  
  # Post text only
  python test_twitter_integration.py --post "Just text, no image"
  
  # Test specific functionality
  python test_twitter_integration.py --test setup
  python test_twitter_integration.py --test generation
        """
    )
    
    parser.add_argument("--post", "-p", help="Post a custom tweet with this text")
    parser.add_argument("--image", "-i", help="Path to image file to include with tweet")
    parser.add_argument("--test", "-t", choices=["setup", "generation", "preview", "dryrun"], 
                       help="Run a specific test only")
    
    args = parser.parse_args()
    
    # If posting a custom tweet
    if args.post:
        success = post_custom_tweet(args.post, args.image)
        sys.exit(0 if success else 1)
    
    # If running specific test
    if args.test:
        print(f"🧪 Running {args.test} test only")
        print("=" * 40)
        
        test_functions = {
            "setup": test_twitter_setup,
            "generation": test_tweet_generation,
            "preview": test_preview_tweet,
            "dryrun": test_dry_run_posting,
        }
        
        test_func = test_functions[args.test]
        try:
            result = test_func()
            if result:
                print(f"✅ {args.test} test passed!")
            else:
                print(f"❌ {args.test} test failed!")
            sys.exit(0 if result else 1)
        except Exception as e:
            print(f"❌ {args.test} test failed with exception: {e}")
            sys.exit(1)
    
    # Run all tests (default behavior)
    print("🧪 Twitter Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Twitter Setup", test_twitter_setup),
        ("Tweet Generation", test_tweet_generation),
        ("Tweet Preview", test_preview_tweet),
        ("Dry Run Posting", test_dry_run_posting),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📋 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Twitter integration is ready.")
    else:
        print("⚠️ Some tests failed. Check the setup and try again.")


if __name__ == "__main__":
    main()
