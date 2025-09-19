#!/usr/bin/env python3
"""
Click the Preview button to get full-screen artifact view, then screenshot it.
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

def preview_and_screenshot_artifact():
    """Click Preview button and screenshot the full-screen artifact view."""
    print("👁️ Clicking Preview button and taking full-screen screenshot...")
    
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
        debug_screenshot = f"screenshots/before_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(debug_screenshot)
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
                    elements = driver.find_elements(By.XPATH, selector)
                else:
                    # CSS selector
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
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
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            for i, button in enumerate(all_buttons):
                try:
                    text = button.text.strip()
                    if text:
                        print(f"   Button {i}: '{text}'")
                except:
                    pass
            return None
        
        # Click the Preview button
        print("👁️ Clicking Preview button...")
        driver.execute_script("arguments[0].click();", preview_button)
        time.sleep(5)  # Wait for preview to load
        
        # Take a screenshot after clicking preview
        after_preview_screenshot = f"screenshots/after_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(after_preview_screenshot)
        print(f"📸 After preview screenshot saved: {after_preview_screenshot}")
        
        # Wait a bit more for the content to fully load
        print("⏳ Waiting for preview to load completely...")
        time.sleep(10)
        
        # Take a screenshot of the preview
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f"charts/preview_artifact_{timestamp}.png"
        
        print("📸 Taking preview artifact screenshot...")
        driver.save_screenshot(screenshot_path)
        
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
        error_screenshot_path = f"screenshots/error_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
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

def try_direct_screenshot():
    """Try taking a direct screenshot of the current artifact view."""
    print("📸 Taking direct screenshot of current artifact view...")
    
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
        
        # Scroll to top to ensure we capture everything
        print("📜 Scrolling to top...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # Take a direct screenshot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f"charts/direct_artifact_{timestamp}.png"
        
        print("📸 Taking direct artifact screenshot...")
        driver.save_screenshot(screenshot_path)
        
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
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    # Try preview approach first
    print("=== Preview and Screenshot ===")
    preview_result = preview_and_screenshot_artifact()
    
    if not preview_result:
        print("\n=== Direct Screenshot Fallback ===")
        direct_result = try_direct_screenshot()
        
        if direct_result:
            print(f"\n🎉 Success! Direct artifact screenshot: {direct_result}")
        else:
            print("\n❌ Both approaches failed")
    else:
        print(f"\n🎉 Success! Preview artifact screenshot: {preview_result}")
