import os
import sys
import time
import subprocess
import re
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
            version_output = None
            
            # Platform-specific Chrome paths
            if os.name == 'nt':  # Windows
                chrome_paths = [
                    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                ]
            elif sys.platform == 'darwin':  # macOS
                chrome_paths = [
                    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                    '/Applications/Chromium.app/Contents/MacOS/Chromium',
                ]
            else:  # Linux
                chrome_paths = [
                    '/usr/bin/google-chrome',
                    '/usr/bin/google-chrome-stable',
                    '/usr/bin/chromium-browser',
                    '/usr/bin/chromium',
                    '/snap/bin/chromium',
                ]
            
            # Try absolute paths first
            for path in chrome_paths:
                try:
                    if os.path.exists(path):
                        result = subprocess.run(
                            [path, '--version'],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode == 0:
                            version_output = result.stdout.strip()
                            self.logger.log_info(f"Found Chrome at: {path}")
                            break
                except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError, OSError) as e:
                    continue
            
            # If no absolute path worked, try common commands (works if in PATH)
            if not version_output:
                for cmd in ['google-chrome', 'google-chrome-stable', 'chromium-browser', 'chromium']:
                    try:
                        result = subprocess.run(
                            [cmd, '--version'],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode == 0:
                            version_output = result.stdout.strip()
                            self.logger.log_info(f"Found Chrome via command: {cmd}")
                            break
                    except (FileNotFoundError, PermissionError, OSError):
                        continue
            
            # Extract version number from output
            if version_output:
                # Format examples:
                # "Google Chrome 140.0.7339.207"
                # "Chromium 140.0.7339.207"
                # "Google Chrome 141.0.7390.123"
                version_match = re.search(r'(\d+)\.\d+\.\d+\.\d+', version_output)
                if version_match:
                    major_version = int(version_match.group(1))
                    self.logger.log_info(f"✅ Detected Chrome version: {major_version} (from: {version_output})")
                    return major_version
                
                # Try alternative pattern (just major.minor)
                version_match = re.search(r'(\d+)\.\d+', version_output)
                if version_match:
                    major_version = int(version_match.group(1))
                    self.logger.log_info(f"✅ Detected Chrome version: {major_version} (from: {version_output})")
                    return major_version
            
            self.logger.log_warning("⚠️ Could not detect Chrome version automatically")
            return None
            
        except Exception as e:
            self.logger.log_warning(f"Chrome version detection failed: {e}")
            return None
    
    def setup_driver(self):
        """Setup stealth Chrome driver with anti-detection capabilities."""
        try:
            self.logger.log_info("🤖 Setting up stealth Chrome driver")
            
            import undetected_chromedriver as uc
            
            # Detect Chrome version first
            chrome_version = self._detect_chrome_version()
            
            # Configure Chrome options for stealth
            options = uc.ChromeOptions()
            
            # Check if running in headless mode from environment
            headless_mode = os.getenv('CHROME_HEADLESS', 'false').lower() == 'true'
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
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-features=VizDisplayCompositor')
            
            # Window size for consistent screenshots
            window_size = os.getenv('CHROME_WINDOW_SIZE', '1920,1080')
            options.add_argument(f'--window-size={window_size}')
            
            # User agent - update to match detected Chrome version
            if chrome_version:
                user_agent = f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36'
            else:
                user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
            options.add_argument(f'--user-agent={user_agent}')
            
            # Clear cache before creating driver to avoid version mismatches
            try:
                import shutil
                cache_dir = os.path.expanduser('~/.undetected_chromedriver')
                if os.path.exists(cache_dir):
                    self.logger.log_info("Clearing undetected-chromedriver cache to ensure correct version...")
                    shutil.rmtree(cache_dir)
                    self.logger.log_info("✅ Cache cleared")
            except Exception as cache_error:
                self.logger.log_warning(f"Could not clear cache (may not exist): {cache_error}")
            
            # Create undetected driver with explicit version if detected
            # This ensures ChromeDriver version matches the installed Chrome version
            if chrome_version:
                self.logger.log_info(f"Using Chrome version {chrome_version} for ChromeDriver")
                self.driver = uc.Chrome(options=options, version_main=chrome_version)
            else:
                self.logger.log_info("Auto-detecting Chrome version for ChromeDriver")
                self.driver = uc.Chrome(options=options, version_main=None)
            
            # Execute stealth scripts
            self._apply_stealth_scripts()
            
            self.logger.log_success("✅ Stealth Chrome driver setup complete")
            return self.driver
            
        except Exception as e:
            self.logger.log_error(f"Stealth driver setup failed: {e}")
            # Try fallback with no version specified
            try:
                self.logger.log_info("Attempting fallback with auto-detection...")
                import undetected_chromedriver as uc
                options = uc.ChromeOptions()
                if os.getenv('CHROME_HEADLESS', 'false').lower() == 'true':
                    options.add_argument('--headless=new')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                self.driver = uc.Chrome(options=options)
                self._apply_stealth_scripts()
                self.logger.log_success("✅ Fallback driver setup successful")
                return self.driver
            except Exception as fallback_error:
                self.logger.log_error(f"Fallback driver setup also failed: {fallback_error}")
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
            
            # Navigate directly to chat page (as in original working code)
            self.driver.get("https://flipsidecrypto.xyz/chat/")
            self._human_like_delay(2, 4)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if we're already logged in
            if self._check_if_logged_in():
                self.logger.log_info("✅ Already logged in")
                return True
            
            # Find and fill email field
            email_field = self._find_element_with_retry([
                "#email",
                "input[type='email']",
                "input[name='email']",
                "input[placeholder*='email']"
            ])
            
            if not email_field:
                self.logger.log_error("❌ Could not find email field")
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
            
            # Wait for redirect
            max_wait = 20
            for i in range(max_wait):
                current_url = self.driver.current_url
                if 'login' not in current_url.lower() and 'signin' not in current_url.lower():
                    self.logger.log_info(f"✅ Redirected to: {current_url}")
                    break
                time.sleep(1)
            
            # Final validation
            if self._check_if_logged_in():
                self.logger.log_info("✅ Login successful")
                return True
            else:
                self.logger.log_error("❌ Login failed - not authenticated")
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
                        element = self.driver.find_element(By.XPATH, xpath)
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if element and element.is_displayed():
                        return element
                except:
                    continue
            
            if attempt < max_attempts - 1:
                self._human_like_delay(1, 2)
        
        return None
    
    def _check_if_logged_in(self) -> bool:
        """Check if user is logged in."""
        try:
            current_url = self.driver.current_url
            
            # Check URL
            if 'login' in current_url.lower() or 'signin' in current_url.lower():
                return False
            
            # Check for chat input
            chat_indicators = [
                "textarea[placeholder*='Ask FlipsideAI']",
                "textarea[placeholder*='message']",
                "textarea[data-testid='chat-input']"
            ]
            
            for selector in chat_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element and element.is_displayed():
                        return True
                except:
                    continue
            
            # Check for any textarea that might be chat input
            try:
                textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                for textarea in textareas:
                    if textarea.is_displayed():
                        placeholder = textarea.get_attribute("placeholder") or ""
                        if "ask" in placeholder.lower() or "message" in placeholder.lower():
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