#!/usr/bin/env python3
"""
Test the robust automation with proper timeouts and error handling.
"""

import os
import sys
from src.chat_automation_robust import RobustFlipsideChatAutomation
from src.automation_logger import setup_automation_logging

def test_robust_automation():
    """Test the robust automation with timeouts."""
    print("🔧 Testing Robust Flipside Chat Automation")
    print("=" * 60)
    
    # Setup enhanced logging
    debug_mode = os.getenv("DEBUG_MODE", "true").lower() == "true"
    logger = setup_automation_logging(debug_mode=debug_mode)
    
    if debug_mode:
        logger.log_info("Debug mode enabled - verbose logging active")
    else:
        logger.log_info("Standard logging mode - essential steps only")
    
    # Initialize automation
    automation = RobustFlipsideChatAutomation()
    
    try:
        # Run the analysis
        logger.log_info("Starting robust automation workflow...")
        results = automation.run_analysis()
        
        # Check results
        if results.get("success", False):
            logger.log_success("🎉 Automation completed successfully!")
            
            # Show results summary
            data = results.get("data", {})
            response_length = len(data.get("response_text", ""))
            artifacts_count = len(data.get("artifacts", []))
            screenshots_count = len(data.get("screenshots", []))
            
            print(f"\n📊 Results Summary:")
            print(f"  Response Length: {response_length} characters")
            print(f"  Artifacts Found: {artifacts_count}")
            print(f"  Screenshots Taken: {screenshots_count}")
            
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
    test_robust_automation()
