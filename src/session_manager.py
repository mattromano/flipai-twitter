"""
Session Manager for Flipside Chat Automation

Handles cookie encoding/decoding, session validation, and authentication state management.
"""

import base64
import json
import logging
import os
import time
from typing import Dict, List, Optional, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages Flipside Crypto session cookies and authentication state."""
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.cookies = []
        
    def encode_cookies_for_secret(self, cookies: List[Dict[str, Any]]) -> str:
        """
        Encode cookies to base64 string for GitHub secrets storage.
        
        Args:
            cookies: List of cookie dictionaries from Selenium
            
        Returns:
            Base64 encoded string of cookies
        """
        try:
            # Convert cookies to JSON string
            cookies_json = json.dumps(cookies)
            # Encode to base64
            encoded = base64.b64encode(cookies_json.encode('utf-8')).decode('utf-8')
            logger.info(f"Successfully encoded {len(cookies)} cookies for secret storage")
            return encoded
        except Exception as e:
            logger.error(f"Failed to encode cookies: {e}")
            raise
    
    def decode_cookies_from_secret(self, encoded_cookies: str) -> List[Dict[str, Any]]:
        """
        Decode cookies from base64 string stored in GitHub secrets.
        
        Args:
            encoded_cookies: Base64 encoded string of cookies
            
        Returns:
            List of cookie dictionaries for Selenium
        """
        try:
            # Decode from base64
            decoded = base64.b64decode(encoded_cookies.encode('utf-8')).decode('utf-8')
            # Parse JSON
            cookies = json.loads(decoded)
            logger.info(f"Successfully decoded {len(cookies)} cookies from secret")
            return cookies
        except Exception as e:
            logger.error(f"Failed to decode cookies: {e}")
            raise
    
    def load_cookies_from_env(self) -> List[Dict[str, Any]]:
        """
        Load cookies from environment variable (GitHub secret).
        
        Returns:
            List of cookie dictionaries for Selenium
        """
        encoded_cookies = os.getenv('FLIPSIDE_COOKIES')
        if not encoded_cookies:
            raise ValueError("FLIPSIDE_COOKIES environment variable not set")
        
        return self.decode_cookies_from_secret(encoded_cookies)
    
    def apply_cookies_to_driver(self, cookies: List[Dict[str, Any]]) -> bool:
        """
        Apply cookies to the current WebDriver session.
        
        Args:
            cookies: List of cookie dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Navigate to the domain first
            self.driver.get("https://flipsidecrypto.xyz")
            
            # Apply each cookie
            for cookie in cookies:
                try:
                    # Remove 'expiry' key if present as it can cause issues
                    cookie_copy = cookie.copy()
                    if 'expiry' in cookie_copy:
                        del cookie_copy['expiry']
                    
                    self.driver.add_cookie(cookie_copy)
                    logger.debug(f"Applied cookie: {cookie_copy.get('name', 'unknown')}")
                except Exception as e:
                    logger.warning(f"Failed to apply cookie {cookie.get('name', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Successfully applied {len(cookies)} cookies to driver")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply cookies to driver: {e}")
            return False
    
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
            
            # Check if we're redirected to login page
            current_url = self.driver.current_url
            if 'login' in current_url.lower() or 'signin' in current_url.lower():
                logger.warning(f"Session validation failed - redirected to login page: {current_url}")
                return False
            
            # Check for authentication indicators
            # Look for chat input or user-specific elements
            auth_indicators = [
                "textarea[placeholder*='Ask FlipsideAI']",
                "textarea[placeholder*='message']",
                "textarea[data-testid='chat-input']",
                "[data-testid='user-menu']",
                ".user-avatar",
                ".authenticated"
            ]
            
            for selector in auth_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element:
                        logger.info("Session validation successful - found authenticated element")
                        return True
                except:
                    continue
            
            # Check for login redirect or authentication required
            login_indicators = [
                "button[data-testid='login']",
                "a[href*='login']",
                ".login-form",
                "input[type='password']"
            ]
            
            for selector in login_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element:
                        logger.warning("Session validation failed - found login element")
                        return False
                except:
                    continue
            
            # If we can't find clear indicators, assume session is valid
            logger.info("Session validation inconclusive - assuming valid")
            return True
            
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            return False
    
    def refresh_session_if_needed(self) -> bool:
        """
        Refresh session if it appears to be expired or invalid.
        
        Returns:
            True if session is valid after refresh attempt, False otherwise
        """
        try:
            # Try to refresh the page
            self.driver.refresh()
            
            # Wait for page to reload
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Validate session again
            return self.validate_session()
            
        except Exception as e:
            logger.error(f"Failed to refresh session: {e}")
            return False
    
    def get_current_cookies(self) -> List[Dict[str, Any]]:
        """
        Get current cookies from the driver.
        
        Returns:
            List of current cookie dictionaries
        """
        try:
            cookies = self.driver.get_cookies()
            logger.info(f"Retrieved {len(cookies)} current cookies")
            return cookies
        except Exception as e:
            logger.error(f"Failed to get current cookies: {e}")
            return []
    
    def save_cookies_for_future_use(self, filepath: str = "cookies.json") -> bool:
        """
        Save current cookies to a file for future use.
        
        Args:
            filepath: Path to save cookies file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cookies = self.get_current_cookies()
            if not cookies:
                logger.warning("No cookies to save")
                return False
            
            with open(filepath, 'w') as f:
                json.dump(cookies, f, indent=2)
            
            logger.info(f"Saved {len(cookies)} cookies to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")
            return False
    
    def load_cookies_from_file(self, filepath: str = "cookies.json") -> List[Dict[str, Any]]:
        """
        Load cookies from a file.
        
        Args:
            filepath: Path to cookies file
            
        Returns:
            List of cookie dictionaries
        """
        try:
            with open(filepath, 'r') as f:
                content = f.read().strip()
            
            # Check if it's a base64 encoded format (starts with FLIPSIDE_COOKIES=)
            if content.startswith('FLIPSIDE_COOKIES='):
                # Extract the base64 part after the equals sign
                encoded_cookies = content.split('=', 1)[1]
                # Decode the base64 string
                cookies = self.decode_cookies_from_secret(encoded_cookies)
            else:
                # Try to load as regular JSON
                cookies = json.loads(content)
            
            logger.info(f"Loaded {len(cookies)} cookies from {filepath}")
            return cookies
            
        except Exception as e:
            logger.error(f"Failed to load cookies from file: {e}")
            return []
    
    def handle_login_fallback(self, max_wait_time: int = 300) -> bool:
        """
        Handle login fallback when cookies are expired.
        This will wait for manual login and then save fresh cookies.
        
        Args:
            max_wait_time: Maximum time to wait for manual login (seconds)
            
        Returns:
            True if login was successful, False otherwise
        """
        try:
            logger.warning("🍪 Cookies expired - initiating login fallback")
            logger.info(f"⏰ Waiting up to {max_wait_time} seconds for manual login...")
            
            # Navigate to login page
            self.driver.get("https://flipsidecrypto.xyz/chat/")
            
            start_time = time.time()
            login_successful = False
            
            while time.time() - start_time < max_wait_time:
                try:
                    # Check if we're now authenticated
                    if self.validate_session():
                        logger.info("✅ Manual login detected - session is now valid")
                        login_successful = True
                        break
                    
                    # Check if we're still on login page
                    current_url = self.driver.current_url
                    if 'login' not in current_url.lower() and 'signin' not in current_url.lower():
                        # We might have been redirected, check again
                        time.sleep(2)
                        continue
                    
                    # Wait a bit before checking again
                    time.sleep(5)
                    
                    # Log progress every 30 seconds
                    elapsed = int(time.time() - start_time)
                    if elapsed % 30 == 0 and elapsed > 0:
                        remaining = max_wait_time - elapsed
                        logger.info(f"⏳ Still waiting for login... {remaining} seconds remaining")
                
                except Exception as e:
                    logger.warning(f"Error during login wait: {e}")
                    time.sleep(5)
                    continue
            
            if login_successful:
                # Save fresh cookies for future use
                logger.info("💾 Saving fresh cookies for future use...")
                if self.save_fresh_cookies():
                    logger.info("✅ Fresh cookies saved successfully")
                else:
                    logger.warning("⚠️ Failed to save fresh cookies")
                
                return True
            else:
                logger.error(f"❌ Login timeout after {max_wait_time} seconds")
                return False
                
        except Exception as e:
            logger.error(f"Login fallback failed: {e}")
            return False
    
    
    def save_fresh_cookies(self, filepath: str = "flipside_cookies.txt") -> bool:
        """
        Save fresh cookies in the format expected by the automation.
        
        Args:
            filepath: Path to save cookies file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current cookies
            cookies = self.get_current_cookies()
            if not cookies:
                logger.warning("No cookies to save")
                return False
            
            # Encode cookies for storage
            encoded_cookies = self.encode_cookies_for_secret(cookies)
            
            # Save in the expected format
            with open(filepath, 'w') as f:
                f.write(f"FLIPSIDE_COOKIES={encoded_cookies}")
            
            logger.info(f"✅ Saved {len(cookies)} fresh cookies to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save fresh cookies: {e}")
            return False
    
    def setup_session_with_fallback(self, cookie_file: str = "flipside_cookies.txt", 
                                  max_login_wait: int = 300) -> bool:
        """
        Set up session with login fallback if cookies are expired.
        
        Args:
            cookie_file: Path to cookie file
            max_login_wait: Maximum time to wait for manual login (seconds)
            
        Returns:
            True if session is valid, False otherwise
        """
        try:
            # Try to load and apply cookies
            logger.info("🍪 Attempting to load existing cookies...")
            cookies = self.load_cookies_from_file(cookie_file)
            
            if cookies:
                logger.info(f"📁 Loaded {len(cookies)} cookies from {cookie_file}")
                
                # Apply cookies to driver
                if self.apply_cookies_to_driver(cookies):
                    logger.info("✅ Cookies applied successfully")
                    
                    # Validate session
                    if self.validate_session():
                        logger.info("✅ Session validation successful - cookies are valid")
                        return True
                    else:
                        logger.warning("⚠️ Session validation failed - cookies may be expired")
                else:
                    logger.warning("⚠️ Failed to apply cookies")
            else:
                logger.warning("⚠️ No cookies found in file")
            
            # If we get here, cookies are invalid or missing
            logger.info("🔄 Initiating login fallback...")
            return self.handle_login_fallback(max_login_wait)
            
        except Exception as e:
            logger.error(f"Session setup with fallback failed: {e}")
            return False
