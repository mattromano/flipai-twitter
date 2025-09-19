#!/usr/bin/env python3
"""
Direct URL test to extract response from a specific chat URL using clipboard copy.
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

def test_direct_url_extraction():
    """Test extracting response from a direct chat URL using clipboard copy."""
    # Setup logging
    automation_logger = setup_automation_logging(debug_mode=True)
    error_logger, error_log_file = setup_error_logging()
    
    automation_logger.log_info("Starting direct URL response extraction test...")
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
        screenshot_path = automation.driver.save_screenshot(f"screenshots/direct_url_loaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        automation_logger.log_info(f"Screenshot saved: {screenshot_path}")
        
        # Step 4: Look for the specific copy button you identified
        automation_logger.log_info("Looking for the specific copy button...")
        
        # The specific copy button selector based on your HTML
        copy_button_selectors = [
            # Most specific - the exact button you provided
            'button[data-slot="tooltip-trigger"]',
            # More specific selectors
            'button[data-slot="tooltip-trigger"] svg.lucide-copy',
            'button:has(svg.lucide-copy)',
            # Fallback selectors
            'button[class*="lucide-copy"]',
            'button svg[class*="lucide-copy"]',
            # Generic copy button selectors
            'button[title*="Copy"]',
            'button[aria-label*="Copy"]',
            'button:has-text("Copy")',
            # Look for buttons with copy icon
            'button svg[viewBox="0 0 24 24"]',
            # Generic button selectors in the chat area
            'button[class*="copy"]',
            'button[class*="Copy"]'
        ]
        
        copy_button = None
        for selector in copy_button_selectors:
            try:
                automation_logger.log_info(f"Trying selector: {selector}")
                elements = automation.driver.find_elements("css selector", selector)
                automation_logger.log_info(f"Found {len(elements)} elements with selector: {selector}")
                
                for i, element in enumerate(elements):
                    if element.is_displayed() and element.is_enabled():
                        # Check if it's the copy button by looking for the copy icon
                        try:
                            # Look for the copy icon SVG
                            svg_elements = element.find_elements("css selector", "svg")
                            is_copy_button = False
                            
                            for svg in svg_elements:
                                svg_html = svg.get_attribute('outerHTML')
                                if 'lucide-copy' in svg_html or 'copy' in svg_html.lower():
                                    is_copy_button = True
                                    break
                            
                            # Also check for copy-related text or attributes
                            element_text = element.text.lower()
                            element_title = (element.get_attribute('title') or '').lower()
                            element_aria_label = (element.get_attribute('aria-label') or '').lower()
                            
                            if (is_copy_button or 
                                'copy' in element_text or 
                                'copy' in element_title or 
                                'copy' in element_aria_label):
                                copy_button = element
                                automation_logger.log_success(f"Found copy button with selector: {selector} - Element {i}")
                                break
                        except Exception as e:
                            automation_logger.log_warning(f"Error checking element {i}: {e}")
                            continue
                
                if copy_button:
                    break
            except Exception as e:
                automation_logger.log_warning(f"Error with selector {selector}: {e}")
                continue
        
        if not copy_button:
            automation_logger.log_warning("Copy button not found with specific selectors")
            # Take screenshot for debugging
            automation.driver.save_screenshot(f"screenshots/copy_button_not_found_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            
            # Try to find any button that might be a copy button
            automation_logger.log_info("Trying to find any potential copy button...")
            all_buttons = automation.driver.find_elements("css selector", "button")
            automation_logger.log_info(f"Found {len(all_buttons)} total buttons on page")
            
            for i, button in enumerate(all_buttons):
                if button.is_displayed() and button.is_enabled():
                    try:
                        button_html = button.get_attribute('outerHTML')
                        if 'copy' in button_html.lower() or 'lucide-copy' in button_html:
                            copy_button = button
                            automation_logger.log_success(f"Found potential copy button: Button {i}")
                            break
                    except:
                        continue
        
        if copy_button:
            automation_logger.log_info("Copy button found! Attempting to click it...")
            
            # Scroll to the button to ensure it's visible
            automation.driver.execute_script("arguments[0].scrollIntoView(true);", copy_button)
            time.sleep(1)
            
            # Click the copy button
            copy_button.click()
            automation_logger.log_success("Copy button clicked!")
            
            # Wait a moment for the copy operation to complete
            time.sleep(2)
            
            # Try to get the clipboard content
            try:
                clipboard_content = pyperclip.paste()
                automation_logger.log_success(f"Clipboard content retrieved: {len(clipboard_content)} characters")
                
                # Save the clipboard content to a file
                response_file = f"logs/clipboard_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(response_file, 'w', encoding='utf-8') as f:
                    f.write(clipboard_content)
                automation_logger.log_success(f"Response saved to: {response_file}")
                
                # Log a preview of the content
                preview = clipboard_content[:500] + "..." if len(clipboard_content) > 500 else clipboard_content
                automation_logger.log_info(f"Response preview: {preview}")
                
                return {
                    "success": True,
                    "response_text": clipboard_content,
                    "response_file": response_file,
                    "length": len(clipboard_content)
                }
                
            except Exception as e:
                automation_logger.log_error(f"Failed to get clipboard content: {e}")
                return {
                    "success": False,
                    "error": f"Clipboard error: {e}",
                    "response_text": "",
                    "length": 0
                }
        else:
            automation_logger.log_error("Copy button not found!")
            return {
                "success": False,
                "error": "Copy button not found",
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
                automation.driver.save_screenshot(f"screenshots/error_direct_url_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
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
        results = test_direct_url_extraction()
        if results["success"]:
            print("✅ Test completed successfully!")
            print(f"Response text length: {results['length']}")
            print(f"Response saved to: {results['response_file']}")
        else:
            print(f"❌ Test failed: {results['error']}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
