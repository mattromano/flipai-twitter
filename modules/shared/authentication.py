import os
import time
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from modules.shared.logger import AutomationLogger


class StealthAuthenticator:
    """Handles stealth authentication for Flipside."""
    
    def __init__(self, logger=None):
        self.driver = None
        self.logger = logger or AutomationLogger()
    
    def _detect_chrome_version(self) -> Optional[int]:
        """Detect the installed Chrome version."""
        try:
            import subprocess
            import re
            import platform
            
            system = platform.system()
            
            if system == "Darwin":  # macOS
                chrome_paths = [
                    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"
                ]
                for chrome_path in chrome_paths:
                    try:
                        result = subprocess.run(
                            [chrome_path, "--version"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode == 0:
                            version_match = re.search(r'(\d+)\.', result.stdout)
                            if version_match:
                                version = int(version_match.group(1))
                                self.logger.log_info(f"Found Chrome at: {chrome_path}")
                                self.logger.log_info(f"✅ Detected Chrome version: {version} (from: {result.stdout.strip()})")
                                return version
                    except:
                        continue
            elif system == "Linux":
                try:
                    result = subprocess.run(
                        ["google-chrome", "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        version_match = re.search(r'(\d+)\.', result.stdout)
                        if version_match:
                            version = int(version_match.group(1))
                            self.logger.log_info(f"Found Chrome at: /usr/bin/google-chrome")
                            self.logger.log_info(f"✅ Detected Chrome version: {version} (from: {result.stdout.strip()})")
                            return version
                except:
                    pass
            elif system == "Windows":
                try:
                    import winreg
                    reg_path = r"SOFTWARE\Google\Chrome\BLBeacon"
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
                    version = winreg.QueryValueEx(key, "version")[0]
                    version_match = re.search(r'(\d+)\.', version)
                    if version_match:
                        version_num = int(version_match.group(1))
                        self.logger.log_info(f"✅ Detected Chrome version: {version_num} (from: {version})")
                        return version_num
                except:
                    pass
            
            return None
        except Exception as e:
            self.logger.log_warning(f"Failed to detect Chrome version: {e}")
            return None
    
    def setup_driver(self):
        """Setup stealth Chrome driver with anti-detection capabilities."""
        try:
            self.logger.log_info("🤖 Setting up stealth Chrome driver")
            
            import undetected_chromedriver as uc
            
            # Detect Chrome version to ensure compatibility
            chrome_version = self._detect_chrome_version()
            
            # Configure Chrome options for stealth
            options = uc.ChromeOptions()
            
            # Headless mode based on environment
            headless_mode = os.getenv('HEADLESS_MODE', 'false').lower() == 'true' or \
                          os.getenv('CHROME_HEADLESS', 'false').lower() == 'true'
            if headless_mode:
                options.add_argument('--headless=new')
                self.logger.log_info("Headless mode enabled")
            else:
                self.logger.log_info("Headless mode disabled (visible browser)")
            
            # Anti-detection arguments
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            # Note: JavaScript must be enabled for login forms to render
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--window-size=1920,1080')
            
            # User agent - match detected Chrome version or use 141 as fallback
            if chrome_version:
                user_agent = f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36'
            else:
                user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
            options.add_argument(f'--user-agent={user_agent}')
            
            # Create undetected driver with version matching
            if chrome_version:
                self.logger.log_info(f"Using Chrome version {chrome_version} for ChromeDriver")
                self.driver = uc.Chrome(options=options, version_main=chrome_version)
            else:
                self.logger.log_info("Auto-detecting Chrome version for ChromeDriver")
                self.driver = uc.Chrome(options=options)
            
            # Execute stealth scripts
            self._apply_stealth_scripts()
            
            self.logger.log_success("✅ Stealth Chrome driver setup complete")
            return self.driver
            
        except Exception as e:
            self.logger.log_error(f"Stealth driver setup failed: {e}")
            return None
    
    def _apply_stealth_scripts(self):
        """Apply JavaScript stealth scripts to avoid detection."""
        try:
            # Remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Override navigator properties
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """)
            
            # Override permissions
            self.driver.execute_script("""
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
            """)
            
            self.logger.log_info("✅ Stealth scripts applied")
            
        except Exception as e:
            self.logger.log_warning(f"Failed to apply some stealth scripts: {e}")
    
    def login(self) -> bool:
        """Perform stealth login using the original working logic."""
        try:
            self.logger.log_info("🔐 Starting stealth login process")
            
            # Navigate directly to login page
            login_url = "https://flipsidecrypto.xyz/home/login"
            self.logger.log_info(f"🌐 Navigating to login page: {login_url}")
            self.driver.get(login_url)
            self._human_like_delay(3, 5)
            
            # Wait for page to load - allow time for JavaScript to render
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for JavaScript-rendered content
            self._human_like_delay(2, 3)
            
            # Check if we're already logged in (might redirect automatically)
            current_url = self.driver.current_url
            if 'login' not in current_url.lower() or self._check_if_logged_in():
                self.logger.log_info("✅ Already logged in or redirected")
                return True
            
            # Debug: Take screenshot and log page info
            try:
                current_url = self.driver.current_url
                page_title = self.driver.title
                self.logger.log_info(f"📍 Current URL: {current_url}")
                self.logger.log_info(f"📄 Page title: {page_title}")
                
                # Save screenshot for debugging
                screenshot_path = f"screenshots/login_page_{int(time.time())}.png"
                self.driver.save_screenshot(screenshot_path)
                self.logger.log_info(f"📸 Debug screenshot saved: {screenshot_path}")
                
                # Log all input elements on the page
                all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                self.logger.log_info(f"🔍 Found {len(all_inputs)} input elements on page")
                for i, inp in enumerate(all_inputs[:10]):  # Log first 10
                    try:
                        inp_type = inp.get_attribute("type") or "unknown"
                        inp_name = inp.get_attribute("name") or "none"
                        inp_id = inp.get_attribute("id") or "none"
                        inp_placeholder = inp.get_attribute("placeholder") or "none"
                        inp_class = inp.get_attribute("class") or "none"
                        is_displayed = inp.is_displayed()
                        self.logger.log_info(f"   Input {i}: type={inp_type}, name={inp_name}, id={inp_id}, placeholder={inp_placeholder[:30]}, displayed={is_displayed}")
                    except:
                        pass
            except Exception as debug_error:
                self.logger.log_warning(f"Debug logging failed: {debug_error}")
            
            # Find and fill email field with comprehensive selectors
            email_field = self._find_element_with_retry([
                "#email",
                "input[type='email']",
                "input[name='email']",
                "input[placeholder*='email']",
                "input[placeholder*='Email']",
                "input[id*='email']",
                "input[id*='Email']",
                "input[class*='email']",
                "input[class*='Email']",
                "input[data-testid*='email']",
                "input[data-testid*='Email']",
                "input[aria-label*='email']",
                "input[aria-label*='Email']",
                "input[autocomplete='email']",
                "input[autocomplete='username']"
            ], max_attempts=5)
            
            if not email_field:
                self.logger.log_error("❌ Could not find email field")
                # Try one more time with even more generic selectors
                self.logger.log_info("🔄 Trying fallback: all visible input fields...")
                try:
                    all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for inp in all_inputs:
                        if inp.is_displayed() and inp.is_enabled():
                            inp_type = inp.get_attribute("type") or ""
                            inp_placeholder = (inp.get_attribute("placeholder") or "").lower()
                            if inp_type == "email" or "email" in inp_placeholder or inp_type == "text":
                                self.logger.log_info(f"⚠️ Found potential email field: type={inp_type}, placeholder={inp.get_attribute('placeholder')}")
                                email_field = inp
                                break
                except:
                    pass
                
                if not email_field:
                    return False
            
            # Get credentials from environment
            email = os.getenv('FLIPSIDE_EMAIL')
            password = os.getenv('FLIPSIDE_PASSWORD')
            
            if not email or not password:
                self.logger.log_error("❌ FLIPSIDE_EMAIL and FLIPSIDE_PASSWORD must be set in environment")
                return False
            
            # Human-like email entry
            self.logger.log_info("📧 Entering email")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", email_field)
            self._human_like_delay(0.5, 1.0)
            email_field.click()
            self._human_like_delay(0.2, 0.5)
            self._human_like_typing(email_field, email)
            
            # Find and fill password field
            password_field = self._find_element_with_retry([
                "#password",
                "input[type='password']",
                "input[name='password']",
                "input[placeholder*='password']"
            ])
            
            if not password_field:
                self.logger.log_error("❌ Could not find password field")
                return False
            
            # Human-like password entry
            self.logger.log_info("🔑 Entering password")
            self._human_like_delay(0.5, 1.0)
            password_field.click()
            self._human_like_delay(0.2, 0.5)
            self._human_like_typing(password_field, password)
            
            # Find and click login button
            login_button = self._find_element_with_retry([
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Login')",
                "button:contains('Sign In')"
            ])
            
            if login_button:
                self.logger.log_info("🖱️ Clicking login button")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
                self._human_like_delay(0.5, 1.0)
                login_button.click()
            else:
                # Try pressing Enter
                self.logger.log_info("⌨️ Submitting with Enter key")
                from selenium.webdriver.common.keys import Keys
                password_field.send_keys(Keys.RETURN)
            
            # Wait for login to complete
            self.logger.log_info("⏳ Waiting for login to complete")
            self._human_like_delay(3, 5)
            
            # Wait for redirect or page load
            max_wait = 30
            login_success = False
            for i in range(max_wait):
                try:
                    # Check if window is still open
                    if not self.driver or not hasattr(self.driver, 'current_url'):
                        self.logger.log_error("❌ Browser window was closed")
                        return False
                    
                    current_url = self.driver.current_url or ""
                    self.logger.log_debug(f"Waiting for login... ({i+1}/{max_wait}) - URL: {current_url}")
                    
                    # Check if we're logged in
                    if self._check_if_logged_in():
                        self.logger.log_info(f"✅ Login successful! Redirected to: {current_url}")
                        login_success = True
                        break
                    
                    # Also check if we're no longer on login page
                    if current_url and 'login' not in current_url.lower() and 'signin' not in current_url.lower():
                        # Give it a bit more time for page to fully load
                        self._human_like_delay(2, 3)
                        if self._check_if_logged_in():
                            self.logger.log_info(f"✅ Login successful! On page: {current_url}")
                            login_success = True
                            break
                    
                    time.sleep(1)
                except Exception as wait_error:
                    error_msg = str(wait_error).lower()
                    if 'no such window' in error_msg or 'target window already closed' in error_msg:
                        self.logger.log_error("❌ Browser window was closed during login wait")
                        return False
                    self.logger.log_warning(f"Error during login wait: {wait_error}")
                    time.sleep(1)
                    continue
            
            # Final validation with additional wait
            if not login_success:
                self.logger.log_info("🔄 Performing final login check...")
                self._human_like_delay(2, 3)
                login_success = self._check_if_logged_in()
            
            if login_success:
                self.logger.log_info("✅ Login successful")
                
                # Navigate to chat page after successful login
                current_url = self.driver.current_url or ""
                if '/chat/' in current_url:
                    self.logger.log_info(f"✅ Already on chat page: {current_url}")
                else:
                    # Navigate to chat page manually
                    self.logger.log_info("🔄 Navigating to chat page...")
                    self.driver.get("https://flipsidecrypto.xyz/chat/")
                    self._human_like_delay(3, 5)
                    self.logger.log_info(f"✅ Navigated to chat page: {self.driver.current_url}")
                
                return True
            else:
                self.logger.log_error("❌ Login failed - not authenticated")
                # Take screenshot for debugging
                try:
                    screenshot_path = f"screenshots/login_failed_{int(time.time())}.png"
                    self.driver.save_screenshot(screenshot_path)
                    self.logger.log_info(f"📸 Failed login screenshot: {screenshot_path}")
                except:
                    pass
                return False
                
        except Exception as e:
            self.logger.log_error(f"Login process failed: {e}")
            return False
    
    def _human_like_delay(self, min_delay: float = 0.5, max_delay: float = 2.0):
        """Add human-like delays between actions."""
        import random
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _human_like_typing(self, element, text: str):
        """Type text in a human-like manner."""
        import random
        try:
            element.clear()
            self._human_like_delay(0.1, 0.3)
            
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            self._human_like_delay(0.2, 0.5)
            
        except Exception as e:
            self.logger.log_error(f"Human-like typing failed: {e}")
            # Fallback to normal typing
            element.clear()
            element.send_keys(text)
    
    def _find_element_with_retry(self, selectors: list, max_attempts: int = 3):
        """Find element with retry logic."""
        for attempt in range(max_attempts):
            for selector in selectors:
                try:
                    if ":contains(" in selector:
                        # Use XPath for text-based selection
                        text = selector.split(':contains(')[1].split(')')[0].strip("'\"")
                        xpath = f"//button[contains(text(), '{text}')]"
                        element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                    else:
                        # Try WebDriverWait for better reliability
                        try:
                            element = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                        except:
                            # Fallback to immediate find
                            element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if element and element.is_displayed() and element.is_enabled():
                        self.logger.log_info(f"✅ Found element with selector: {selector}")
                        return element
                except Exception as e:
                    self.logger.log_debug(f"Selector {selector} failed (attempt {attempt + 1}/{max_attempts}): {e}")
                    continue
            
            if attempt < max_attempts - 1:
                self.logger.log_info(f"Retrying element search (attempt {attempt + 2}/{max_attempts})...")
                self._human_like_delay(2, 3)
        
        return None
    
    def _check_if_logged_in(self) -> bool:
        """Check if user is logged in."""
        try:
            if not self.driver:
                return False
                
            current_url = self.driver.current_url or ""
            
            # Check URL - if we're on chat page, we're likely logged in
            if '/chat/' in current_url.lower():
                # Additional verification: check for chat elements
                try:
                    # Wait a moment for page to render
                    time.sleep(1)
                    
                    # Check for chat input or any chat-related elements
                    chat_indicators = [
                        "textarea[placeholder*='Ask']",
                        "textarea[placeholder*='ask']",
                        "textarea[placeholder*='message']",
                        "textarea[placeholder*='Message']",
                        "textarea[data-testid='chat-input']",
                        "textarea",
                        "input[placeholder*='message']",
                        "input[placeholder*='ask']"
                    ]
                    
                    for selector in chat_indicators:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                if element and element.is_displayed() and element.is_enabled():
                                    self.logger.log_debug(f"✅ Login verified by chat element: {selector}")
                                    return True
                        except:
                            continue
                    
                    # If we're on /chat/ URL, assume logged in even if we can't find input yet
                    # (might still be loading)
                    self.logger.log_debug(f"✅ Login verified by URL: {current_url}")
                    return True
                except Exception as e:
                    self.logger.log_debug(f"Error checking chat elements: {e}")
                    # Still return True if on chat URL
                    if '/chat/' in current_url.lower():
                        return True
            
            # Check if we're still on login page
            if 'login' in current_url.lower() or 'signin' in current_url.lower():
                return False
            
            # If URL doesn't contain login/signin and we're not on chat, might be logged in
            # but on a different page - check for any user-specific content
            try:
                # Look for any signs we're authenticated (not on login page)
                page_source = self.driver.page_source.lower()
                if 'welcome' in page_source or 'dashboard' in page_source or 'chat' in page_source:
                    return True
            except:
                pass
            
            return False
            
        except Exception as e:
            self.logger.log_debug(f"Login check failed: {e}")
            return False
    
    def _try_traditional_login(self) -> bool:
        """Try traditional email/password login approach."""
        try:
            self.logger.log_info("🔐 Trying traditional email/password login...")
            
            # Find email field
            email_field = None
            email_selectors = [
                "input[name='email']",
                "input[type='email']",
                "input[placeholder*='email']",
                "input[placeholder*='Email']",
                "input[id*='email']",
                "input[class*='email']",
                "input[data-testid*='email']",
                "input[aria-label*='email']",
                "input[aria-label*='Email']",
                "input[autocomplete='email']",
                "input[autocomplete='username']"
            ]
            
            for selector in email_selectors:
                try:
                    email_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    self.logger.log_info(f"✅ Found email field with selector: {selector}")
                    break
                except Exception as e:
                    self.logger.log_debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not email_field:
                self.logger.log_error("❌ Could not find email field for traditional login")
                return False
            
            # Find password field
            password_field = None
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "input[placeholder*='password']",
                "input[placeholder*='Password']",
                "input[id*='password']",
                "input[class*='password']",
                "input[data-testid*='password']",
                "input[aria-label*='password']",
                "input[aria-label*='Password']",
                "input[autocomplete='current-password']"
            ]
            
            for selector in password_selectors:
                try:
                    password_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    self.logger.log_info(f"✅ Found password field with selector: {selector}")
                    break
                except Exception as e:
                    self.logger.log_debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not password_field:
                self.logger.log_error("❌ Could not find password field for traditional login")
                return False
            
            # Get credentials from environment
            email = os.getenv('FLIPSIDE_EMAIL')
            password = os.getenv('FLIPSIDE_PASSWORD')
            
            if not email or not password:
                self.logger.log_error("❌ FLIPSIDE_EMAIL and FLIPSIDE_PASSWORD must be set in environment")
                return False
            
            # Fill in credentials
            self.logger.log_info("⌨️ Filling in email and password")
            email_field.clear()
            email_field.send_keys(email)
            time.sleep(1)
            
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # Find and click submit button
            submit_button = None
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Sign In')",
                "button:contains('Login')",
                "button:contains('Log In')",
                "button:contains('Sign in')",
                "button:contains('Log in')",
                "[data-testid*='submit']",
                "[data-testid*='login']",
                "[data-testid*='signin']",
                ".submit-button",
                ".login-button",
                ".signin-button"
            ]
            
            for selector in submit_selectors:
                try:
                    if selector.startswith('button:contains'):
                        # XPath for text content
                        xpath = f"//button[contains(text(), '{selector.split('contains(')[1].split(')')[0].strip(chr(39))}')]"
                        submit_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                    else:
                        submit_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    self.logger.log_info(f"✅ Found submit button with selector: {selector}")
                    break
                except Exception as e:
                    self.logger.log_debug(f"Submit selector {selector} failed: {e}")
                    continue
            
            if not submit_button:
                self.logger.log_error("❌ Could not find submit button for traditional login")
                return False
            
            # Submit the form properly
            self.logger.log_info("🖱️ Submitting form")
            try:
                # Try pressing Enter on the password field first
                from selenium.webdriver.common.keys import Keys
                password_field.send_keys(Keys.RETURN)
                time.sleep(3)
                
                # Check if that worked
                current_url = self.driver.current_url
                if "login" not in current_url.lower():
                    self.logger.log_success("✅ Form submitted successfully with Enter key")
                    return True
                
                # If that didn't work, try JavaScript form submission
                self.logger.log_info("🔄 Trying JavaScript form submission")
                self.driver.execute_script("arguments[0].form.submit();", password_field)
                time.sleep(5)
                
            except Exception as e:
                self.logger.log_warning(f"Form submission failed, trying button click: {e}")
                # Fallback to button click
                submit_button.click()
                time.sleep(5)
            
            # Check if login was successful
            current_url = self.driver.current_url
            self.logger.log_info(f"📍 URL after login: {current_url}")
            
            if "login" not in current_url.lower() and "signin" not in current_url.lower():
                self.logger.log_success("✅ Traditional login successful!")
                return True
            else:
                self.logger.log_error("❌ Traditional login failed - still on login page")
                return False
                
        except Exception as e:
            self.logger.log_error(f"Traditional login failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up the driver."""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.log_info("🧹 Stealth driver cleanup complete")
        except Exception as e:
            self.logger.log_error(f"Cleanup error: {e}")