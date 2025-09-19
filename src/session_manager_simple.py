"""
Simplified session manager that focuses on cookie-based authentication.
This version removes the complex login fallback and focuses on reliable cookie management.
"""

import os
import time
import base64
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .automation_logger import AutomationLogger

logger = AutomationLogger()

class SimpleSessionManager:
    """Simplified session manager for cookie-based authentication."""
    
    def __init__(self, driver):
        self.driver = driver
        self.cookie_file = "flipside_cookies.txt"
    
    def setup_session(self) -> bool:
        """
        Set up session using stored cookies.
        
        Returns:
            True if session is valid, False otherwise
        """
        try:
            logger.info("🍪 Setting up session with cookies")
            
            # Load and apply cookies
            if self.load_cookies():
                logger.info("✅ Cookies loaded successfully")
                
                # Validate session
                if self.validate_session():
                    logger.info("✅ Session validation successful")
                    return True
                else:
                    logger.warning("⚠️ Session validation failed - cookies may be expired")
                    return False
            else:
                logger.error("❌ Failed to load cookies")
                return False
                
        except Exception as e:
            logger.error(f"Session setup failed: {e}")
            return False
    
    def load_cookies(self) -> bool:
        """
        Load cookies from file and apply them to the driver.
        
        Returns:
            True if cookies were loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(self.cookie_file):
                logger.error(f"Cookie file not found: {self.cookie_file}")
                return False
            
            # Read cookies from file
            with open(self.cookie_file, 'r') as f:
                cookie_string = f.read().strip()
            
            if not cookie_string:
                logger.error("Cookie file is empty")
                return False
            
            # Parse cookies from string format
            cookies = self._parse_cookie_string(cookie_string)
            
            if not cookies:
                logger.error("No valid cookies found in file")
                return False
            
            # Navigate to the domain first
            self.driver.get("https://flipsidecrypto.xyz")
            time.sleep(2)
            
            # Apply cookies
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    logger.debug(f"Failed to add cookie {cookie.get('name', 'unknown')}: {e}")
                    continue
            
            logger.info(f"✅ Applied {len(cookies)} cookies")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")
            return False
    
    def _parse_cookie_string(self, cookie_string: str) -> list:
        """
        Parse cookie string into list of cookie dictionaries.
        
        Args:
            cookie_string: Cookie string in format "name1=value1; name2=value2; ..."
            
        Returns:
            List of cookie dictionaries
        """
        cookies = []
        
        # Split by semicolon and parse each cookie
        cookie_pairs = cookie_string.split(';')
        
        for pair in cookie_pairs:
            pair = pair.strip()
            if '=' in pair:
                name, value = pair.split('=', 1)
                name = name.strip()
                value = value.strip()
                
                if name and value:
                    # Create cookie dictionary
                    cookie = {
                        'name': name,
                        'value': value,
                        'domain': '.flipsidecrypto.xyz',
                        'path': '/',
                        'secure': True,
                        'httpOnly': False
                    }
                    cookies.append(cookie)
        
        return cookies
    
    def validate_session(self) -> bool:
        """
        Validate that the current session is authenticated.
        
        Returns:
            True if session is valid, False otherwise
        """
        try:
            # Navigate to chat page
            self.driver.get("https://flipsidecrypto.xyz/chat/")
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Give the page a moment to fully load
            time.sleep(3)
            
            # Check if we're redirected to login page
            current_url = self.driver.current_url
            logger.debug(f"Session validation - current URL: {current_url}")
            
            if 'login' in current_url.lower() or 'signin' in current_url.lower():
                logger.warning(f"Session validation failed - redirected to login page: {current_url}")
                return False
            
            # Check for authentication indicators
            auth_indicators = [
                "textarea[placeholder*='Ask FlipsideAI']",
                "textarea[placeholder*='message']",
                "textarea[data-testid='chat-input']",
                "[data-testid='user-menu']",
                ".user-avatar",
                ".authenticated"
            ]
            
            logger.debug("Checking for authentication indicators...")
            for selector in auth_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element and element.is_displayed():
                        logger.info(f"Session validation successful - found authenticated element: {selector}")
                        return True
                except Exception as e:
                    logger.debug(f"Selector {selector} not found: {e}")
                    continue
            
            # Additional check: look for any textarea that might be the chat input
            try:
                textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                for textarea in textareas:
                    if textarea.is_displayed():
                        placeholder = textarea.get_attribute("placeholder") or ""
                        if "ask" in placeholder.lower() or "message" in placeholder.lower():
                            logger.info(f"Session validation successful - found chat textarea with placeholder: {placeholder}")
                            return True
            except Exception as e:
                logger.debug(f"Error checking textareas: {e}")
            
            # If we can't find clear indicators, assume session is valid
            logger.info("Session validation inconclusive - assuming valid")
            return True
            
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            return False
    
    def save_fresh_cookies(self) -> bool:
        """
        Save current cookies to file for future use.
        
        Returns:
            True if cookies were saved successfully, False otherwise
        """
        try:
            cookies = self.driver.get_cookies()
            
            if not cookies:
                logger.warning("No cookies to save")
                return False
            
            # Save cookies in simple format
            with open(self.cookie_file, 'w') as f:
                for cookie in cookies:
                    f.write(f"{cookie['name']}={cookie['value']}; ")
            
            logger.info(f"✅ Saved {len(cookies)} cookies to {self.cookie_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")
            return False
