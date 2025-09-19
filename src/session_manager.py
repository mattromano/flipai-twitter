"""
Session Manager for Flipside Chat Automation

Handles cookie encoding/decoding, session validation, and authentication state management.
"""

import base64
import json
import logging
import os
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
            
            # Check for authentication indicators
            # Look for chat input or user-specific elements
            auth_indicators = [
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
                cookies = json.load(f)
            
            logger.info(f"Loaded {len(cookies)} cookies from {filepath}")
            return cookies
            
        except Exception as e:
            logger.error(f"Failed to load cookies from file: {e}")
            return []
