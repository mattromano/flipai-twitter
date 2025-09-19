#!/usr/bin/env python3
"""
Working extraction script based on the actual page structure analysis.
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

def extract_response_from_page_text(page_text):
    """Extract the actual response content from the full page text."""
    lines = page_text.split('\n')
    
    # Find the start of the response (after the prompt)
    response_start = -1
    for i, line in enumerate(lines):
        if 'Analyze decentralized lending protocols' in line or 'I\'ll analyze' in line:
            response_start = i
            break
    
    if response_start == -1:
        return None
    
    # Extract the response content
    response_lines = []
    in_response = False
    
    for i in range(response_start, len(lines)):
        line = lines[i].strip()
        
        # Skip empty lines at the start
        if not line and not in_response:
            continue
            
        # Start collecting when we hit the actual response
        if 'I\'ll analyze' in line or 'Let me start' in line:
            in_response = True
        
        if in_response:
            # Stop at certain UI elements that indicate end of response
            if line in ['Copy message', 'Regenerate response', 'Twitter Response Formats']:
                break
            response_lines.append(line)
    
    return '\n'.join(response_lines)

def extract_twitter_text(response_text):
    """Extract the TWITTER_TEXT section from the response."""
    lines = response_text.split('\n')
    twitter_text = None
    
    for i, line in enumerate(lines):
        if 'TWITTER_TEXT:' in line:
            # Get the text after "TWITTER_TEXT:"
            twitter_text = line.split('TWITTER_TEXT:', 1)[1].strip()
            break
    
    return twitter_text

def test_working_extraction():
    """Test the working extraction approach."""
    # Setup logging
    automation_logger = setup_automation_logger(debug_mode=True)
    error_logger, error_log_file = setup_error_logging()
    
    automation_logger.log_info("Starting working extraction test...")
    automation_logger.log_info(f"Error log file: {error_log_file}")
    
    automation = RobustFlipsideChatAutomation()
    
    try:
        # Setup WebDriver
        automation_logger.log_info("Setting up Chrome WebDriver...")
        if not automation.setup_chrome_driver():
            raise Exception("Failed to setup Chrome driver")
        
        # Setup session
        automation_logger.log_info("Setting up session...")
        if not automation.setup_session_with_timeout(60):
            raise Exception("Failed to setup session")
        
        # Navigate to the specific chat URL
        target_url = "https://flipsidecrypto.xyz/chat/ba2e61e8-329c-4410-9d3d-cffdbe5417e1"
        automation_logger.log_info(f"Navigating to: {target_url}")
        automation.driver.get(target_url)
        
        # Wait for page to load
        time.sleep(5)
        automation_logger.log_success("Page loaded")
        
        # Get the full page text
        page_text = automation.driver.find_element("tag name", "body").text
        automation_logger.log_info(f"Page text length: {len(page_text)}")
        
        # Extract the response content
        automation_logger.log_info("Extracting response content...")
        response_text = extract_response_from_page_text(page_text)
        
        if response_text:
            automation_logger.log_success(f"Extracted response: {len(response_text)} characters")
            
            # Save the full response
            response_file = f"logs/working_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(response_text)
            automation_logger.log_success(f"Full response saved to: {response_file}")
            
            # Extract Twitter text
            twitter_text = extract_twitter_text(response_text)
            if twitter_text:
                automation_logger.log_success(f"Extracted Twitter text: {twitter_text}")
                
                # Save Twitter text separately
                twitter_file = f"logs/twitter_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(twitter_file, 'w', encoding='utf-8') as f:
                    f.write(twitter_text)
                automation_logger.log_success(f"Twitter text saved to: {twitter_file}")
            else:
                automation_logger.log_warning("No Twitter text found in response")
            
            # Log a preview of the response
            preview = response_text[:500] + "..." if len(response_text) > 500 else response_text
            automation_logger.log_info(f"Response preview: {preview}")
            
            return {
                "success": True,
                "response_text": response_text,
                "twitter_text": twitter_text,
                "response_file": response_file,
                "twitter_file": twitter_file if twitter_text else None,
                "length": len(response_text)
            }
        else:
            automation_logger.log_error("Failed to extract response content")
            return {
                "success": False,
                "error": "Failed to extract response content",
                "response_text": "",
                "length": 0
            }
        
    except Exception as e:
        error_msg = f"Test failed: {e}"
        automation_logger.log_error(error_msg)
        error_logger.error(error_msg, exc_info=True)
        
        return {
            "success": False,
            "error": error_msg,
            "response_text": "",
            "length": 0
        }
    
    finally:
        if automation.driver:
            try:
                automation.driver.quit()
                automation_logger.log_info("WebDriver cleanup complete")
            except Exception as e:
                automation_logger.log_warning(f"Error during WebDriver cleanup: {e}")

if __name__ == "__main__":
    try:
        results = test_working_extraction()
        if results["success"]:
            print("✅ Test completed successfully!")
            print(f"Response text length: {results['length']}")
            print(f"Response saved to: {results['response_file']}")
            if results.get("twitter_text"):
                print(f"Twitter text: {results['twitter_text']}")
                print(f"Twitter text saved to: {results['twitter_file']}")
        else:
            print(f"❌ Test failed: {results['error']}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
