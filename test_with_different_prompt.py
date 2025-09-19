#!/usr/bin/env python3
"""
Test the robust automation with a different prompt.
"""

import os
import sys
from src.chat_automation_robust import RobustFlipsideChatAutomation
from src.automation_logger import setup_automation_logging
from config.prompts import AnalysisPrompts

def test_with_different_prompt():
    """Test with a different prompt from the collection."""
    print("🔧 Testing Robust Automation with Different Prompt")
    print("=" * 60)
    
    # Setup enhanced logging
    debug_mode = os.getenv("DEBUG_MODE", "true").lower() == "true"
    logger = setup_automation_logging(debug_mode=debug_mode)
    
    if debug_mode:
        logger.log_info("Debug mode enabled - verbose logging active")
    else:
        logger.log_info("Standard logging mode - essential steps only")
    
    # Get a different prompt
    market_prompts = AnalysisPrompts.MARKET_INSIGHTS
    selected_prompt = market_prompts[1]  # "Analyze stablecoin supply and usage patterns..."
    
    print(f"📝 Using prompt: {selected_prompt}")
    print()
    
    # Initialize automation
    automation = RobustFlipsideChatAutomation()
    
    try:
        # Run the analysis
        logger.log_info("Starting robust automation workflow...")
        
        # Run automation with custom prompt
        results = automation.run_analysis(custom_prompt=selected_prompt)
        
        # Check results
        if results.get("success", False):
            logger.log_success("🎉 Automation completed successfully!")
            
            # Show results summary
            data = results.get("data", {})
            response_length = len(data.get("response_text", ""))
            artifacts_count = len(data.get("artifacts", []))
            screenshots_count = len(data.get("screenshots", []))
            chat_url = data.get("chat_url", "")
            
            print(f"\n📊 Results Summary:")
            print(f"  Response Length: {response_length} characters")
            print(f"  Artifacts Found: {artifacts_count}")
            print(f"  Screenshots Taken: {screenshots_count}")
            print(f"  Chat URL: {chat_url}")
            
            if response_length > 0:
                print(f"\n📝 Response Preview:")
                response_text = data.get("response_text", "")
                preview = response_text[:300] + "..." if len(response_text) > 300 else response_text
                print(f"  {preview}")
            
            # Show artifacts
            if artifacts_count > 0:
                print(f"\n🖼️  Artifacts Found:")
                for i, artifact in enumerate(data.get("artifacts", []), 1):
                    print(f"  {i}. {artifact.get('type', 'unknown')} - {artifact.get('screenshot', 'N/A')}")
            
        else:
            logger.log_error("❌ Automation failed!")
            error = results.get("error", "Unknown error")
            print(f"\n🚨 Error: {error}")
            
    except KeyboardInterrupt:
        logger.log_warning("Automation interrupted by user")
        print("\n⏹️  Automation stopped by user")
        
    except Exception as e:
        logger.log_error(f"Unexpected error: {e}")
        print(f"\n💥 Unexpected error: {e}")
    
    print("\n🏁 Automation session ended")

if __name__ == "__main__":
    test_with_different_prompt()
