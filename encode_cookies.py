#!/usr/bin/env python3
"""
Cookie Encoding Script for Flipside Chat Automation

This script helps you get your Flipside Crypto session cookies and encode them
for use in the automation system.
"""

import json
import base64
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def setup_chrome_driver():
    """Set up Chrome WebDriver for cookie extraction."""
    try:
        chrome_options = Options()
        # Don't run headless so you can login manually
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Set up ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome WebDriver setup complete")
        return driver
        
    except Exception as e:
        print(f"❌ Failed to setup Chrome WebDriver: {e}")
        return None


def get_flipside_cookies():
    """Get cookies from Flipside Crypto after manual login."""
    print("🍪 Flipside Crypto Cookie Extractor")
    print("=" * 50)
    
    # Setup Chrome driver
    driver = setup_chrome_driver()
    if not driver:
        return None
    
    try:
        print("\n🌐 Opening Flipside Crypto...")
        driver.get("https://flipsidecrypto.xyz")
        
        print("\n📝 Please login to Flipside Crypto in the browser window that opened.")
        print("   - Enter your credentials")
        print("   - Complete any 2FA if required")
        print("   - Navigate to the chat page if needed")
        print("\n⏳ Press Enter when you're fully logged in and ready...")
        
        # Wait for user to login
        input()
        
        print("\n🔍 Extracting cookies...")
        
        # Get all cookies
        cookies = driver.get_cookies()
        
        if not cookies:
            print("❌ No cookies found. Make sure you're logged in.")
            return None
        
        print(f"✅ Found {len(cookies)} cookies")
        
        # Encode cookies for GitHub secrets
        cookies_json = json.dumps(cookies, indent=2)
        encoded = base64.b64encode(cookies_json.encode('utf-8')).decode('utf-8')
        
        print("\n" + "=" * 50)
        print("🎉 COOKIES EXTRACTED SUCCESSFULLY!")
        print("=" * 50)
        
        print(f"\n📋 Copy this value to your .env file:")
        print(f"FLIPSIDE_COOKIES={encoded}")
        
        print(f"\n📁 Or copy this to your GitHub repository secrets:")
        print(f"Secret Name: FLIPSIDE_COOKIES")
        print(f"Secret Value: {encoded}")
        
        # Save to file for convenience
        with open('flipside_cookies.txt', 'w') as f:
            f.write(f"FLIPSIDE_COOKIES={encoded}\n")
        
        print(f"\n💾 Cookies also saved to: flipside_cookies.txt")
        
        return encoded
        
    except KeyboardInterrupt:
        print("\n⚠️ Cookie extraction cancelled by user")
        return None
    except Exception as e:
        print(f"\n❌ Error extracting cookies: {e}")
        return None
    finally:
        if driver:
            driver.quit()
            print("\n🔒 Browser closed")


def validate_cookies(encoded_cookies):
    """Validate that the encoded cookies can be decoded properly."""
    try:
        # Decode cookies
        decoded = base64.b64decode(encoded_cookies.encode('utf-8')).decode('utf-8')
        cookies = json.loads(decoded)
        
        print(f"\n✅ Cookie validation successful:")
        print(f"   - {len(cookies)} cookies decoded")
        print(f"   - Cookie names: {[c.get('name', 'unknown') for c in cookies[:5]]}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Cookie validation failed: {e}")
        return False


def main():
    """Main function."""
    print("🚀 Starting Flipside Crypto Cookie Extraction")
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️ Warning: Virtual environment may not be activated")
        print("   Consider running: source venv/bin/activate")
        print()
    
    # Extract cookies
    encoded_cookies = get_flipside_cookies()
    
    if encoded_cookies:
        # Validate the cookies
        if validate_cookies(encoded_cookies):
            print("\n🎯 Next steps:")
            print("1. Copy the FLIPSIDE_COOKIES value above")
            print("2. Paste it into your .env file")
            print("3. Or add it as a GitHub secret for automated runs")
            print("4. Test the automation: python src/chat_automation.py")
        else:
            print("\n❌ Cookie validation failed. Please try again.")
    else:
        print("\n❌ Cookie extraction failed. Please try again.")


if __name__ == "__main__":
    main()
