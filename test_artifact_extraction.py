#!/usr/bin/env python3
"""
Test script to extract artifact from a chat URL.
Loads the URL, finds the copy link button, navigates to artifact, and screenshots it.
"""

import os
import sys
import time
from datetime import datetime

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

try:
    import pyperclip
except ImportError:
    pyperclip = None
    print("⚠️ pyperclip not available. Install with: pip install pyperclip")

from modules.shared.authentication import StealthAuthenticator
from modules.shared.logger import AutomationLogger


def find_copy_link_button(driver, logger):
    """Find the copy link button (lucide-link icon) in the upper right corner."""
    try:
        logger.log_info("🔍 Looking for Copy link button (lucide-link icon)")
        
        # Method 1: Find any button with lucide-link SVG
        all_buttons = driver.find_elements(By.TAG_NAME, 'button')
        logger.log_debug(f"Found {len(all_buttons)} total buttons on page")
        
        for i, button in enumerate(all_buttons):
            if not button.is_displayed():
                continue
            
            try:
                # CRITICAL: Exclude any button with share2 SVG or "Share" text
                button_text = button.text.strip().lower()
                share2_svgs = button.find_elements(By.CSS_SELECTOR, 'svg.lucide-share2')
                if share2_svgs or 'share' in button_text:
                    continue  # Skip share buttons
                
                # Check for lucide-link SVG
                svgs = button.find_elements(By.CSS_SELECTOR, 'svg.lucide-link')
                if svgs:
                    # Check if it's in the upper right area
                    location = button.location
                    size = driver.get_window_size()
                    if location['x'] > size['width'] * 0.5:  # Right half of screen
                        logger.log_success(f"✅ Found Copy link button with lucide-link icon - Element {i} at x={location['x']}")
                        return button
                
                # Fallback: Check for SVG with link structure
                all_svgs = button.find_elements(By.CSS_SELECTOR, 'svg')
                for svg in all_svgs:
                    svg_html = svg.get_attribute('outerHTML') or ''
                    # Skip if it has share2 icon
                    if 'lucide-share2' in svg_html:
                        continue
                    # Check for link icon characteristics
                    if ('lucide-link' in svg_html or 
                        (svg_html.count('<path') >= 2 and 'M10 13' in svg_html)):
                        location = button.location
                        size = driver.get_window_size()
                        if location['x'] > size['width'] * 0.5:
                            logger.log_success(f"✅ Found Copy link button via SVG structure - Element {i}")
                            return button
                        
            except Exception as e:
                logger.log_debug(f"Error checking button {i}: {e}")
                continue
        
        logger.log_warning("⚠️ Copy link button not found")
        return None
        
    except Exception as e:
        logger.log_error(f"Error finding Copy link button: {e}")
        return None


def extract_url_from_clipboard(logger):
    """Extract the artifact URL from the clipboard."""
    try:
        logger.log_info("📋 Reading artifact URL from clipboard")
        
        if not pyperclip:
            logger.log_warning("⚠️ pyperclip not available, cannot read from clipboard")
            return ""
        
        # Read from clipboard
        clipboard_content = pyperclip.paste()
        
        if not clipboard_content:
            logger.log_warning("⚠️ Clipboard is empty")
            return ""
        
        # Check if clipboard contains a URL
        if 'flipsidecrypto.xyz' in clipboard_content or 'http' in clipboard_content:
            import re
            url_pattern = r'https?://[^\s]+flipsidecrypto\.xyz[^\s]*'
            url_matches = re.findall(url_pattern, clipboard_content)
            
            if url_matches:
                artifact_url = url_matches[0]
                artifact_url = artifact_url.rstrip('.,;:!?')
                logger.log_success(f"✅ Found artifact URL in clipboard: {artifact_url}")
                return artifact_url
            elif clipboard_content.strip().startswith('http'):
                logger.log_success(f"✅ Using clipboard content as URL: {clipboard_content.strip()}")
                return clipboard_content.strip()
        else:
            logger.log_warning(f"⚠️ Clipboard does not contain a URL: {clipboard_content[:50]}...")
        
        return ""
        
    except Exception as e:
        logger.log_error(f"Error reading from clipboard: {e}")
        return ""


