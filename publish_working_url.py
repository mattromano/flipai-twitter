#!/usr/bin/env python3
"""
Click the Publish button on the working URL to get full-screen artifact view.
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

def publish_and_screenshot_working_url():
    """Click Publish button on the working URL and screenshot the full-screen artifact view."""
    print("📤 Publishing artifact from working URL and taking full-screen screenshot...")
    
    # Setup Chrome options for high-quality screenshots
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1600,1200")  # Large window for high quality
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Set high DPI for better quality
    chrome_options.add_argument("--force-device-scale-factor=2")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Use the working URL that has the artifact
        target_url = "https://flipsidecrypto.xyz/chat/shared/chats/b2753e8c-ab2a-40cb-82c3-e285450b7fec"
        print(f"🌐 Navigating to: {target_url}")
        driver.get(target_url)
        
        # Wait for page to load completely
        print("⏳ Waiting for page to load completely...")
        time.sleep(10)
        
        # Take a screenshot to see the current state
        debug_screenshot = f"screenshots/before_publish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(debug_screenshot)
        print(f"📸 Before publish screenshot saved: {debug_screenshot}")
        
        # Look for the Publish button
        print("🔍 Looking for Publish button...")
        
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
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    # CSS selector
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed():
                        text = element.text.strip()
                        if "Publish" in text or "publish" in text.lower():
                            publish_button = element
                            print(f"✅ Found Publish button with selector: {selector}")
                            print(f"   Button text: '{text}'")
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
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            for i, button in enumerate(all_buttons):
                try:
                    text = button.text.strip()
                    if text:
                        print(f"   Button {i}: '{text}'")
                except:
                    pass
            
            # Let's also check all spans
            print("🔍 Checking all available spans...")
            all_spans = driver.find_elements(By.TAG_NAME, "span")
            for i, span in enumerate(all_spans):
                try:
                    text = span.text.strip()
                    if text and len(text) < 20:  # Only show short text
                        print(f"   Span {i}: '{text}'")
                except:
                    pass
            
            return None
        
        # Click the Publish button
        print("📤 Clicking Publish button...")
        driver.execute_script("arguments[0].click();", publish_button)
        time.sleep(5)  # Wait for publish action to start
        
        # Take a screenshot after clicking publish
        after_publish_screenshot = f"screenshots/after_publish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(after_publish_screenshot)
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
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            text = element.text.strip()
                            if "View" in text:
                                view_button = element
                                print(f"✅ Found View button with selector: {selector}")
                                print(f"   Button text: '{text}'")
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
            driver.save_screenshot(debug_screenshot)
            print(f"📸 Debug screenshot saved: {debug_screenshot}")
            return None
        
        # Click the View button to open the full-screen view
        print("👁️ Clicking View button to open full-screen artifact...")
        driver.execute_script("arguments[0].click();", view_button)
        time.sleep(5)  # Wait for the full-screen view to load
        
        # Wait a bit more for the content to fully load
        print("⏳ Waiting for full-screen artifact to load completely...")
        time.sleep(10)
        
        # Take a screenshot of the full-screen artifact
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f"charts/fullscreen_artifact_{timestamp}.png"
        
        print("📸 Taking full-screen artifact screenshot...")
        driver.save_screenshot(screenshot_path)
        
        # Get file details
        if os.path.exists(screenshot_path):
            file_size = os.path.getsize(screenshot_path)
            print(f"✅ Full-screen artifact screenshot saved: {screenshot_path}")
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
        print(f"❌ Error during publish and screenshot: {e}")
        # Take an error screenshot
        error_screenshot_path = f"screenshots/error_publish_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        try:
            driver.save_screenshot(error_screenshot_path)
            print(f"📸 Error screenshot saved: {error_screenshot_path}")
        except:
            print("❌ Could not save error screenshot")
        return None
        
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    result = publish_and_screenshot_working_url()
    
    if result:
        print(f"\n🎉 Success! Full-screen artifact screenshot: {result}")
    else:
        print("\n❌ Failed to create full-screen artifact screenshot")
