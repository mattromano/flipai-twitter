#!/usr/bin/env python3
"""
Test script for the enhanced monitoring capabilities.
"""

import os
import sys
from src.chat_automation import FlipsideChatAutomation
from src.results_logger import ResultsLogger

def test_monitoring():
    """Test the enhanced monitoring features."""
    print("🧪 Testing Enhanced Monitoring Features")
    print("=" * 50)
    
    # Test results logger
    print("\n1. Testing Results Logger...")
    logger = ResultsLogger()
    
    # Test logging a sample response
    sample_response = """
    Based on the analysis of Bitcoin trading data, here are the key insights:
    
    📊 **Price Analysis:**
    - Current price: $45,230
    - 24h change: +2.3%
    - Volume: $2.1B
    
    📈 **Chart Analysis:**
    The attached chart shows a bullish trend with strong support at $44,000.
    
    💡 **Recommendations:**
    - Consider buying on dips below $44,500
    - Watch for resistance at $46,000
    """
    
    sample_metadata = {
        "word_count": 45,
        "has_charts": True,
        "has_tables": False,
        "has_code": False,
        "analysis_type": "market_analysis"
    }
    
    log_path = logger.log_response_only(sample_response, sample_metadata)
    print(f"✅ Response logged to: {log_path}")
    
    # Test daily summary
    print("\n2. Testing Daily Summary...")
    summary = logger.get_daily_summary()
    print(f"✅ Daily summary: {summary}")
    
    # Test recent logs
    print("\n3. Testing Recent Logs...")
    recent_logs = logger.list_recent_logs(days=1)
    print(f"✅ Found {len(recent_logs)} recent logs")
    
    print("\n🎉 Monitoring test completed!")
    print("\nTo test the full automation with monitoring:")
    print("  source venv/bin/activate")
    print("  DEBUG_MODE=true python src/chat_automation.py")

if __name__ == "__main__":
    test_monitoring()
