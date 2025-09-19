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
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Give the page a moment to fully load
            time.sleep(2)
            
            # Check if we're redirected to login page
            current_url = self.driver.current_url
            logger.debug(f"Session validation - current URL: {current_url}")
            
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
            
            # Check for login redirect or authentication required
            login_indicators = [
                "button[data-testid='login']",
                "a[href*='login']",
                ".login-form",
                "input[type='password']"
            ]
            
            logger.debug("Checking for login indicators...")
            for selector in login_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element and element.is_displayed():
                        logger.warning(f"Session validation failed - found login element: {selector}")
                        return False
                except:
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
        Uses stored credentials for automatic login in all environments.
        
        Args:
            max_wait_time: Maximum time to wait for login (seconds)
            
        Returns:
            True if login was successful, False otherwise
        """
        try:
            logger.warning("🍪 Cookies expired - initiating login fallback")
            
            # Check if we have credentials available
            email = os.getenv('FLIPSIDE_EMAIL')
            password = os.getenv('FLIPSIDE_PASSWORD')
            
            if email and password:
                logger.info("🔐 Using stored credentials for automatic login")
                return self._perform_automatic_login()
            else:
                logger.error("❌ Login fallback failed - credentials not available")
                logger.info("💡 Set FLIPSIDE_EMAIL and FLIPSIDE_PASSWORD environment variables")
                return False
                
        except Exception as e:
            logger.error(f"Login fallback failed: {e}")
            return False
    
    
    def _perform_automatic_login(self) -> bool:
        """
        Perform automatic login using environment credentials with multiple strategies.
        
        Returns:
            True if login was successful, False otherwise
        """
        try:
            # Get credentials from environment
            email = os.getenv('FLIPSIDE_EMAIL')
            password = os.getenv('FLIPSIDE_PASSWORD')
            
            if not email or not password:
                logger.error("❌ Credentials not available in environment")
                return False
            
            logger.info(f"📧 Attempting automatic login for: {email}")
            
            # Strategy 1: Try direct login page
            if self._try_direct_login(email, password):
                return True
            
            # Strategy 2: Try navigating to chat first, then login
            if self._try_chat_redirect_login(email, password):
                return True
            
            # Strategy 3: Try with different user agents
            if self._try_user_agent_login(email, password):
                return True
            
            logger.error("❌ All login strategies failed")
            return False
                
        except Exception as e:
            logger.error(f"Automatic login failed: {e}")
            return False
    
    def _try_direct_login(self, email: str, password: str) -> bool:
        """Try logging in via direct login page."""
        try:
            logger.info("🔄 Strategy 1: Direct login page")
            
            # Navigate directly to login page
            self.driver.get("https://flipsidecrypto.xyz/home/login")
            time.sleep(3)
            
            return self._perform_login_form(email, password)
            
        except Exception as e:
            logger.debug(f"Direct login strategy failed: {e}")
            return False
    
    def _try_chat_redirect_login(self, email: str, password: str) -> bool:
        """Try logging in via chat redirect."""
        try:
            logger.info("🔄 Strategy 2: Chat redirect login")
            
            # Navigate to chat (should redirect to login)
            self.driver.get("https://flipsidecrypto.xyz/chat/")
            time.sleep(5)
            
            return self._perform_login_form(email, password)
            
        except Exception as e:
            logger.debug(f"Chat redirect login strategy failed: {e}")
            return False
    
    def _try_user_agent_login(self, email: str, password: str) -> bool:
        """Try logging in with different user agent."""
        try:
            logger.info("🔄 Strategy 3: User agent login")
            
            # Set a different user agent
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Try login again
            self.driver.get("https://flipsidecrypto.xyz/chat/")
            time.sleep(5)
            
            return self._perform_login_form(email, password)
            
        except Exception as e:
            logger.debug(f"User agent login strategy failed: {e}")
            return False
    
    def _perform_login_form(self, email: str, password: str) -> bool:
        """Perform the actual login form submission."""
        try:
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait a bit more for dynamic content
            time.sleep(3)
            
            # Find and fill email field with multiple attempts
            email_field = None
            email_selectors = [
                "#email",
                "input[type='email']",
                "input[name='email']",
                "input[placeholder*='email']",
                "input[placeholder*='Email']"
            ]
            
            for selector in email_selectors:
                try:
                    email_field = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    if email_field and email_field.is_displayed():
                        logger.info(f"✅ Found email field with selector: {selector}")
                        break
                except:
                    continue
            
            if not email_field:
                logger.error("❌ Could not find email input field")
                return False
            
            # Clear and fill email
            email_field.clear()
            time.sleep(0.5)
            email_field.send_keys(email)
            logger.info("✅ Email entered")
            
            # Find and fill password field
            password_field = None
            password_selectors = [
                "#password",
                "input[type='password']",
                "input[name='password']",
                "input[placeholder*='password']",
                "input[placeholder*='Password']"
            ]
            
            for selector in password_selectors:
                try:
                    password_field = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    if password_field and password_field.is_displayed():
                        logger.info(f"✅ Found password field with selector: {selector}")
                        break
                except:
                    continue
            
            if not password_field:
                logger.error("❌ Could not find password input field")
                return False
            
            # Clear and fill password
            password_field.clear()
            time.sleep(0.5)
            password_field.send_keys(password)
            logger.info("✅ Password entered")
            
            # Find and click login button
            login_button = None
            login_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Login')",
                "button:contains('Sign In')",
                "button:contains('Log in')"
            ]
            
            for selector in login_selectors:
                try:
                    if ":contains(" in selector:
                        # Use XPath for text-based selection
                        xpath = f"//button[contains(text(), '{selector.split(':contains(')[1].split(')')[0]}')]"
                        login_button = self.driver.find_element(By.XPATH, xpath)
                    else:
                        login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if login_button and login_button.is_displayed():
                        logger.info(f"✅ Found login button with selector: {selector}")
                        break
                except:
                    continue
            
            if not login_button:
                # Try to find button by text content
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    try:
                        if button.text and any(text in button.text.lower() for text in ["login", "sign in", "log in"]) and button.is_displayed():
                            login_button = button
                            logger.info("✅ Found login button by text content")
                            break
                    except:
                        pass
            
            if login_button:
                # Scroll to button and click
                self.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
                time.sleep(1)
                login_button.click()
                logger.info("✅ Login button clicked")
            else:
                # Try pressing Enter on password field
                password_field.send_keys("\n")
                logger.info("✅ Submitted form with Enter key")
            
            # Wait for login to complete with multiple checks
            logger.info("⏳ Waiting for login to complete...")
            
            # Wait for redirect or page change
            max_wait = 15
            for i in range(max_wait):
                time.sleep(1)
                current_url = self.driver.current_url
                
                # Check if we're no longer on login page
                if 'login' not in current_url.lower() and 'signin' not in current_url.lower():
                    logger.info(f"✅ Redirected away from login page: {current_url}")
                    break
                
                if i == max_wait - 1:
                    logger.warning("⚠️ Still on login page after waiting")
            
            # Additional wait for page to stabilize
            time.sleep(3)
            
            # Validate session with retries
            max_validation_attempts = 5
            for attempt in range(max_validation_attempts):
                logger.info(f"🔍 Validating session (attempt {attempt + 1}/{max_validation_attempts})...")
                
                if self.validate_session():
                    logger.info("✅ Automatic login successful")
                    
                    # Save fresh cookies
                    if self.save_fresh_cookies():
                        logger.info("✅ Fresh cookies saved")
                    
                    return True
                else:
                    if attempt < max_validation_attempts - 1:
                        logger.info("⏳ Session validation failed, retrying in 5 seconds...")
                        time.sleep(5)
                    else:
                        logger.warning("⚠️ Session validation failed after all attempts")
                        return False
            
            return False
                
        except Exception as e:
            logger.error(f"Login form submission failed: {e}")
            return False
    
    def _find_element_by_selectors(self, selectors: list):
        """
        Find an element using a list of CSS selectors.
        
        Args:
            selectors: List of CSS selectors to try
            
        Returns:
            WebElement if found, None otherwise
        """
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element and element.is_displayed():
                    logger.debug(f"✅ Found element with selector: {selector}")
                    return element
            except:
                continue
        return None
    
    
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
