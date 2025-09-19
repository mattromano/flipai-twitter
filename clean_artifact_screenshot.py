#!/usr/bin/env python3
"""
Create the cleanest possible artifact screenshot by targeting the specific content
and using optimal browser settings for high-quality capture.
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

def create_clean_artifact_screenshot():
    """Create the cleanest possible artifact screenshot."""
    print("🎨 Creating clean, high-quality artifact screenshot...")
    
    # Setup Chrome options for high-quality screenshots
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1600,1200")  # Large window for high quality
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Set high DPI for better quality
    chrome_options.add_argument("--force-device-scale-factor=2")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Navigate to the chat URL
        target_url = "https://flipsidecrypto.xyz/chat/shared/chats/b2753e8c-ab2a-40cb-82c3-e285450b7fec"
        print(f"🌐 Navigating to: {target_url}")
        driver.get(target_url)
        
        # Wait for page to load completely
        print("⏳ Waiting for page to load completely...")
        time.sleep(10)
        
        # Wait for the main content to be visible
        wait = WebDriverWait(driver, 20)
        
        # Try to find the main content area
        content_selectors = [
            'main',
            '[role="main"]',
            '.main-content',
            '.content',
            '.report',
            '.analysis',
            '.artifact',
        ]
        
        main_content = None
        for selector in content_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.size['width'] > 300 and element.size['height'] > 300:
                        main_content = element
                        print(f"✅ Found main content with selector: {selector}")
                        break
                if main_content:
                    break
            except:
                continue
        
        if not main_content:
            print("⚠️  Main content not found, using full page")
            main_content = driver.find_element(By.TAG_NAME, "body")
        
        # Scroll to top to ensure we capture everything
        print("📜 Scrolling to top...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # Wait a bit more for any animations to complete
        time.sleep(3)
        
        # Take screenshot of the main content
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f"charts/clean_artifact_{timestamp}.png"
        
        print("📸 Taking high-quality screenshot...")
        main_content.screenshot(screenshot_path)
        
        # Also take a full page screenshot as backup
        full_page_path = f"charts/full_page_backup_{timestamp}.png"
        driver.save_screenshot(full_page_path)
        
        # Get file details
        if os.path.exists(screenshot_path):
            file_size = os.path.getsize(screenshot_path)
            print(f"✅ Clean artifact screenshot saved: {screenshot_path}")
            print(f"📁 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            if file_size < 5 * 1024 * 1024:  # Under 5MB
                print("✅ Twitter-friendly file size")
            else:
                print("⚠️  Large file size for Twitter")
        
        if os.path.exists(full_page_path):
            full_size = os.path.getsize(full_page_path)
            print(f"✅ Full page backup saved: {full_page_path}")
            print(f"📁 Backup size: {full_size:,} bytes ({full_size/1024:.1f} KB)")
        
        return screenshot_path
        
    except Exception as e:
        print(f"❌ Error during screenshot: {e}")
        # Take an error screenshot
        error_screenshot_path = f"screenshots/error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(error_screenshot_path)
        print(f"📸 Error screenshot saved: {error_screenshot_path}")
        return None
        
    finally:
        driver.quit()

def create_twitter_optimized_screenshot():
    """Create a Twitter-optimized screenshot with perfect dimensions."""
    print("🐦 Creating Twitter-optimized artifact screenshot...")
    
    # Twitter-optimized dimensions
    twitter_dimensions = [
        {"width": 1200, "height": 800, "name": "twitter_standard"},
        {"width": 1200, "height": 1000, "name": "twitter_tall"},
        {"width": 1400, "height": 800, "name": "twitter_wide"},
    ]
    
    results = []
    
    for dims in twitter_dimensions:
        print(f"\n🖼️  Creating {dims['name']} ({dims['width']}x{dims['height']})...")
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--window-size={dims['width']},{dims['height']}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        try:
            # Navigate to the chat URL
            target_url = "https://flipsidecrypto.xyz/chat/shared/chats/b2753e8c-ab2a-40cb-82c3-e285450b7fec"
            driver.get(target_url)
            time.sleep(8)
            
            # Wait for content to load
            time.sleep(10)
            
            # Scroll to top
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # Take screenshot
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = f"charts/{dims['name']}_{timestamp}.png"
            driver.save_screenshot(screenshot_path)
            
            if os.path.exists(screenshot_path):
                file_size = os.path.getsize(screenshot_path)
                results.append({
                    'name': dims['name'],
                    'path': screenshot_path,
                    'size': file_size,
                    'size_kb': file_size / 1024
                })
                print(f"✅ {dims['name']}: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            else:
                print(f"❌ {dims['name']} failed")
                
        except Exception as e:
            print(f"❌ {dims['name']} failed: {e}")
        finally:
            driver.quit()
    
    print(f"\n🎉 Twitter-optimized screenshots completed!")
    print(f"✅ Successfully created {len(results)} screenshots")
    
    if results:
        print("\n📊 Twitter Screenshot Summary:")
        for result in results:
            print(f"   • {result['name']}: {result['size_kb']:.1f} KB")
        
        # Find the best for Twitter
        best_twitter = max(results, key=lambda x: x['size'])
        print(f"\n🏆 Best for Twitter: {best_twitter['name']} ({best_twitter['size_kb']:.1f} KB)")
    
    return results

if __name__ == "__main__":
    # Create clean screenshot
    print("=== Clean Artifact Screenshot ===")
    clean_result = create_clean_artifact_screenshot()
    
    # Create Twitter-optimized screenshots
    print("\n=== Twitter-Optimized Screenshots ===")
    twitter_results = create_twitter_optimized_screenshot()
    
    print("\n🎉 All screenshot tests completed!")
    print("📋 Check the charts/ directory for the generated images")
