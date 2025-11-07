#!/usr/bin/env python3
"""
Test Twitter API connection and credentials without posting anything.
This script uses a read-only endpoint to verify credentials and permissions.
"""

import sys
import os

# Try to load environment variables from .env file (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, assume environment variables are already set
    pass

# Add modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.twitter_manager.twitter_poster import TwitterPoster

def main():
    """Test Twitter API connection."""
    print("=" * 60)
    print("🔍 Twitter API Connection Test")
    print("=" * 60)
    print("This test uses a READ-ONLY endpoint - no tweets will be posted.")
    print()
    
    # Check if credentials are set
    required_vars = [
        "TWITTER_API_KEY", "TWITTER_API_SECRET",
        "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_TOKEN_SECRET",
        "TWITTER_BEARER_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        # Also check alternate names
        alt_var = var.replace("TWITTER_API_KEY", "TWITTER_CONSUMER_KEY")
        alt_var = alt_var.replace("TWITTER_API_SECRET", "TWITTER_CONSUMER_SECRET")
        
        if not os.getenv(var) and not os.getenv(alt_var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file or environment.")
        return 1
    
    print("✅ All required environment variables are set")
    print()
    
    # Initialize Twitter poster
    try:
        twitter_poster = TwitterPoster()
        print()
    except Exception as e:
        print(f"❌ Failed to initialize Twitter poster: {e}")
        return 1
    
    # Test API connection
    print("Testing API connection...")
    print("-" * 60)
    result = twitter_poster.test_api_connection()
    print()
    
    # Display results
    print("=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    
    if result.get("success"):
        print("✅ Connection test PASSED")
        print(f"   Username: @{result.get('username', 'Unknown')}")
        print(f"   Name: {result.get('name', 'Unknown')}")
        print(f"   User ID: {result.get('user_id', 'Unknown')}")
        print()
        print("Your Twitter API credentials are working correctly!")
        return 0
    else:
        print("❌ Connection test FAILED")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        print(f"   Error Type: {result.get('error_type', 'Unknown')}")
        
        if result.get('status_code'):
            print(f"   HTTP Status: {result.get('status_code')}")
        
        if result.get('api_codes'):
            print(f"   API Error Codes: {result.get('api_codes')}")
        
        print()
        print("This indicates a problem with:")
        print("   - API credentials (invalid keys/tokens)")
        print("   - API permissions (missing read permissions)")
        print("   - Account status (suspended/restricted)")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

