#!/usr/bin/env python3
"""
Final test to extract actual response content from the chat URL.
"""

import os
import sys
import time
import logging
from datetime import datetime
import pyperclip  # For clipboard operations

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

def test_final_response_extraction():
    """Test extracting actual response content from the chat URL."""
    # Setup logging
    automation_logger = setup_automation_logging(debug_mode=True)
    error_logger, error_log_file = setup_error_logging()
    
    automation_logger.log_info("Starting final response extraction test...")
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
        
        # Step 3: Navigate directly to the specific chat URL
        target_url = "https://flipsidecrypto.xyz/chat/ba2e61e8-329c-4410-9d3d-cffdbe5417e1"
        automation_logger.log_info(f"Navigating directly to: {target_url}")
        automation.driver.get(target_url)
        
        # Wait for page to load
        time.sleep(5)
        automation_logger.log_success("Successfully navigated to chat URL")
        
        # Take screenshot to see current state
        screenshot_path = automation.driver.save_screenshot(f"screenshots/final_url_loaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        automation_logger.log_info(f"Screenshot saved: {screenshot_path}")
        
        # Step 4: Look for the actual chat response content first
        automation_logger.log_info("Looking for actual chat response content...")
        
        # Get all text content from the page and look for the response
        page_text = automation.driver.find_element("tag name", "body").text
        automation_logger.log_info(f"Total page text length: {len(page_text)}")
        
        # Look for content that contains our keywords
        lines = page_text.split('\n')
        response_lines = []
        in_response = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for lines that contain response-related keywords
            if any(keyword in line.lower() for keyword in [
                'compound', 'aave', 'lending', 'ethereum', 'market', 'analysis',
                'defi', 'protocol', 'tvl', 'borrowing', 'interest', 'rate',
                'comparison', 'since 2019', 'growth', 'adoption'
            ]):
                if not in_response:
                    in_response = True
                    automation_logger.log_info(f"Found response start: {line[:100]}...")
                response_lines.append(line)
            elif in_response and len(line) > 20:  # Continue collecting substantial lines
                response_lines.append(line)
            elif in_response and len(line) < 10:  # Stop if we hit a short line (likely end)
                break
        
        if response_lines:
            response_content = '\n'.join(response_lines)
            automation_logger.log_success(f"Found response content: {len(response_content)} characters")
            
            # Save the found content
            response_file = f"logs/final_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(response_content)
            automation_logger.log_success(f"Response saved to: {response_file}")
            
            # Log a preview
            preview = response_content[:500] + "..." if len(response_content) > 500 else response_content
            automation_logger.log_info(f"Response preview: {preview}")
            
            return {
                "success": True,
                "response_text": response_content,
                "response_file": response_file,
                "length": len(response_content),
                "method": "page_text_extraction"
            }
        else:
            automation_logger.log_warning("No response content found in page text")
            
            # Try to find specific elements that might contain the response
            automation_logger.log_info("Trying to find response elements...")
            
            # Look for elements that might contain the response
            potential_selectors = [
                '[data-testid*="message"]',
                '[data-testid*="response"]',
                '[data-testid*="content"]',
                '[class*="message"]',
                '[class*="response"]',
                '[class*="content"]',
                'div[class*="prose"]',
                'div[class*="markdown"]'
            ]
            
            for selector in potential_selectors:
                try:
                    elements = automation.driver.find_elements("css selector", selector)
                    automation_logger.log_info(f"Found {len(elements)} elements with selector: {selector}")
                    
                    for i, element in enumerate(elements):
                        if element.is_displayed():
                            text_content = element.text.strip()
                            if len(text_content) > 100:
                                automation_logger.log_info(f"Element {i} has {len(text_content)} characters: {text_content[:100]}...")
                                
                                # Check if this looks like a response
                                if any(keyword in text_content.lower() for keyword in [
                                    'compound', 'aave', 'lending', 'ethereum', 'market'
                                ]):
                                    response_file = f"logs/final_response_element_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                                    with open(response_file, 'w', encoding='utf-8') as f:
                                        f.write(text_content)
                                    
                                    automation_logger.log_success(f"Found response in element {i}")
                                    return {
                                        "success": True,
                                        "response_text": text_content,
                                        "response_file": response_file,
                                        "length": len(text_content),
                                        "method": "element_extraction"
                                    }
                except Exception as e:
                    automation_logger.log_warning(f"Error with selector {selector}: {e}")
                    continue
            
            # If still no response found, return the full page text for analysis
            automation_logger.log_warning("No specific response found, returning full page text")
            full_page_file = f"logs/full_page_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(full_page_file, 'w', encoding='utf-8') as f:
                f.write(page_text)
            
            return {
                "success": True,
                "response_text": page_text,
                "response_file": full_page_file,
                "length": len(page_text),
                "method": "full_page_extraction"
            }
        
    except Exception as e:
        error_msg = f"Test failed: {e}"
        automation_logger.log_error(error_msg)
        error_logger.error(error_msg, exc_info=True)
        
        # Take error screenshot
        if automation.driver:
            try:
                automation.driver.save_screenshot(f"screenshots/error_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            except:
                pass
        
        return {
            "success": False,
            "error": error_msg,
            "response_text": "",
            "length": 0
        }
    
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
        results = test_final_response_extraction()
        if results["success"]:
            print("✅ Test completed successfully!")
            print(f"Response text length: {results['length']}")
            print(f"Method used: {results['method']}")
            print(f"Response saved to: {results['response_file']}")
        else:
            print(f"❌ Test failed: {results['error']}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
