#!/usr/bin/env python3
"""
Simple script to screenshot the artifact directly from the page for a clean Twitter image.
"""

import os
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def simple_artifact_screenshot():
    """Take a clean screenshot of the artifact."""
    print("📸 Taking clean artifact screenshot...")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1400,1000")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Navigate to the chat URL
        target_url = "https://flipsidecrypto.xyz/chat/shared/chats/b2753e8c-ab2a-40cb-82c3-e285450b7fec"
        print(f"🌐 Navigating to: {target_url}")
        driver.get(target_url)
        time.sleep(8)  # Wait for page to load
        
        # Wait for the artifact to be visible
        print("⏳ Waiting for artifact to load...")
        time.sleep(10)
        
        # Try to find the artifact/report section
        artifact_selectors = [
            '[data-testid="artifact"]',
            '.artifact',
            '.report-content',
            '.chart-container',
            'div[class*="artifact"]',
            'div[class*="report"]',
            'div[class*="analysis"]',
            'main',
            'article',
        ]
        
        artifact_element = None
        for selector in artifact_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.size['width'] > 200 and element.size['height'] > 200:
                        artifact_element = element
                        print(f"✅ Found artifact with selector: {selector}")
                        break
                if artifact_element:
                    break
            except Exception as e:
                print(f"❌ Selector {selector} failed: {e}")
                continue
        
        if artifact_element:
            # Take a screenshot of just the artifact element
            print("📸 Taking screenshot of artifact element...")
            screenshot_path = f"charts/artifact_element_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            artifact_element.screenshot(screenshot_path)
            print(f"✅ Artifact element screenshot saved: {screenshot_path}")
        else:
            # Take a full page screenshot
            print("📸 Taking full page screenshot...")
            screenshot_path = f"charts/full_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_path)
            print(f"✅ Full page screenshot saved: {screenshot_path}")
        
        # Also try to scroll to make sure we capture everything
        print("📜 Scrolling to capture all content...")
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # Take another screenshot after scrolling
        scroll_screenshot_path = f"charts/artifact_scrolled_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(scroll_screenshot_path)
        print(f"✅ Scrolled screenshot saved: {scroll_screenshot_path}")
        
        # Get file sizes
        for path in [screenshot_path, scroll_screenshot_path]:
            if os.path.exists(path):
                file_size = os.path.getsize(path)
                print(f"📁 {os.path.basename(path)}: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
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

def test_multiple_approaches():
    """Test different approaches to get the best screenshot."""
    print("🧪 Testing multiple screenshot approaches...")
    
    approaches = [
        {"name": "Standard", "window_size": "1400,1000"},
        {"name": "Large", "window_size": "1600,1200"},
        {"name": "Wide", "window_size": "1800,1000"},
        {"name": "Tall", "window_size": "1200,1400"},
    ]
    
    results = []
    
    for approach in approaches:
        print(f"\n🖼️  Testing {approach['name']} approach ({approach['window_size']})...")
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"--window-size={approach['window_size']}")
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
            
            # Take screenshot
            screenshot_path = f"charts/artifact_{approach['name'].lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_path)
            
            if os.path.exists(screenshot_path):
                file_size = os.path.getsize(screenshot_path)
                results.append({
                    'name': approach['name'],
                    'path': screenshot_path,
                    'size': file_size,
                    'size_kb': file_size / 1024
                })
                print(f"✅ {approach['name']} screenshot: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            else:
                print(f"❌ {approach['name']} screenshot failed")
                
        except Exception as e:
            print(f"❌ {approach['name']} approach failed: {e}")
        finally:
            driver.quit()
    
    print(f"\n🎉 Screenshot testing completed!")
    print(f"✅ Successfully created {len(results)} screenshots")
    
    if results:
        print("\n📊 Screenshot Summary:")
        for result in results:
            print(f"   • {result['name']}: {result['size_kb']:.1f} KB")
        
        # Find the best screenshot
        best = max(results, key=lambda x: x['size'])
        print(f"\n🏆 Largest screenshot: {best['name']} ({best['size_kb']:.1f} KB)")
    
    return results

if __name__ == "__main__":
    # Test simple approach first
    print("=== Simple Artifact Screenshot ===")
    simple_artifact_screenshot()
    
    print("\n=== Multiple Approaches Test ===")
    test_multiple_approaches()
