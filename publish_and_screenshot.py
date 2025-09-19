#!/usr/bin/env python3
"""
Click the Publish button to get full-screen artifact view, then screenshot it.
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

def publish_and_screenshot_artifact():
    """Click Publish button and screenshot the full-screen artifact view."""
    print("📤 Publishing artifact and taking full-screen screenshot...")
    
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
        # Navigate to the chat URL
        target_url = "https://flipsidecrypto.xyz/chat/a0604692-3937-4e21-aaec-ef911ecfd1c6"
        print(f"🌐 Navigating to: {target_url}")
        driver.get(target_url)
        
        # Wait for page to load completely
        print("⏳ Waiting for page to load completely...")
        time.sleep(10)
        
        # Wait for the Publish button to be visible
        print("🔍 Looking for Publish button...")
        wait = WebDriverWait(driver, 20)
        
        # Find the Publish button
        publish_selectors = [
            '//span[text()="Publish"]',  # XPath for exact text match
            '//span[contains(text(), "Publish")]',  # XPath for partial text match
            'span.text-xs',  # CSS selector for the class
            'button:has(span.text-xs)',  # CSS selector for button containing span
            '//button[.//span[text()="Publish"]]',  # XPath for button containing Publish span
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
                    if element.is_displayed() and "Publish" in element.text:
                        publish_button = element
                        print(f"✅ Found Publish button with selector: {selector}")
                        break
                
                if publish_button:
                    break
            except Exception as e:
                print(f"❌ Selector {selector} failed: {e}")
                continue
        
        if not publish_button:
            print("❌ Publish button not found")
            # Take a screenshot to see what's available
            debug_screenshot = f"screenshots/publish_button_not_found_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(debug_screenshot)
            print(f"📸 Debug screenshot saved: {debug_screenshot}")
            return None
        
        # Click the Publish button
        print("📤 Clicking Publish button...")
        driver.execute_script("arguments[0].click();", publish_button)
        time.sleep(3)  # Wait for publish action to start
        
        # Wait for the Publish button to change to View
        print("⏳ Waiting for Publish to change to View...")
        view_selectors = [
            '//span[text()="View"]',  # XPath for exact text match
            '//span[contains(text(), "View")]',  # XPath for partial text match
            '//button[.//span[text()="View"]]',  # XPath for button containing View span
        ]
        
        view_button = None
        max_wait_time = 30  # Wait up to 30 seconds for the change
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            for selector in view_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and "View" in element.text:
                            view_button = element
                            print(f"✅ Found View button with selector: {selector}")
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
        driver.save_screenshot(error_screenshot_path)
        print(f"📸 Error screenshot saved: {error_screenshot_path}")
        return None
        
    finally:
        driver.quit()

def test_multiple_publish_approaches():
    """Test different approaches to find and click the Publish button."""
    print("🧪 Testing multiple approaches to find Publish button...")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1600,1200")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Navigate to the chat URL
        target_url = "https://flipsidecrypto.xyz/chat/a0604692-3937-4e21-aaec-ef911ecfd1c6"
        print(f"🌐 Navigating to: {target_url}")
        driver.get(target_url)
        time.sleep(10)
        
        # Try different approaches to find the Publish button
        approaches = [
            {"name": "XPath Text", "selector": '//span[text()="Publish"]'},
            {"name": "XPath Contains", "selector": '//span[contains(text(), "Publish")]'},
            {"name": "CSS Class", "selector": 'span.text-xs'},
            {"name": "Button with Span", "selector": '//button[.//span[text()="Publish"]]'},
            {"name": "All Buttons", "selector": 'button'},
            {"name": "All Spans", "selector": 'span'},
        ]
        
        for approach in approaches:
            print(f"\n🔍 Testing {approach['name']} approach...")
            try:
                if approach['selector'].startswith('//'):
                    elements = driver.find_elements(By.XPATH, approach['selector'])
                else:
                    elements = driver.find_elements(By.CSS_SELECTOR, approach['selector'])
                
                print(f"   Found {len(elements)} elements")
                
                for i, element in enumerate(elements):
                    try:
                        text = element.text.strip()
                        if "Publish" in text:
                            print(f"   ✅ Element {i}: '{text}' - Contains 'Publish'")
                            if element.is_displayed():
                                print(f"      📍 Element is visible and clickable")
                            else:
                                print(f"      ❌ Element is not visible")
                        elif text:
                            print(f"   📝 Element {i}: '{text}'")
                    except:
                        print(f"   ❌ Element {i}: Could not get text")
                        
            except Exception as e:
                print(f"   ❌ {approach['name']} failed: {e}")
        
        # Take a screenshot to see the current state
        debug_screenshot = f"screenshots/publish_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(debug_screenshot)
        print(f"\n📸 Debug screenshot saved: {debug_screenshot}")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    # First, debug to see what elements are available
    print("=== Debug: Finding Publish Button ===")
    test_multiple_publish_approaches()
    
    print("\n=== Publish and Screenshot ===")
    result = publish_and_screenshot_artifact()
    
    if result:
        print(f"\n🎉 Success! Full-screen artifact screenshot: {result}")
    else:
        print("\n❌ Failed to create full-screen artifact screenshot")