def capture_artifact_screenshot(driver, artifact_url, logger):
    """Navigate to artifact URL and capture screenshot."""
    try:
        logger.log_info(f"🧭 Navigating to artifact URL: {artifact_url}")
        driver.get(artifact_url)
        time.sleep(5)
        
        # Wait for page to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Wait for title to appear (e.g., "Chain Health Radar")
        logger.log_info("⏳ Waiting for artifact title to load...")
        try:
            WebDriverWait(driver, 15).until(
                lambda d: "Chain Health" in d.page_source or "Health Radar" in d.page_source or len(d.find_elements(By.TAG_NAME, "h1")) > 0
            )
            logger.log_info("✅ Artifact title detected")
        except:
            logger.log_warning("⚠️ Title not found, proceeding anyway")
        
        time.sleep(3)  # Additional wait for all content to render
        
        # Scroll through entire page to ensure all content loads
        logger.log_info("📜 Scrolling through page to load all content...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_pause = 1
        max_scrolls = 10
        scroll_count = 0
        
        while scroll_count < max_scrolls:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scroll_count += 1
        
        # Scroll back to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # Get full page dimensions
        total_width = driver.execute_script("return Math.max(document.body.scrollWidth, document.documentElement.scrollWidth);")
        total_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);")
        
        logger.log_info(f"📏 Full page dimensions: {total_width}x{total_height}")
        
        # Set window to full page size with buffer
        adjusted_height = total_height + 200  # Extra buffer for header/footer
        driver.set_window_size(max(total_width, 1200), adjusted_height)
        time.sleep(2)
        
        # Scroll to top one more time to ensure we start from beginning
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Take screenshot
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path = f"screenshots/artifact_test_{timestamp}.png"
        
        logger.log_info("📸 Taking full page screenshot...")
        driver.save_screenshot(screenshot_path)
        
        logger.log_success(f"✅ Full page screenshot captured: {screenshot_path}")
        logger.log_info(f"📐 Screenshot size: {total_width}x{adjusted_height}")
        
        return screenshot_path
        
    except Exception as e:
        logger.log_error(f"Error capturing artifact screenshot: {e}")
        return ""


def main():
    """Main test function."""
    chat_url = "https://flipsidecrypto.xyz/chat/7149195a-fc1e-45dc-9db4-dcbf70f651d8"
    
    logger = AutomationLogger()
    driver = None
    
    try:
        logger.log_info("🚀 Starting artifact extraction test")
        logger.log_info(f"🔗 Chat URL: {chat_url}")
        
        # Setup driver
        logger.log_info("🤖 Setting up Chrome driver")
        authenticator = StealthAuthenticator(logger)
        if not authenticator.setup_driver():
            logger.log_error("❌ Failed to setup driver")
            return
        
        driver = authenticator.driver
        
        # Authenticate
        logger.log_info("🔐 Authenticating...")
        if not authenticator.login():
            logger.log_error("❌ Authentication failed")
            return
        
        # Navigate to chat URL
        logger.log_info(f"🧭 Navigating to chat: {chat_url}")
        driver.get(chat_url)
        time.sleep(5)
        
        # Wait for page to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)
        
        # Find and click copy link button
        copy_link_button = find_copy_link_button(driver, logger)
        if not copy_link_button:
            logger.log_error("❌ Copy link button not found")
            driver.save_screenshot("screenshots/test_error_copy_link_not_found.png")
            return
        
        logger.log_info("🔗 Clicking Copy link button")
        driver.execute_script("arguments[0].click();", copy_link_button)
        time.sleep(2)
        
        # Read URL from clipboard
        artifact_url = extract_url_from_clipboard(logger)
        if not artifact_url:
            logger.log_error("❌ Could not read URL from clipboard")
            driver.save_screenshot("screenshots/test_error_clipboard_empty.png")
            return
        
        logger.log_info(f"✅ Got artifact URL: {artifact_url}")
        
        # Navigate to artifact and screenshot
        screenshot_path = capture_artifact_screenshot(driver, artifact_url, logger)
        
        if screenshot_path:
            logger.log_success(f"✅ Test completed! Screenshot: {screenshot_path}")
        else:
            logger.log_error("❌ Failed to capture screenshot")
        
    except Exception as e:
        logger.log_error(f"Test failed: {e}")
        if driver:
            driver.save_screenshot(f"screenshots/test_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    
    finally:
        if driver:
            driver.quit()
        logger.log_info("🧹 Cleanup completed")


if __name__ == "__main__":
    main()

