#!/usr/bin/env python3
"""
1. Click the blue Publish button in upper right corner
2. Wait for it to change to View button
3. Click the View button to go to new page
4. Screenshot that new page
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

def publish_view_screenshot():
    """Click Publish -> View -> Screenshot the new page."""
    print("📤 Clicking Publish button, then View button, then screenshotting...")
    
    automation = RobustFlipsideChatAutomation()
    
    try:
        # Setup WebDriver with authentication
        automation.setup_chrome_driver()
        automation.setup_session_with_timeout(60)
        
        # Navigate to the correct URL
        target_url = "https://flipsidecrypto.xyz/chat/a0604692-3937-4e21-aaec-ef911ecfd1c6"
        print(f"🌐 Navigating to: {target_url}")
        automation.driver.get(target_url)
        
        # Wait for page to load completely
        print("⏳ Waiting for page to load completely...")
        time.sleep(10)
        
        # Take a screenshot to see the current state
        debug_screenshot = f"screenshots/before_publish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        automation.driver.save_screenshot(debug_screenshot)
        print(f"📸 Before publish screenshot saved: {debug_screenshot}")
        
        # Look for the blue Publish button in upper right corner
        print("🔍 Looking for blue Publish button in upper right corner...")
        
        # Try different approaches to find the Publish button
        publish_selectors = [
            '//span[text()="Publish"]',  # XPath for exact text match
            '//span[contains(text(), "Publish")]',  # XPath for partial text match
            '//button[.//span[text()="Publish"]]',  # XPath for button containing Publish span
            '//button[contains(text(), "Publish")]',  # XPath for button with Publish text
            'button[title*="Publish"]',  # CSS selector for button with Publish in title
            'button[aria-label*="Publish"]',  # CSS selector for button with Publish in aria-label
        ]
        
        publish_button = None
        for selector in publish_selectors:
            try:
                if selector.startswith('//'):
                    # XPath selector
                    elements = automation.driver.find_elements(By.XPATH, selector)
                else:
                    # CSS selector
                    elements = automation.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed():
                        text = element.text.strip()
                        if "Publish" in text or "publish" in text.lower():
                            # Check if it's in the upper right area
                            location = element.location
                            size = automation.driver.get_window_size()
                            if location['x'] > size['width'] * 0.5:  # Right half of screen
                                publish_button = element
                                print(f"✅ Found Publish button with selector: {selector}")
                                print(f"   Button text: '{text}'")
                                print(f"   Button location: x={location['x']}, y={location['y']}")
                                break
                
                if publish_button:
                    break
            except Exception as e:
                print(f"❌ Selector {selector} failed: {e}")
                continue
        
        if not publish_button:
            print("❌ Publish button not found with any selector")
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
        
        # Click the Publish button
        print("📤 Clicking Publish button...")
        automation.driver.execute_script("arguments[0].click();", publish_button)
        time.sleep(5)  # Wait for publish action to start
        
        # Take a screenshot after clicking publish
        after_publish_screenshot = f"screenshots/after_publish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        automation.driver.save_screenshot(after_publish_screenshot)
        print(f"📸 After publish screenshot saved: {after_publish_screenshot}")
        
        # Wait for the Publish button to change to View
        print("⏳ Waiting for Publish to change to View...")
        view_selectors = [
            '//span[text()="View"]',  # XPath for exact text match
            '//span[contains(text(), "View")]',  # XPath for partial text match
            '//button[.//span[text()="View"]]',  # XPath for button containing View span
            '//button[contains(text(), "View")]',  # XPath for button with View text
        ]
        
        view_button = None
        max_wait_time = 30  # Wait up to 30 seconds for the change
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
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
                except:
                    continue
            
            if view_button:
                break
            
            print("⏳ Still waiting for View button...")
            time.sleep(2)
        
        if not view_button:
            print("❌ View button not found after waiting")
            # Take a screenshot to see current state
            debug_screenshot = f"screenshots/view_button_not_found_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            automation.driver.save_screenshot(debug_screenshot)
            print(f"📸 Debug screenshot saved: {debug_screenshot}")
            return None
        
        # Click the View button to go to the new page
        print("👁️ Clicking View button to go to new page...")
        automation.driver.execute_script("arguments[0].click();", view_button)
        time.sleep(5)  # Wait for navigation to new page
        
        # Wait for the new page to load completely
        print("⏳ Waiting for new page to load completely...")
        time.sleep(10)
        
        # Take a screenshot of the new page
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f"charts/published_artifact_{timestamp}.png"
        
        print("📸 Taking screenshot of the published artifact page...")
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
        print(f"❌ Error during publish -> view -> screenshot: {e}")
        # Take an error screenshot
        error_screenshot_path = f"screenshots/error_publish_view_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        try:
            automation.driver.save_screenshot(error_screenshot_path)
            print(f"📸 Error screenshot saved: {error_screenshot_path}")
        except:
            print("❌ Could not save error screenshot")
        return None
        
    finally:
        if automation.driver:
            automation.driver.quit()

if __name__ == "__main__":
    result = publish_view_screenshot()
    
    if result:
        print(f"\n🎉 Success! Published artifact screenshot: {result}")
    else:
        print("\n❌ Failed to create published artifact screenshot")
