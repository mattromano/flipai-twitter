#!/usr/bin/env python3
"""
One-time script to generate fresh cookies for Flipside Crypto.
This script opens a browser window for manual login and saves the cookies.
"""

import os
import sys
import time
import base64
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def generate_fresh_cookies():
    """Generate fresh cookies by opening a browser for manual login."""
    print("🍪 Flipside Cookie Generator")
    print("=" * 40)
    print("This script will open a browser window for you to log in manually.")
    print("After successful login, it will save the cookies for automation use.")
    print()
    
    # Set up Chrome options (non-headless for manual login)
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    # Note: Not running headless so user can log in manually
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🌐 Opening Flipside login page...")
        driver.get("https://flipsidecrypto.xyz/chat/")
        
        print("\n📋 Instructions:")
        print("1. Log in to your Flipside account in the browser window")
        print("2. Make sure you can see the chat interface")
        print("3. Come back here and press Enter when you're logged in")
        print()
        
        # Wait for user to log in manually
        input("Press Enter after you've successfully logged in...")
        
        # Verify login
        print("\n🔍 Verifying login...")
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        # Check if we're on the chat page
        if 'chat' in current_url.lower() and 'login' not in current_url.lower():
            print("✅ Login appears successful!")
            
            # Get all cookies
            cookies = driver.get_cookies()
            print(f"📊 Retrieved {len(cookies)} cookies")
            
            # Save cookies to file
            cookie_file = "flipside_cookies.txt"
            with open(cookie_file, 'w') as f:
                for cookie in cookies:
                    f.write(f"{cookie['name']}={cookie['value']}; ")
            
            print(f"💾 Cookies saved to: {cookie_file}")
            
            # Also save as base64 for GitHub Actions
            cookie_data = json.dumps(cookies)
            encoded_cookies = base64.b64encode(cookie_data.encode()).decode()
            
            print(f"\n🔐 Base64 encoded cookies (for GitHub Actions):")
            print(f"Copy this to your FLIPSIDE_COOKIES secret:")
            print("-" * 60)
            print(encoded_cookies)
            print("-" * 60)
            
            print(f"\n✅ Cookie generation completed successfully!")
            print(f"📁 Cookies saved to: {cookie_file}")
            print(f"🔑 Base64 encoded cookies ready for GitHub Actions")
            
            return True
            
        else:
            print("❌ Login verification failed")
            print("Make sure you're logged in and on the chat page")
            return False
            
    except Exception as e:
        print(f"❌ Error generating cookies: {e}")
        return False
    
    finally:
        print("\n🧹 Closing browser...")
        input("Press Enter to close the browser...")
        driver.quit()

if __name__ == "__main__":
    success = generate_fresh_cookies()
    if success:
        print("\n🎉 Cookie generation completed! You can now run the automation.")
    else:
        print("\n❌ Cookie generation failed. Please try again.")
        sys.exit(1)
