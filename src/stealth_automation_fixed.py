"""
Stealth automation system using undetected-chromedriver and anti-detection techniques.
This system is designed to work in GitHub Actions without manual intervention.
"""

import os
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from .automation_logger import AutomationLogger

logger = AutomationLogger()

class StealthAutomation:
    """Stealth automation system with anti-detection capabilities."""
    
    def __init__(self, headless: bool = True):
        self.driver = None
        self.headless = headless
        self.email = os.getenv('FLIPSIDE_EMAIL')
        self.password = os.getenv('FLIPSIDE_PASSWORD')
        
        if not self.email or not self.password:
            raise ValueError("FLIPSIDE_EMAIL and FLIPSIDE_PASSWORD environment variables are required")
    
    def setup_driver(self) -> bool:
        """Set up undetected Chrome driver with stealth options."""
        try:
            logger.log_info("🤖 Setting up stealth Chrome driver")
            
            # Configure Chrome options for stealth
            options = uc.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless=new')
            
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
            options.add_argument('--window-size=1920,1080')
            
            # User agent
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Create undetected driver
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Execute stealth scripts
            self._apply_stealth_scripts()
            
            logger.log_info("✅ Stealth Chrome driver setup complete")
            return True
            
        except Exception as e:
            logger.log_error(f"Failed to setup stealth driver: {e}")
            return False
    
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
            
            logger.log_info("✅ Stealth scripts applied")
            
        except Exception as e:
            logger.log_warning(f"Failed to apply some stealth scripts: {e}")
    
    def human_like_delay(self, min_delay: float = 0.5, max_delay: float = 2.0):
        """Add human-like delays between actions."""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def human_like_typing(self, element, text: str):
        """Type text in a human-like manner."""
        try:
            element.clear()
            self.human_like_delay(0.1, 0.3)
            
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
            
            self.human_like_delay(0.2, 0.5)
            
        except Exception as e:
            logger.log_error(f"Human-like typing failed: {e}")
            # Fallback to normal typing
            element.clear()
            element.send_keys(text)
    
    def perform_login(self) -> bool:
        """Perform automated login with stealth techniques."""
        try:
            logger.log_info("🔐 Starting stealth login process")
            
            # Navigate to login page
            self.driver.get("https://flipsidecrypto.xyz/chat/")
            self.human_like_delay(2, 4)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Check if we're already logged in
            if self._check_if_logged_in():
                logger.log_info("✅ Already logged in")
                return True
            
            # Find and fill email field
            email_field = self._find_element_with_retry([
                "#email",
                "input[type='email']",
                "input[name='email']",
                "input[placeholder*='email']"
            ])
            
            if not email_field:
                logger.log_error("❌ Could not find email field")
                return False
            
            # Human-like email entry
            logger.log_info("📧 Entering email")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", email_field)
            self.human_like_delay(0.5, 1.0)
            email_field.click()
            self.human_like_delay(0.2, 0.5)
            self.human_like_typing(email_field, self.email)
            
            # Find and fill password field
            password_field = self._find_element_with_retry([
                "#password",
                "input[type='password']",
                "input[name='password']",
                "input[placeholder*='password']"
            ])
            
            if not password_field:
                logger.log_error("❌ Could not find password field")
                return False
            
            # Human-like password entry
            logger.log_info("🔑 Entering password")
            self.human_like_delay(0.5, 1.0)
            password_field.click()
            self.human_like_delay(0.2, 0.5)
            self.human_like_typing(password_field, self.password)
            
            # Find and click login button
            login_button = self._find_element_with_retry([
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Login')",
                "button:contains('Sign In')"
            ])
            
            if login_button:
                logger.log_info("🖱️ Clicking login button")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
                self.human_like_delay(0.5, 1.0)
                login_button.click()
            else:
                # Try pressing Enter
                logger.log_info("⌨️ Submitting with Enter key")
                password_field.send_keys(Keys.RETURN)
            
            # Wait for login to complete
            logger.log_info("⏳ Waiting for login to complete")
            self.human_like_delay(3, 5)
            
            # Wait for redirect
            max_wait = 20
            for i in range(max_wait):
                current_url = self.driver.current_url
                if 'login' not in current_url.lower() and 'signin' not in current_url.lower():
                    logger.log_info(f"✅ Redirected to: {current_url}")
                    break
                time.sleep(1)
            
            # Final validation
            if self._check_if_logged_in():
                logger.log_info("✅ Login successful")
                return True
            else:
                logger.log_error("❌ Login failed - not authenticated")
                return False
                
        except Exception as e:
            logger.log_error(f"Login process failed: {e}")
            return False
    
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
                self.human_like_delay(1, 2)
        
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
            logger.log_debug(f"Login check failed: {e}")
            return False
    
    def submit_prompt(self, prompt: str) -> bool:
        """Submit a prompt to the chat interface."""
        try:
            logger.log_info(f"📝 Submitting prompt: {prompt[:50]}...")
            
            # Find chat input
            chat_input = self._find_element_with_retry([
                "textarea[placeholder*='Ask FlipsideAI']",
                "textarea[placeholder*='message']",
                "textarea[data-testid='chat-input']"
            ])
            
            if not chat_input:
                # Try to find any textarea
                textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                for textarea in textareas:
                    if textarea.is_displayed():
                        chat_input = textarea
                        break
            
            if not chat_input:
                logger.log_error("❌ Could not find chat input")
                return False
            
            # Clear and type prompt
            chat_input.clear()
            self.human_like_delay(0.5, 1.0)
            self.human_like_typing(chat_input, prompt)
            
            # Submit prompt
            chat_input.send_keys(Keys.RETURN)
            logger.log_info("✅ Prompt submitted")
            
            return True
            
        except Exception as e:
            logger.log_error(f"Failed to submit prompt: {e}")
            return False
    
    def wait_for_response(self, timeout: int = 300) -> bool:
        """Wait for AI response by monitoring chat input state."""
        try:
            logger.log_info(f"⏳ Waiting for AI response (timeout: {timeout}s)")
            
            start_time = time.time()
            last_response_length = 0
            response_started = False
            chat_input_was_disabled = False
            
            while time.time() - start_time < timeout:
                # First, check if response has started by looking for new content
                if not response_started:
                    try:
                        # Look for any new messages or responses
                        response_indicators = [
                            "[data-testid='message']",
                            ".message",
                            ".response",
                            ".ai-response",
                            ".chat-message"
                        ]
                        
                        for selector in response_indicators:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            if elements and len(elements) > 1:  # More than just our prompt
                                response_started = True
                                logger.log_info("📝 AI response started")
                                break
                    except:
                        pass
                
                # If response has started, monitor its progress
                if response_started:
                    try:
                        # Check if response is still growing
                        current_length = 0
                        for selector in response_indicators:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            current_length += sum(len(el.text) for el in elements)
                        
                        if current_length > last_response_length:
                            last_response_length = current_length
                            logger.log_info(f"📊 Response growing: {current_length} characters")
                        
                        # Check if chat input is editable again (indicates response is complete)
                        # Re-find the element each time to avoid stale element reference
                        try:
                            chat_input = self._find_chat_input()
                            if chat_input:
                                is_enabled = chat_input.is_enabled()
                                is_displayed = chat_input.is_displayed()
                                
                                # Track if chat input was disabled (AI working)
                                if not is_enabled:
                                    chat_input_was_disabled = True
                                    logger.log_info("🔒 Chat input is disabled - AI is working")
                                
                                # If chat input was disabled and is now enabled, response is complete
                                if chat_input_was_disabled and is_enabled and is_displayed:
                                    logger.log_info("✅ Chat input became editable again - response complete!")
                                    return True
                                
                                # Log current state for debugging
                                logger.log_info(f"Chat input state: enabled={is_enabled}, displayed={is_displayed}, was_disabled={chat_input_was_disabled}")
                            else:
                                logger.log_debug("Chat input not found")
                        except Exception as stale_error:
                            # Handle stale element reference by continuing the loop
                            logger.log_debug(f"Stale element reference, continuing: {stale_error}")
                            continue
                            
                    except Exception as e:
                        logger.log_debug(f"Error checking response progress: {e}")
                
                # Fallback: if response hasn't grown in 15 seconds, assume it's complete
                if response_started and time.time() - start_time > 15 and current_length == last_response_length:
                    logger.log_info("✅ Response appears complete (no growth detected)")
                    return True
                
                # Additional fallback: if we've been waiting for 2 minutes and have substantial content, assume complete
                if response_started and time.time() - start_time > 120 and current_length > 1000:
                    logger.log_info("✅ Response appears complete (substantial content after 2 minutes)")
                    return True
                
                time.sleep(2)
            
            logger.log_warning(f"⚠️ Response timeout after {timeout} seconds")
            return False
            
        except Exception as e:
            logger.log_error(f"Error waiting for response: {e}")
            return False
    
    def _find_chat_input(self):
        """Find the chat input element."""
        try:
            chat_selectors = [
                "textarea[placeholder*='Ask FlipsideAI']",
                "textarea[placeholder*='message']",
                "textarea[data-testid='chat-input']",
                "textarea"
            ]
            
            for selector in chat_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element and element.is_displayed():
                        return element
                except:
                    continue
            
            return None
        except:
            return None
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if self.driver:
                self.driver.quit()
                logger.log_info("✅ Driver cleanup complete")
        except Exception as e:
            logger.log_warning(f"Cleanup warning: {e}")
