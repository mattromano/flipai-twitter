#!/usr/bin/env python3
"""
Focused test script to test response text extraction from Flipside chat.
"""

import os
import sys
import time
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.chat_automation_robust import RobustFlipsideChatAutomation
from src.automation_logger import setup_automation_logging

def setup_error_logging():
    """Set up error logging to a specific file."""
    error_logger = logging.getLogger('error_logger')
    error_logger.setLevel(logging.ERROR)
    
    # Create error log file
    error_log_file = f"logs/error_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    os.makedirs("logs", exist_ok=True)
    
    handler = logging.FileHandler(error_log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    error_logger.addHandler(handler)
    
    return error_logger, error_log_file

def test_response_extraction():
    """Test just the response text extraction part."""
    # Setup logging
    automation_logger = setup_automation_logging(debug_mode=True)  # Enable verbose logging
    error_logger, error_log_file = setup_error_logging()
    
    automation_logger.log_info("Starting focused response extraction test...")
    automation_logger.log_info(f"Error log file: {error_log_file}")
    
    automation = RobustFlipsideChatAutomation()
    
    try:
        # Step 1: Setup WebDriver
        automation_logger.log_info("Setting up Chrome WebDriver...")
        if not automation.setup_chrome_driver():
            raise Exception("Failed to setup Chrome driver")
        
        # Step 2: Setup session
        automation_logger.log_info("Setting up session...")
        if not automation.setup_session_with_timeout(60):
            raise Exception("Failed to setup session")
        
        # Step 3: Navigate to chat
        automation_logger.log_info("Navigating to chat page...")
        if not automation.navigate_to_chat_with_timeout(60):
            raise Exception("Failed to navigate to chat")
        
        # Step 4: Submit prompt
        automation_logger.log_info("Submitting prompt...")
        prompt = "Give me a full market comparison between compound and aave lending on Ethereum, look specifically how it has changed since 2019 to now"
        if not automation.submit_prompt_with_timeout(prompt, 60):
            raise Exception("Failed to submit prompt")
        
        # Step 5: Wait for response (shorter timeout for testing)
        automation_logger.log_info("Waiting for AI response...")
        automation.wait_for_complete_response_with_timeout(180)  # 3 minutes
        
        # Step 6: Try to copy response text
        automation_logger.log_info("Attempting to copy response text...")
        copy_success = automation._try_copy_response()
        automation_logger.log_info(f"Copy button clicked: {copy_success}")
        
        # Step 7: Extract response text
        automation_logger.log_info("Extracting response text...")
        results = automation.capture_results()
        
        # Log the results
        response_text = results.get("response_text", "")
        automation_logger.log_info(f"Extracted response text length: {len(response_text)}")
        automation_logger.log_info(f"Response text preview: {response_text[:200]}...")
        
        # Save response to file for inspection
        response_file = f"logs/extracted_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(response_file, 'w', encoding='utf-8') as f:
            f.write(response_text)
        automation_logger.log_info(f"Response saved to: {response_file}")
        
        # Take final screenshot
        if automation.driver:
            screenshot_path = automation.driver.save_screenshot(f"screenshots/test_response_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            automation_logger.log_info(f"Final screenshot saved: {screenshot_path}")
        
        return results
        
    except Exception as e:
        error_msg = f"Test failed: {e}"
        automation_logger.log_error(error_msg)
        error_logger.error(error_msg, exc_info=True)
        
        # Take error screenshot
        if automation.driver:
            try:
                automation.driver.save_screenshot(f"screenshots/error_response_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            except:
                pass
        
        raise
    
    finally:
        # Cleanup
        if automation.driver:
            try:
                automation.driver.quit()
                automation_logger.log_info("WebDriver cleanup complete")
            except Exception as e:
                automation_logger.log_warning(f"Error during WebDriver cleanup: {e}")

if __name__ == "__main__":
    try:
        results = test_response_extraction()
        print("✅ Test completed successfully!")
        print(f"Response text length: {len(results.get('response_text', ''))}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
