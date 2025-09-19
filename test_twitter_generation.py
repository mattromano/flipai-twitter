#!/usr/bin/env python3
"""
Test script for Twitter content generation from analysis results.
"""

import json
import os
from src.twitter_generator import TwitterGenerator
from src.results_logger import ResultsLogger

def create_sample_analysis_data():
    """Create sample analysis data for testing."""
    return {
        "success": True,
        "timestamp": "2025-09-18T10:30:00",
        "data": {
            "response_text": """
            Based on the latest Bitcoin trading data analysis, here are the key insights:
            
            📊 **Price Analysis:**
            - Current price: $45,230 (+2.3% in 24h)
            - Volume: $2.1B (15% increase from yesterday)
            - Market cap: $890B
            
            📈 **Technical Indicators:**
            The chart shows a strong bullish trend with Bitcoin breaking through the $44,000 resistance level. 
            The RSI is at 65, indicating healthy momentum without being overbought.
            
            💡 **Key Finding:**
            Bitcoin has shown significant resilience with a 12% recovery from last week's dip, 
            suggesting strong institutional buying pressure.
            
            🎯 **Recommendation:**
            Consider buying on any dips below $44,500 as the trend remains bullish. 
            Watch for resistance at $46,000 level.
            
            The attached chart visualizes the price movement and volume patterns over the past 7 days.
            """,
            "response_metadata": {
                "word_count": 95,
                "has_charts": True,
                "has_tables": False,
                "has_code": False,
                "analysis_type": "market_analysis"
            },
            "artifacts": [
                {
                    "type": "chart",
                    "index": 1,
                    "screenshot": "screenshots/chart_1.png",
                    "selector": "canvas",
                    "tag_name": "canvas",
                    "size": {"width": 800, "height": 400},
                    "location": {"x": 100, "y": 200}
                }
            ],
            "screenshots": [
                "screenshots/full_page_20250918_103000.png",
                "screenshots/chart_1.png"
            ]
        }
    }

def create_sample_error_data():
    """Create sample error data for testing."""
    return {
        "success": False,
        "error": "Failed to navigate to chat page - element not found",
        "timestamp": "2025-09-18T10:30:00",
        "data": {}
    }

def test_twitter_generation():
    """Test the Twitter generation system."""
    print("🐦 Testing Twitter Content Generation")
    print("=" * 50)
    
    # Initialize generator
    generator = TwitterGenerator()
    
    # Test 1: Successful analysis
    print("\n1. Testing successful analysis tweet generation...")
    sample_data = create_sample_analysis_data()
    tweet_result = generator.generate_tweet_from_analysis(sample_data)
    
    if tweet_result["success"]:
        print("✅ Tweet generated successfully!")
        print("\n" + generator.format_tweet_for_display(tweet_result))
        
        # Save preview
        preview_path = generator.save_tweet_preview(tweet_result)
        if preview_path:
            print(f"\n💾 Tweet preview saved to: {preview_path}")
    else:
        print("❌ Tweet generation failed")
    
    # Test 2: Error case
    print("\n2. Testing error case tweet generation...")
    error_data = create_sample_error_data()
    error_tweet = generator.generate_tweet_from_analysis(error_data)
    
    print("\n" + generator.format_tweet_for_display(error_tweet))
    
    # Test 3: Different analysis types
    print("\n3. Testing different analysis types...")
    
    analysis_types = [
        ("volume_analysis", "📊 Volume analysis shows 15% increase in trading activity..."),
        ("user_analysis", "👥 User analysis reveals 2.3M active addresses this week..."),
        ("defi_analysis", "🏦 DeFi protocol analysis shows TVL increased by $500M...")
    ]
    
    for analysis_type, sample_text in analysis_types:
        test_data = {
            "success": True,
            "data": {
                "response_text": sample_text,
                "response_metadata": {
                    "analysis_type": analysis_type,
                    "word_count": 20
                },
                "artifacts": [],
                "screenshots": []
            }
        }
        
        tweet = generator.generate_tweet_from_analysis(test_data)
        print(f"\n{analysis_type}:")
        print(f"  Content: {tweet['content'][:100]}...")
        print(f"  Character count: {tweet['metadata']['character_count']}")
    
    print("\n🎉 Twitter generation test completed!")
    print("\nTo generate tweets from real analysis results:")
    print("  python generate_tweet.py")

if __name__ == "__main__":
    test_twitter_generation()
