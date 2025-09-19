#!/usr/bin/env python3
"""
Create a sample analysis result file for testing Twitter generation.
"""

import json
from datetime import datetime
from pathlib import Path

def create_sample_analysis():
    """Create a realistic sample analysis result."""
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create sample analysis data
    sample_analysis = {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "timestamp": datetime.now().isoformat(),
            "chat_url": "https://flipsidecrypto.xyz/chat/",
            "response_text": """
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
            """,
            "response_metadata": {
                "word_count": 185,
                "has_charts": True,
                "has_tables": False,
                "has_code": False,
                "analysis_type": "market_analysis"
            },
            "screenshots": [
                "screenshots/full_page_20250918_103000.png",
                "screenshots/chart_1.png"
            ],
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
            ]
        }
    }
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_{timestamp}.json"
    filepath = logs_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(sample_analysis, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Sample analysis created: {filepath}")
    print(f"📊 Analysis contains:")
    print(f"   - Response text: {len(sample_analysis['data']['response_text'])} characters")
    print(f"   - Analysis type: {sample_analysis['data']['response_metadata']['analysis_type']}")
    print(f"   - Artifacts: {len(sample_analysis['data']['artifacts'])}")
    print(f"   - Screenshots: {len(sample_analysis['data']['screenshots'])}")
    
    return str(filepath)

if __name__ == "__main__":
    create_sample_analysis()
