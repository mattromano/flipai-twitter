"""
Flipside Chat Automation Manager

Handles the core automation logic for Flipside AI chat interactions.
"""

import os
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from modules.shared.authentication import StealthAuthenticator
from modules.shared.logger import AutomationLogger
from modules.chat_manager.data_extractor import DataExtractor
from modules.chat_manager.artifact_capture import ArtifactCapture


class FlipsideChatManager:
    """Manages Flipside AI chat automation workflow."""
    
    def __init__(self, use_stealth_auth: bool = True):
        self.driver: Optional[webdriver.Chrome] = None
        self.authenticator: Optional[StealthAuthenticator] = None
        self.data_extractor: DataExtractor = DataExtractor()
        self.artifact_capture: ArtifactCapture = ArtifactCapture()
        self.logger: AutomationLogger = AutomationLogger()
        self.use_stealth_auth = use_stealth_auth
        
        # Setup directories
        os.makedirs("screenshots", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
    
    def initialize(self) -> bool:
        """Initialize the automation environment."""
        try:
            self.logger.log_info("🚀 Initializing Flipside chat automation")
            
            if self.use_stealth_auth:
                self.authenticator = StealthAuthenticator()
                self.driver = self.authenticator.setup_driver()
            else:
                self.driver = self._setup_standard_driver()
            
            if not self.driver:
                self.logger.log_error("Failed to initialize WebDriver")
                return False
            
            self.logger.log_success("✅ Automation environment initialized")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Initialization failed: {e}")
            return False
    
    def authenticate(self) -> bool:
        """Authenticate with Flipside."""
        try:
            self.logger.log_info("🔐 Starting authentication")
            
            if self.use_stealth_auth and self.authenticator:
                success = self.authenticator.login()
                if success:
                    self.logger.log_success("✅ Stealth authentication successful")
                    return True
                else:
                    self.logger.log_error("❌ Stealth authentication failed")
                    return False
            else:
                # Fallback to standard authentication
                return self._standard_authentication()
                
        except Exception as e:
            self.logger.log_error(f"Authentication failed: {e}")
            return False
    
    def navigate_to_chat(self) -> bool:
        """Navigate to the Flipside chat page."""
        try:
            self.logger.log_info("🧭 Navigating to chat page")
            
            chat_url = "https://flipsidecrypto.xyz/chat/"
            self.driver.get(chat_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Take screenshot
            screenshot_path = f"screenshots/chat_page_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(screenshot_path)
            self.logger.log_info(f"📸 Screenshot saved: {screenshot_path}")
            
            self.logger.log_success("✅ Successfully navigated to chat page")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Navigation failed: {e}")
            return False
    
    def submit_prompt(self, prompt: str) -> bool:
        """Submit a prompt to the chat."""
        try:
            self.logger.log_info(f"📝 Submitting prompt: {prompt[:50]}...")
            
            # Find chat input
            chat_selectors = [
                "textarea[placeholder*='Ask FlipsideAI']",
                "textarea[placeholder*='message']",
                "textarea[data-testid='chat-input']",
                "textarea"
            ]
            
            chat_input = None
            for selector in chat_selectors:
                try:
                    chat_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if chat_input and chat_input.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            if not chat_input:
                self.logger.log_error("❌ Chat input not found")
                return False
            
            # Clear and type prompt
            chat_input.clear()
            chat_input.send_keys(prompt)
            
            # Submit (usually Enter key or submit button)
            chat_input.send_keys("\n")
            
            self.logger.log_success("✅ Prompt submitted successfully")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Prompt submission failed: {e}")
            return False
    
    def wait_for_response(self, timeout: int = 600) -> bool:
        """Wait for AI response to complete."""
        try:
            self.logger.log_info(f"⏳ Waiting for AI response (timeout: {timeout}s)")
            
            start_time = time.time()
            response_started = False
            chat_input_was_disabled = False
            
            while time.time() - start_time < timeout:
                try:
                    # Check if response has started
                    if not response_started:
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
                                self.logger.log_info("📝 AI response started")
                                break
                    
                    # Check chat input state
                    if response_started:
                        chat_input = self._find_chat_input()
                        if chat_input:
                            is_enabled = chat_input.is_enabled()
                            is_displayed = chat_input.is_displayed()
                            
                            # Track if chat input was disabled (AI working)
                            if not is_enabled:
                                chat_input_was_disabled = True
                                self.logger.log_info("🔒 Chat input disabled - AI is working")
                            
                            # If chat input was disabled and is now enabled, response is complete
                            if chat_input_was_disabled and is_enabled and is_displayed:
                                self.logger.log_success("✅ Chat input enabled - response complete!")
                                return True
                    
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.log_debug(f"Error checking response: {e}")
                    time.sleep(2)
            
            self.logger.log_warning(f"⚠️ Response timeout after {timeout} seconds")
            return False
            
        except Exception as e:
            self.logger.log_error(f"Error waiting for response: {e}")
            return False
    
    def extract_data(self) -> Dict[str, Any]:
        """Extract all data from the chat response."""
        try:
            self.logger.log_info("📊 Extracting chat data")
            
            # Extract text data
            text_data = self.data_extractor.extract_text_data(self.driver)
            
            # Extract artifacts
            artifacts = self.artifact_capture.capture_artifacts(self.driver)
            
            # Combine results
            results = {
                "timestamp": datetime.now().isoformat(),
                "chat_url": self.driver.current_url,
                "response_text": text_data.get("response_text", ""),
                "twitter_text": text_data.get("twitter_text", ""),
                "artifacts": artifacts,
                "screenshots": [],
                "response_metadata": {
                    "response_length": len(text_data.get("response_text", "")),
                    "artifacts_count": len(artifacts)
                }
            }
            
            self.logger.log_success(f"✅ Data extracted: {results['response_metadata']['response_length']} chars, {results['response_metadata']['artifacts_count']} artifacts")
            return results
            
        except Exception as e:
            self.logger.log_error(f"Data extraction failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "chat_url": self.driver.current_url if self.driver else "",
                "response_text": "",
                "twitter_text": "",
                "artifacts": [],
                "screenshots": [],
                "response_metadata": {"error": str(e)}
            }
    
    def capture_final_screenshot(self) -> str:
        """Capture final screenshot of the chat."""
        try:
            screenshot_path = f"screenshots/final_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(screenshot_path)
            self.logger.log_info(f"📸 Final screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            self.logger.log_error(f"Failed to capture final screenshot: {e}")
            return ""
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if self.authenticator:
                self.authenticator.cleanup()
            elif self.driver:
                self.driver.quit()
            self.logger.log_info("🧹 Cleanup completed")
        except Exception as e:
            self.logger.log_error(f"Cleanup error: {e}")
    
    def _setup_standard_driver(self) -> Optional[webdriver.Chrome]:
        """Setup standard Chrome driver."""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            self.logger.log_error(f"Failed to setup standard driver: {e}")
            return None
    
    def _standard_authentication(self) -> bool:
        """Standard authentication fallback."""
        # This would implement cookie-based authentication
        # For now, return True as placeholder
        self.logger.log_info("Using standard authentication (placeholder)")
        return True
    
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
                except NoSuchElementException:
                    continue
            
            return None
        except Exception:
            return None
