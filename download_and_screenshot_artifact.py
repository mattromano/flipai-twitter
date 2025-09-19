#!/usr/bin/env python3
"""
Download the artifact using the download button and screenshot the entire window
to get a clean, professional image for Twitter posting.
"""

import os
import sys
import time
import tempfile
import webbrowser
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
from src.automation_logger import AutomationLogger

def download_and_screenshot_artifact():
    """Download the artifact and screenshot it for a clean Twitter image."""
    print("📥 Downloading artifact and creating clean screenshot...")
    
    automation_logger = AutomationLogger(debug_mode=True)
    automation = RobustFlipsideChatAutomation()
    
    try:
        # Setup WebDriver
        automation.setup_chrome_driver()
        automation.setup_session_with_timeout(60)
        
        # Navigate to the chat URL
        target_url = "https://flipsidecrypto.xyz/chat/shared/chats/b2753e8c-ab2a-40cb-82c3-e285450b7fec"
        automation_logger.log_info(f"Navigating to: {target_url}")
        automation.driver.get(target_url)
        time.sleep(5)  # Wait for page to load
        
        # Wait for the artifact to be visible
        automation_logger.log_info("Waiting for artifact to load...")
        time.sleep(10)
        
        # Find and click the download button
        download_selectors = [
            'button[data-slot="tooltip-trigger"]',  # The specific button you provided
            'button[class*="lucide-download"]',
            'button svg[class*="lucide-download"]',
            'button:has(svg[class*="lucide-download"])',
            '//button[.//svg[contains(@class, "lucide-download")]]',  # XPath version
        ]
        
        download_button = None
        for selector in download_selectors:
            try:
                if selector.startswith('//'):
                    # XPath selector
                    download_button = automation.driver.find_element(By.XPATH, selector)
                else:
                    # CSS selector
                    download_button = automation.driver.find_element(By.CSS_SELECTOR, selector)
                
                if download_button and download_button.is_displayed():
                    automation_logger.log_info(f"Found download button with selector: {selector}")
                    break
            except Exception as e:
                automation_logger.log_warning(f"Download button not found with selector {selector}: {e}")
                continue
        
        if not download_button:
            automation_logger.log_error("Download button not found with any selector")
            # Take a screenshot to see what's available
            screenshot_path = f"screenshots/download_button_not_found_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            automation.driver.save_screenshot(screenshot_path)
            automation_logger.log_info(f"Screenshot saved: {screenshot_path}")
            return None
        
        # Click the download button
        automation_logger.log_info("Clicking download button...")
        automation.driver.execute_script("arguments[0].click();", download_button)
        time.sleep(3)  # Wait for download to start
        
        # Wait for download to complete and get the downloaded file
        automation_logger.log_info("Waiting for download to complete...")
        time.sleep(5)
        
        # Get the downloaded HTML content
        # The download should have triggered a file download, but we need to get the HTML content
        # Let's try to get the artifact HTML directly from the page
        automation_logger.log_info("Extracting artifact HTML content...")
        
        # Look for the artifact content in the page
        artifact_selectors = [
            '[data-testid="artifact"]',
            '.artifact',
            '.report-content',
            '.chart-container',
            'div[class*="artifact"]',
            'div[class*="report"]',
        ]
        
        artifact_element = None
        for selector in artifact_selectors:
            try:
                artifact_element = automation.driver.find_element(By.CSS_SELECTOR, selector)
                if artifact_element:
                    automation_logger.log_info(f"Found artifact with selector: {selector}")
                    break
            except:
                continue
        
        if not artifact_element:
            automation_logger.log_warning("Artifact element not found, taking full page screenshot")
            # Take a full page screenshot of the current view
            screenshot_path = f"charts/artifact_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            automation.driver.save_screenshot(screenshot_path)
            automation_logger.log_info(f"Full page screenshot saved: {screenshot_path}")
            return screenshot_path
        
        # Create a new browser window to display the artifact cleanly
        automation_logger.log_info("Creating clean artifact view...")
        
        # Get the HTML content of the artifact
        artifact_html = artifact_element.get_attribute('outerHTML')
        
        # Create a temporary HTML file with the artifact
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
            # Create a clean HTML document with the artifact
            clean_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>DeFi Lending Analysis</title>
                <style>
                    body {{
                        margin: 0;
                        padding: 20px;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background-color: white;
                        line-height: 1.6;
                    }}
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                    }}
                    h1, h2, h3 {{
                        color: #333;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin: 20px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 12px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f5f5f5;
                        font-weight: bold;
                    }}
                    .chart {{
                        margin: 20px 0;
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        padding: 20px;
                        background-color: #fafafa;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    {artifact_html}
                </div>
            </body>
            </html>
            """
            temp_file.write(clean_html)
            temp_file_path = temp_file.name
        
        # Open the temporary HTML file in a new browser window
        automation_logger.log_info(f"Opening clean artifact view: {temp_file_path}")
        
        # Create a new WebDriver instance for the clean view
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1400,1000")
        
        clean_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        try:
            # Load the clean HTML file
            clean_driver.get(f"file://{temp_file_path}")
            time.sleep(3)  # Wait for content to load
            
            # Take a screenshot of the clean view
            screenshot_path = f"charts/clean_artifact_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            clean_driver.save_screenshot(screenshot_path)
            automation_logger.log_info(f"Clean artifact screenshot saved: {screenshot_path}")
            
            # Get file size
            if os.path.exists(screenshot_path):
                file_size = os.path.getsize(screenshot_path)
                automation_logger.log_info(f"Screenshot file size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            return screenshot_path
            
        finally:
            clean_driver.quit()
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
    except Exception as e:
        automation_logger.log_error(f"Error during artifact download and screenshot: {e}")
        # Take a screenshot for debugging
        screenshot_path = f"screenshots/error_artifact_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        automation.driver.save_screenshot(screenshot_path)
        automation_logger.log_info(f"Error screenshot saved: {screenshot_path}")
        return None
        
    finally:
        if automation.driver:
            automation.driver.quit()

def test_artifact_screenshot():
    """Test the artifact screenshot functionality."""
    print("🧪 Testing artifact download and screenshot...")
    
    result = download_and_screenshot_artifact()
    
    if result:
        print(f"✅ Successfully created artifact screenshot: {result}")
        
        # Check if file exists and get details
        if os.path.exists(result):
            file_size = os.path.getsize(result)
            print(f"📁 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            if file_size < 5 * 1024 * 1024:  # Under 5MB
                print("✅ Twitter-friendly file size")
            else:
                print("⚠️  Large file size for Twitter")
        else:
            print("❌ Screenshot file was not created")
    else:
        print("❌ Failed to create artifact screenshot")
    
    return result

if __name__ == "__main__":
    test_artifact_screenshot()
