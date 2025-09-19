#!/usr/bin/env python3
"""
Starting from the point where Publish has already been clicked.
Click the View button and switch to the new window that opens, then screenshot it.
"""

import os
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.chat_automation_robust import RobustFlipsideChatAutomation

def view_new_window_screenshot():
    """Click View button and switch to new window, then screenshot it."""
    print("👁️ Clicking View button and switching to new window...")
    
    automation = RobustFlipsideChatAutomation()
    
    try:
        # Setup WebDriver with authentication
        automation.setup_chrome_driver()
        automation.setup_session_with_timeout(60)
        
        # Navigate to the correct URL (assuming Publish was already clicked)
        target_url = "https://flipsidecrypto.xyz/chat/a0604692-3937-4e21-aaec-ef911ecfd1c6"
        print(f"🌐 Navigating to: {target_url}")
        automation.driver.get(target_url)
        
        # Wait for page to load completely
        print("⏳ Waiting for page to load completely...")
        time.sleep(10)
        
        # Take a screenshot to see the current state
        debug_screenshot = f"screenshots/before_view_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        automation.driver.save_screenshot(debug_screenshot)
        print(f"📸 Before view screenshot saved: {debug_screenshot}")
        
        # Get current window handles before clicking View
        original_window = automation.driver.current_window_handle
        print(f"📋 Original window handle: {original_window}")
        
        # Look for the View button
        print("🔍 Looking for View button...")
        
        # Try different approaches to find the View button
        view_selectors = [
            '//span[text()="View"]',  # XPath for exact text match
            '//span[contains(text(), "View")]',  # XPath for partial text match
            '//button[.//span[text()="View"]]',  # XPath for button containing View span
            '//button[contains(text(), "View")]',  # XPath for button with View text
        ]
        
        view_button = None
        for selector in view_selectors:
            try:
                elements = automation.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed():
                        text = element.text.strip()
                        if "View" in text:
                            # Check if it's in the upper right area
                            location = element.location
                            size = automation.driver.get_window_size()
                            if location['x'] > size['width'] * 0.5:  # Right half of screen
                                view_button = element
                                print(f"✅ Found View button with selector: {selector}")
                                print(f"   Button text: '{text}'")
                                print(f"   Button location: x={location['x']}, y={location['y']}")
                                break
                
                if view_button:
                    break
            except Exception as e:
                print(f"❌ Selector {selector} failed: {e}")
                continue
        
        if not view_button:
            print("❌ View button not found")
            # Let's see what buttons are available
            print("🔍 Checking all available buttons...")
            all_buttons = automation.driver.find_elements(By.TAG_NAME, "button")
            for i, button in enumerate(all_buttons):
                try:
                    text = button.text.strip()
                    if text:
                        location = button.location
                        print(f"   Button {i}: '{text}' at x={location['x']}, y={location['y']}")
                except:
                    pass
            return None
        
        # Click the View button
        print("👁️ Clicking View button...")
        automation.driver.execute_script("arguments[0].click();", view_button)
        time.sleep(3)  # Wait for new window to open
        
        # Get all window handles after clicking View
        all_windows = automation.driver.window_handles
        print(f"📋 All window handles after click: {all_windows}")
        
        # Find the new window
        new_window = None
        for window in all_windows:
            if window != original_window:
                new_window = window
                break
        
        if not new_window:
            print("❌ No new window opened")
            # Take a screenshot of current state
            debug_screenshot = f"screenshots/no_new_window_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            automation.driver.save_screenshot(debug_screenshot)
            print(f"📸 Debug screenshot saved: {debug_screenshot}")
            return None
        
        # Switch to the new window
        print(f"🔄 Switching to new window: {new_window}")
        automation.driver.switch_to.window(new_window)
        
        # Wait for the new page to load completely
        print("⏳ Waiting for new page to load completely...")
        time.sleep(10)
        
        # Take a screenshot of the new window
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f"charts/published_artifact_new_window_{timestamp}.png"
        
        print("📸 Taking screenshot of the new window...")
        automation.driver.save_screenshot(screenshot_path)
        
        # Get file details
        if os.path.exists(screenshot_path):
            file_size = os.path.getsize(screenshot_path)
            print(f"✅ Published artifact screenshot saved: {screenshot_path}")
            print(f"📁 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            if file_size < 5 * 1024 * 1024:  # Under 5MB
                print("✅ Twitter-friendly file size")
            else:
                print("⚠️  Large file size for Twitter")
        else:
            print("❌ Screenshot file was not created")
            return None
        
        return screenshot_path
        
    except Exception as e:
        print(f"❌ Error during view -> new window -> screenshot: {e}")
        # Take an error screenshot
        error_screenshot_path = f"screenshots/error_view_window_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        try:
            automation.driver.save_screenshot(error_screenshot_path)
            print(f"📸 Error screenshot saved: {error_screenshot_path}")
        except:
            print("❌ Could not save error screenshot")
        return None
        
    finally:
        if automation.driver:
            automation.driver.quit()

def test_direct_url_approach():
    """Alternative approach: try to construct the published URL directly."""
    print("🔗 Testing direct URL approach...")
    
    automation = RobustFlipsideChatAutomation()
    
    try:
        # Setup WebDriver with authentication
        automation.setup_chrome_driver()
        automation.setup_session_with_timeout(60)
        
        # Try to construct the published URL
        # The pattern might be something like /shared/chats/...
        base_url = "https://flipsidecrypto.xyz"
        chat_id = "a0604692-3937-4e21-aaec-ef911ecfd1c6"
        
        # Try different possible published URL patterns
        possible_urls = [
            f"{base_url}/chat/shared/chats/{chat_id}",
            f"{base_url}/shared/chats/{chat_id}",
            f"{base_url}/chat/{chat_id}/published",
            f"{base_url}/chat/{chat_id}/view",
        ]
        
        for url in possible_urls:
            print(f"🌐 Trying URL: {url}")
            try:
                automation.driver.get(url)
                time.sleep(5)
                
                # Check if we got a valid page (not 404 or error)
                page_title = automation.driver.title
                if "404" not in page_title and "error" not in page_title.lower():
                    print(f"✅ Found valid page with title: {page_title}")
                    
                    # Take a screenshot
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    screenshot_path = f"charts/direct_url_artifact_{timestamp}.png"
                    automation.driver.save_screenshot(screenshot_path)
                    
                    if os.path.exists(screenshot_path):
                        file_size = os.path.getsize(screenshot_path)
                        print(f"✅ Direct URL screenshot saved: {screenshot_path}")
                        print(f"📁 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                        return screenshot_path
                else:
                    print(f"❌ Invalid page: {page_title}")
                    
            except Exception as e:
                print(f"❌ URL {url} failed: {e}")
                continue
        
        print("❌ No valid published URL found")
        return None
        
    except Exception as e:
        print(f"❌ Error during direct URL approach: {e}")
        return None
        
    finally:
        if automation.driver:
            automation.driver.quit()

if __name__ == "__main__":
    # Try the new window approach first
    print("=== View -> New Window -> Screenshot ===")
    result = view_new_window_screenshot()
    
    if not result:
        print("\n=== Direct URL Approach Fallback ===")
        direct_result = test_direct_url_approach()
        
        if direct_result:
            print(f"\n🎉 Success! Direct URL screenshot: {direct_result}")
        else:
            print("\n❌ Both approaches failed")
    else:
        print(f"\n🎉 Success! New window screenshot: {result}")
