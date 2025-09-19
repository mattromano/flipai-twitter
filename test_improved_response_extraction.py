#!/usr/bin/env python3
"""
Improved response extraction that finds the actual chat response content first.
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

def test_improved_response_extraction():
    """Test extracting response with improved approach."""
    # Setup logging
    automation_logger = setup_automation_logger(debug_mode=True)
    error_logger, error_log_file = setup_error_logging()
    
    automation_logger.log_info("Starting improved response extraction test...")
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
        screenshot_path = automation.driver.save_screenshot(f"screenshots/improved_url_loaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        automation_logger.log_info(f"Screenshot saved: {screenshot_path}")
        
        # Step 4: First, try to find the actual chat response content
        automation_logger.log_info("Looking for chat response content...")
        
        # Look for various chat response containers
        response_selectors = [
            # Common chat response containers
            '[data-testid="message-content"]',
            '[data-testid="chat-message"]',
            '[data-testid="ai-response"]',
            '[data-testid="response"]',
            '.message-content',
            '.chat-message',
            '.ai-response',
            '.response-content',
            '.message-text',
            '.chat-response',
            # Look for content that might contain the response
            '[class*="message"]',
            '[class*="response"]',
            '[class*="content"]',
            # Look for divs that might contain the actual response text
            'div[class*="prose"]',
            'div[class*="markdown"]',
            'div[class*="text"]',
            # Look for any div that contains substantial text
            'div'
        ]
        
        response_content = None
        response_element = None
        
        for selector in response_selectors:
            try:
                automation_logger.log_info(f"Trying response selector: {selector}")
                elements = automation.driver.find_elements("css selector", selector)
                automation_logger.log_info(f"Found {len(elements)} elements with selector: {selector}")
                
                for i, element in enumerate(elements):
                    if element.is_displayed():
                        try:
                            text_content = element.text.strip()
                            if len(text_content) > 100:  # Look for substantial content
                                automation_logger.log_info(f"Element {i} has {len(text_content)} characters: {text_content[:100]}...")
                                
                                # Check if this looks like a chat response
                                if any(keyword in text_content.lower() for keyword in [
                                    'compound', 'aave', 'lending', 'ethereum', 'market', 'analysis',
                                    'defi', 'protocol', 'tvl', 'borrowing', 'interest', 'rate'
                                ]):
                                    response_content = text_content
                                    response_element = element
                                    automation_logger.log_success(f"Found potential response content in element {i}")
                                    break
                        except Exception as e:
                            automation_logger.log_warning(f"Error checking element {i}: {e}")
                            continue
                
                if response_content:
                    break
            except Exception as e:
                automation_logger.log_warning(f"Error with selector {selector}: {e}")
                continue
        
        if response_content:
            automation_logger.log_success(f"Found response content: {len(response_content)} characters")
            
            # Save the found content
            response_file = f"logs/found_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(response_content)
            automation_logger.log_success(f"Response saved to: {response_file}")
            
            # Now try to use the copy button on this specific element
            if response_element:
                automation_logger.log_info("Attempting to copy the response using the copy button...")
                
                # Look for copy button near this element
                copy_button = None
                
                # Try to find copy button relative to the response element
                try:
                    # Look for copy button in the same parent container
                    parent = response_element.find_element("xpath", "..")
                    copy_buttons = parent.find_elements("css selector", 'button[data-slot="tooltip-trigger"]')
                    
                    for btn in copy_buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            copy_button = btn
                            automation_logger.log_success("Found copy button near response element")
                            break
                except:
                    pass
                
                # If not found, try the original approach
                if not copy_button:
                    automation_logger.log_info("Looking for copy button with original selectors...")
                    copy_button_selectors = [
                        'button[data-slot="tooltip-trigger"]',
                        'button svg[class*="lucide-copy"]',
                        'button[title*="Copy"]',
                        'button[aria-label*="Copy"]'
                    ]
                    
                    for selector in copy_button_selectors:
                        try:
                            elements = automation.driver.find_elements("css selector", selector)
                            for element in elements:
                                if element.is_displayed() and element.is_enabled():
                                    # Check if it has the copy icon
                                    svg_elements = element.find_elements("css selector", "svg")
                                    for svg in svg_elements:
                                        svg_html = svg.get_attribute('outerHTML')
                                        if 'lucide-copy' in svg_html:
                                            copy_button = element
                                            automation_logger.log_success(f"Found copy button with selector: {selector}")
                                            break
                                    if copy_button:
                                        break
                            if copy_button:
                                break
                        except:
                            continue
                
                if copy_button:
                    automation_logger.log_info("Copy button found! Attempting to click it...")
                    
                    # Scroll to the button
                    automation.driver.execute_script("arguments[0].scrollIntoView(true);", copy_button)
                    time.sleep(1)
                    
                    # Click the copy button
                    copy_button.click()
                    automation_logger.log_success("Copy button clicked!")
                    
                    # Wait for copy operation
                    time.sleep(2)
                    
                    # Try to get clipboard content
                    try:
                        clipboard_content = pyperclip.paste()
                        automation_logger.log_info(f"Clipboard content: {len(clipboard_content)} characters")
                        
                        # Check if clipboard has actual response content
                        if len(clipboard_content) > 100 and clipboard_content != response_content:
                            clipboard_file = f"logs/clipboard_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                            with open(clipboard_file, 'w', encoding='utf-8') as f:
                                f.write(clipboard_content)
                            automation_logger.log_success(f"Clipboard response saved to: {clipboard_file}")
                            
                            return {
                                "success": True,
                                "response_text": clipboard_content,
                                "response_file": clipboard_file,
                                "length": len(clipboard_content),
                                "method": "clipboard"
                            }
                        else:
                            automation_logger.log_info("Clipboard content same as found content, using found content")
                            return {
                                "success": True,
                                "response_text": response_content,
                                "response_file": response_file,
                                "length": len(response_content),
                                "method": "direct_extraction"
                            }
                    except Exception as e:
                        automation_logger.log_warning(f"Clipboard error: {e}, using found content")
                        return {
                            "success": True,
                            "response_text": response_content,
                            "response_file": response_file,
                            "length": len(response_content),
                            "method": "direct_extraction"
                        }
                else:
                    automation_logger.log_warning("Copy button not found, using direct extraction")
                    return {
                        "success": True,
                        "response_text": response_content,
                        "response_file": response_file,
                        "length": len(response_content),
                        "method": "direct_extraction"
                    }
            else:
                return {
                    "success": True,
                    "response_text": response_content,
                    "response_file": response_file,
                    "length": len(response_content),
                    "method": "direct_extraction"
                }
        else:
            automation_logger.log_error("No response content found!")
            return {
                "success": False,
                "error": "No response content found",
                "response_text": "",
                "length": 0
            }
        
    except Exception as e:
        error_msg = f"Test failed: {e}"
        automation_logger.log_error(error_msg)
        error_logger.error(error_msg, exc_info=True)
        
        # Take error screenshot
        if automation.driver:
            try:
                automation.driver.save_screenshot(f"screenshots/error_improved_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
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
        results = test_improved_response_extraction()
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
