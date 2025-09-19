#!/usr/bin/env python3
"""
Test script to check what elements are available on Flipside Crypto site
"""

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_flipside_elements():
    """Test what elements are available on Flipside site."""
    print("🔍 Testing Flipside Crypto site elements...")
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Load cookies if available
        cookies_encoded = os.getenv('FLIPSIDE_COOKIES')
        if cookies_encoded:
            print("🍪 Loading cookies...")
            import base64
            import json
            
            cookies = json.loads(base64.b64decode(cookies_encoded).decode('utf-8'))
            driver.get("https://flipsidecrypto.xyz")
            
            for cookie in cookies:
                try:
                    cookie_copy = cookie.copy()
                    if 'expiry' in cookie_copy:
                        del cookie_copy['expiry']
                    driver.add_cookie(cookie_copy)
                except Exception as e:
                    print(f"Warning: Could not add cookie {cookie.get('name', 'unknown')}: {e}")
        
        # Navigate to chat page
        print("🌐 Navigating to chat page...")
        driver.get("https://flipsidecrypto.xyz/chat/")
        
        # Wait a bit for page to load
        import time
        time.sleep(5)
        
        print("📋 Current URL:", driver.current_url)
        print("📋 Page title:", driver.title)
        
        # Look for common input elements
        input_selectors = [
            "input[type='text']",
            "input[type='search']", 
            "textarea",
            "input[placeholder*='message']",
            "input[placeholder*='ask']",
            "input[placeholder*='question']",
            "[data-testid*='input']",
            "[data-testid*='chat']",
            ".chat-input",
            ".message-input",
            "#chat-input",
            "#message-input"
        ]
        
        print("\n🔍 Looking for input elements...")
        for selector in input_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        try:
                            placeholder = elem.get_attribute('placeholder') or 'no placeholder'
                            print(f"   Element {i+1}: placeholder='{placeholder}', tag={elem.tag_name}")
                        except:
                            print(f"   Element {i+1}: tag={elem.tag_name}")
                else:
                    print(f"❌ No elements found with selector: {selector}")
            except Exception as e:
                print(f"⚠️ Error with selector {selector}: {e}")
        
        # Look for buttons
        button_selectors = [
            "button",
            "input[type='submit']",
            "input[type='button']",
            "[role='button']",
            "button[type='submit']",
            "[data-testid*='submit']",
            "[data-testid*='send']",
            ".submit-button",
            ".send-button"
        ]
        
        print("\n🔍 Looking for button elements...")
        for selector in button_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    for i, elem in enumerate(elements[:3]):  # Show first 3
                        try:
                            text = elem.text or elem.get_attribute('value') or 'no text'
                            print(f"   Element {i+1}: text='{text}', tag={elem.tag_name}")
                        except:
                            print(f"   Element {i+1}: tag={elem.tag_name}")
            except Exception as e:
                print(f"⚠️ Error with selector {selector}: {e}")
        
        # Look for any form elements
        print("\n🔍 Looking for form elements...")
        try:
            forms = driver.find_elements(By.TAG_NAME, "form")
            print(f"Found {len(forms)} form elements")
            for i, form in enumerate(forms):
                try:
                    action = form.get_attribute('action') or 'no action'
                    method = form.get_attribute('method') or 'no method'
                    print(f"   Form {i+1}: action='{action}', method='{method}'")
                except:
                    print(f"   Form {i+1}: found")
        except Exception as e:
            print(f"⚠️ Error looking for forms: {e}")
        
        # Get page source snippet
        print("\n📄 Page source snippet (first 1000 chars):")
        page_source = driver.page_source[:1000]
        print(page_source)
        
        # Take a screenshot
        print("\n📸 Taking screenshot...")
        driver.save_screenshot("flipside_test.png")
        print("Screenshot saved as flipside_test.png")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()
        print("🔒 Browser closed")

if __name__ == "__main__":
    test_flipside_elements()
