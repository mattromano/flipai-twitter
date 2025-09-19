#!/usr/bin/env python3
"""
Debug script to identify where the automation is getting stuck.
"""

import os
import sys
import time
from src.chat_automation import FlipsideChatAutomation
from src.automation_logger import setup_automation_logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def debug_automation():
    """Debug the automation step by step."""
    print("🔍 Debugging Flipside Chat Automation")
    print("=" * 50)
    
    # Setup enhanced logging
    logger = setup_automation_logging(debug_mode=True)
    
    automation = FlipsideChatAutomation()
    
    try:
        # Step 1: Setup WebDriver
        logger.log_info("Setting up WebDriver...")
        if not automation.setup_chrome_driver():
            logger.log_error("Failed to setup WebDriver")
            return
        logger.log_success("WebDriver setup complete")
        
        # Step 2: Setup Session
        logger.log_info("Setting up session...")
        if not automation.setup_session():
            logger.log_error("Failed to setup session")
            return
        logger.log_success("Session setup complete")
        
        # Step 3: Navigate to main site first
        logger.log_info("Navigating to main Flipside site...")
        automation.driver.get("https://flipsidecrypto.xyz")
        time.sleep(3)
        
        # Take screenshot of main page
        automation.driver.save_screenshot("debug_main_page.png")
        logger.log_success("Main page screenshot saved: debug_main_page.png")
        
        # Step 4: Check if we're logged in
        logger.log_info("Checking authentication status...")
        try:
            # Look for user menu or profile indicators
            user_indicators = [
                "[data-testid='user-menu']",
                ".user-avatar",
                ".profile-menu",
                ".authenticated",
                "button[data-testid='login']",
                "a[href*='login']"
            ]
            
            for indicator in user_indicators:
                try:
                    element = automation.driver.find_element(By.CSS_SELECTOR, indicator)
                    if element.is_displayed():
                        logger.log_info(f"Found authentication indicator: {indicator}")
                        break
                except:
                    continue
            else:
                logger.log_warning("No clear authentication indicators found")
                
        except Exception as e:
            logger.log_error(f"Error checking authentication: {e}")
        
        # Step 5: Try to navigate to chat
        logger.log_info("Attempting to navigate to chat page...")
        automation.driver.get("https://flipsidecrypto.xyz/chat/")
        time.sleep(5)
        
        # Take screenshot of chat page
        automation.driver.save_screenshot("debug_chat_page.png")
        logger.log_success("Chat page screenshot saved: debug_chat_page.png")
        
        # Step 6: Check page title and URL
        current_url = automation.driver.current_url
        page_title = automation.driver.title
        logger.log_info(f"Current URL: {current_url}")
        logger.log_info(f"Page title: {page_title}")
        
        # Step 7: Look for chat elements
        logger.log_info("Searching for chat interface elements...")
        chat_selectors = [
            "textarea[placeholder*='Ask FlipsideAI']",
            "textarea",
            "textarea[placeholder*='message']",
            "textarea[data-testid='chat-input']",
            ".chat-input",
            "[data-testid='chat-interface']",
            "input[type='text']",
            ".message-input"
        ]
        
        found_elements = []
        for selector in chat_selectors:
            try:
                elements = automation.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for i, element in enumerate(elements):
                        if element.is_displayed():
                            found_elements.append({
                                "selector": selector,
                                "index": i,
                                "tag": element.tag_name,
                                "visible": element.is_displayed(),
                                "enabled": element.is_enabled(),
                                "text": element.get_attribute("placeholder") or element.get_attribute("value") or "N/A"
                            })
            except Exception as e:
                logger.log_debug(f"Error checking selector {selector}: {e}")
        
        if found_elements:
            logger.log_success(f"Found {len(found_elements)} chat elements:")
            for elem in found_elements:
                logger.log_info(f"  - {elem['selector']}: {elem['tag']} (visible: {elem['visible']}, enabled: {elem['enabled']}, text: '{elem['text']}')")
        else:
            logger.log_warning("No chat input elements found")
        
        # Step 8: Check for any error messages or redirects
        logger.log_info("Checking for error messages or redirects...")
        error_selectors = [
            ".error",
            ".error-message",
            "[data-testid='error']",
            ".login-required",
            ".authentication-error"
        ]
        
        for selector in error_selectors:
            try:
                elements = automation.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        error_text = element.text.strip()
                        if error_text:
                            logger.log_warning(f"Found error message: {error_text}")
            except:
                continue
        
        # Step 9: Check page source for clues
        page_source = automation.driver.page_source
        if "login" in page_source.lower():
            logger.log_warning("Page contains 'login' - may need authentication")
        if "error" in page_source.lower():
            logger.log_warning("Page contains 'error' - may have issues")
        if "chat" in page_source.lower():
            logger.log_success("Page contains 'chat' - chat interface may be present")
        
        logger.log_success("Debug analysis complete")
        
    except Exception as e:
        logger.log_error(f"Debug failed: {e}")
        
    finally:
        if automation.driver:
            automation.driver.quit()
            logger.log_success("WebDriver cleanup complete")
    
    print("\n📊 Debug Summary:")
    print("Check the following files for more information:")
    print("  - debug_main_page.png (main Flipside page)")
    print("  - debug_chat_page.png (chat page)")
    print("  - Check the logs above for element detection results")

if __name__ == "__main__":
    debug_automation()
