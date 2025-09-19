#!/usr/bin/env python3
"""
Complete demonstration of Twitter generation from analysis results.
"""

import json
from src.twitter_generator import TwitterGenerator
from src.tweet_formatter import TweetFormatter

def demo_complete_twitter_workflow():
    """Demonstrate the complete Twitter generation workflow."""
    print("🐦 Complete Twitter Generation Demo")
    print("=" * 60)
    
    # Sample analysis response
    sample_response = """
    🚀 **Bitcoin Market Analysis - September 18, 2025**
    
    Based on the latest on-chain data and trading metrics, here are the key insights:
    
    **📊 Price & Volume Metrics:**
    - Current BTC Price: $45,230 (+2.3% in 24h)
    - 24h Volume: $2.1B (15% increase from yesterday)
    - Market Cap: $890B
    - Dominance: 42.3%
    
    **📈 Technical Analysis:**
    Bitcoin has broken through the crucial $44,000 resistance level with strong volume support. 
    The RSI is at 65, indicating healthy momentum without being overbought. 
    The chart shows a clear bullish trend with higher highs and higher lows.
    
    **💡 Key Finding:**
    Institutional buying pressure is evident with large transactions (>$1M) increasing by 23% 
    this week. This suggests strong confidence in the current price levels.
    
    **🎯 Trading Recommendation:**
    Consider buying on any dips below $44,500 as the trend remains bullish. 
    Watch for resistance at $46,000 level. Stop loss at $43,200.
    
    **📊 On-Chain Insights:**
    - Active addresses: 1.2M (7-day average)
    - Exchange inflows: Down 12% (bullish signal)
    - Long-term holders: 68% of supply (all-time high)
    
    The attached chart visualizes the price movement, volume patterns, and key support/resistance levels.
    """
    
    print("📝 Original Analysis Response:")
    print("-" * 40)
    print(sample_response[:200] + "...")
    print()
    
    # Step 1: Extract components using TweetFormatter
    print("🔍 Step 1: Extracting Key Components")
    print("-" * 40)
    
    metrics = TweetFormatter.extract_key_metrics(sample_response)
    insights = TweetFormatter.extract_key_insights(sample_response)
    trends = TweetFormatter.extract_trends(sample_response)
    recommendations = TweetFormatter.extract_recommendations(sample_response)
    
    print(f"📊 Key Metrics: {metrics}")
    print(f"💡 Key Insights: {insights}")
    print(f"📈 Trends: {trends}")
    print(f"🎯 Recommendations: {recommendations}")
    print()
    
    # Step 2: Generate tweet using TweetFormatter
    print("🐦 Step 2: Generating Tweet Content")
    print("-" * 40)
    
    tweet_content = TweetFormatter.create_engaging_tweet(sample_response, "market_analysis")
    
    print("Generated Tweet:")
    print("=" * 50)
    print(tweet_content)
    print("=" * 50)
    print(f"Character count: {len(tweet_content)}")
    print()
    
    # Step 3: Create complete tweet data structure
    print("📋 Step 3: Complete Tweet Data Structure")
    print("-" * 40)
    
    tweet_data = {
        "content": tweet_content,
        "image": "screenshots/chart_1.png",
        "metadata": {
            "timestamp": "2025-09-18T10:30:00",
            "analysis_type": "market_analysis",
            "character_count": len(tweet_content),
            "has_artifacts": True,
            "artifact_types": ["chart"],
            "extracted_metrics": metrics,
            "extracted_insights": insights,
            "extracted_trends": trends,
            "extracted_recommendations": recommendations
        },
        "success": True
    }
    
    print("Tweet Data Structure:")
    print(json.dumps(tweet_data, indent=2))
    print()
    
    # Step 4: Show what would be posted
    print("🚀 Step 4: Final Tweet Ready for Posting")
    print("-" * 40)
    print("🐦 TWEET CONTENT:")
    print("=" * 50)
    print(tweet_data["content"])
    print("=" * 50)
    print(f"🖼️  IMAGE: {tweet_data['image']}")
    print(f"📊 ANALYSIS TYPE: {tweet_data['metadata']['analysis_type']}")
    print(f"📏 CHARACTER COUNT: {tweet_data['metadata']['character_count']}")
    print()
    
    # Step 5: Show different analysis types
    print("🎭 Step 5: Different Analysis Types")
    print("-" * 40)
    
    analysis_examples = [
        ("volume_analysis", "📊 Volume analysis shows 15% increase in trading activity with $2.1B in 24h volume. This suggests strong market participation and potential price momentum."),
        ("user_analysis", "👥 User analysis reveals 2.3M active addresses this week, up 8% from last week. New user adoption is accelerating with 150K new addresses daily."),
        ("defi_analysis", "🏦 DeFi protocol analysis shows TVL increased by $500M this week. Major protocols like Uniswap and Aave are seeing significant growth in user activity.")
    ]
    
    for analysis_type, sample_text in analysis_examples:
        tweet = TweetFormatter.create_engaging_tweet(sample_text, analysis_type)
        print(f"\n{analysis_type.upper()}:")
        print("-" * 30)
        print(tweet)
        print(f"Characters: {len(tweet)}")
    
    print("\n🎉 Demo completed!")
    print("\n💡 Key Features Demonstrated:")
    print("  ✅ Automatic metric extraction ($45,230, +2.3%, $2.1B)")
    print("  ✅ Key insight identification (institutional buying pressure)")
    print("  ✅ Trend analysis (bullish trend, resistance levels)")
    print("  ✅ Recommendation extraction (buy on dips, stop loss)")
    print("  ✅ Smart content formatting with emojis")
    print("  ✅ Hashtag optimization for character limits")
    print("  ✅ Analysis type-specific emojis and formatting")
    print("  ✅ Screenshot integration for visual content")

if __name__ == "__main__":
    demo_complete_twitter_workflow()
