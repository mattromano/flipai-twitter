#!/usr/bin/env python3
"""
Load session cookies and click the Preview button on the correct URL to get full-screen artifact view.
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

def preview_with_authentication():
    """Load session cookies and click Preview button on the correct URL."""
    print("🔐 Loading session cookies and clicking Preview button...")
    
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
        debug_screenshot = f"screenshots/before_preview_auth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        automation.driver.save_screenshot(debug_screenshot)
        print(f"📸 Before preview screenshot saved: {debug_screenshot}")
        
        # Look for the Preview button
        print("🔍 Looking for Preview button...")
        
        # Try different approaches to find the Preview button
        preview_selectors = [
            '//span[text()="Preview"]',  # XPath for exact text match
            '//span[contains(text(), "Preview")]',  # XPath for partial text match
            '//button[.//span[text()="Preview"]]',  # XPath for button containing Preview span
            '//button[contains(text(), "Preview")]',  # XPath for button with Preview text
            'button[title*="Preview"]',  # CSS selector for button with Preview in title
            'button[aria-label*="Preview"]',  # CSS selector for button with Preview in aria-label
        ]
        
        preview_button = None
        for selector in preview_selectors:
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
                        if "Preview" in text or "preview" in text.lower():
                            preview_button = element
                            print(f"✅ Found Preview button with selector: {selector}")
                            print(f"   Button text: '{text}'")
                            break
                
                if preview_button:
                    break
            except Exception as e:
                print(f"❌ Selector {selector} failed: {e}")
                continue
        
        if not preview_button:
            print("❌ Preview button not found with any selector")
            # Let's see what buttons are available
            print("🔍 Checking all available buttons...")
            all_buttons = automation.driver.find_elements(By.TAG_NAME, "button")
            for i, button in enumerate(all_buttons):
                try:
                    text = button.text.strip()
                    if text:
                        print(f"   Button {i}: '{text}'")
                except:
                    pass
            
            # Let's also check all spans
            print("🔍 Checking all available spans...")
            all_spans = automation.driver.find_elements(By.TAG_NAME, "span")
            for i, span in enumerate(all_spans):
                try:
                    text = span.text.strip()
                    if text and len(text) < 20:  # Only show short text
                        print(f"   Span {i}: '{text}'")
                except:
                    pass
            
            return None
        
        # Click the Preview button
        print("👁️ Clicking Preview button...")
        automation.driver.execute_script("arguments[0].click();", preview_button)
        time.sleep(5)  # Wait for preview to load
        
        # Take a screenshot after clicking preview
        after_preview_screenshot = f"screenshots/after_preview_auth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        automation.driver.save_screenshot(after_preview_screenshot)
        print(f"📸 After preview screenshot saved: {after_preview_screenshot}")
        
        # Wait a bit more for the content to fully load
        print("⏳ Waiting for preview to load completely...")
        time.sleep(10)
        
        # Take a screenshot of the preview
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f"charts/preview_artifact_auth_{timestamp}.png"
        
        print("📸 Taking preview artifact screenshot...")
        automation.driver.save_screenshot(screenshot_path)
        
        # Get file details
        if os.path.exists(screenshot_path):
            file_size = os.path.getsize(screenshot_path)
            print(f"✅ Preview artifact screenshot saved: {screenshot_path}")
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
        print(f"❌ Error during preview and screenshot: {e}")
        # Take an error screenshot
        error_screenshot_path = f"screenshots/error_preview_auth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        try:
            automation.driver.save_screenshot(error_screenshot_path)
            print(f"📸 Error screenshot saved: {error_screenshot_path}")
        except:
            print("❌ Could not save error screenshot")
        return None
        
    finally:
        if automation.driver:
            automation.driver.quit()

def test_direct_screenshot_with_auth():
    """Test taking a direct screenshot with authentication loaded."""
    print("📸 Taking direct screenshot with authentication...")
    
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
        
        # Scroll to top to ensure we capture everything
        print("📜 Scrolling to top...")
        automation.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # Take a direct screenshot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f"charts/direct_artifact_auth_{timestamp}.png"
        
        print("📸 Taking direct artifact screenshot...")
        automation.driver.save_screenshot(screenshot_path)
        
        # Get file details
        if os.path.exists(screenshot_path):
            file_size = os.path.getsize(screenshot_path)
            print(f"✅ Direct artifact screenshot saved: {screenshot_path}")
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
        print(f"❌ Error during direct screenshot: {e}")
        return None
        
    finally:
        if automation.driver:
            automation.driver.quit()

if __name__ == "__main__":
    # Try preview approach with authentication first
    print("=== Preview with Authentication ===")
    preview_result = preview_with_authentication()
    
    if not preview_result:
        print("\n=== Direct Screenshot with Authentication Fallback ===")
        direct_result = test_direct_screenshot_with_auth()
        
        if direct_result:
            print(f"\n🎉 Success! Direct artifact screenshot: {direct_result}")
        else:
            print("\n❌ Both approaches failed")
    else:
        print(f"\n🎉 Success! Preview artifact screenshot: {preview_result}")
