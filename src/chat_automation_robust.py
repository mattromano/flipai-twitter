#!/usr/bin/env python3
"""
Robust version of Flipside Chat Automation with proper timeouts and error handling.
"""

import os
import sys
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from .automation_logger import AutomationLogger, AutomationStep, get_automation_logger

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from .session_manager import SessionManager
from .stealth_automation_fixed import StealthAutomation
from .utils import ScreenshotUtils, WaitUtils, TextUtils
from .results_logger import ResultsLogger
from config.prompts import get_prompt_for_today


class RobustFlipsideChatAutomation:
    """Robust automation class with proper timeouts and error handling."""
    
    def __init__(self, use_stealth_auth: bool = True):
        self.driver: Optional[webdriver.Chrome] = None
        self.session_manager: Optional[SessionManager] = None
        self.stealth_automation: Optional[StealthAutomation] = None
        self.results_logger: Optional[ResultsLogger] = None
        self.automation_logger: AutomationLogger = get_automation_logger()
        self.use_stealth_auth = use_stealth_auth
        self.setup_logging()
        self.setup_directories()
        self.results_logger = ResultsLogger()
        
    def setup_logging(self):
        """Set up logging configuration."""
        os.makedirs("logs", exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
    def setup_directories(self):
        """Create necessary directories."""
        os.makedirs("screenshots", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs("tweet_previews", exist_ok=True)
    
    def setup_chrome_driver(self) -> bool:
        """Set up Chrome WebDriver with optimized configuration."""
        try:
            self.automation_logger.log_info("Configuring Chrome WebDriver options")
            chrome_options = Options()
            
            # Headless mode for GitHub Actions
            headless_mode = os.getenv('CHROME_HEADLESS', 'true').lower() == 'true'
            if headless_mode:
                chrome_options.add_argument('--headless')
                self.automation_logger.log_info("Headless mode enabled")
            else:
                self.automation_logger.log_info("Headless mode disabled (visible browser)")
            
            # Window size for consistent screenshots
            window_size = os.getenv('CHROME_WINDOW_SIZE', '1920,1080')
            chrome_options.add_argument(f'--window-size={window_size}')
            self.automation_logger.log_info(f"Window size set to: {window_size}")
            
            # Performance and stability options
            stability_options = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',
                '--disable-javascript',
                '--disable-web-security',
                '--allow-running-insecure-content'
            ]
            
            for option in stability_options:
                chrome_options.add_argument(option)
            
            self.automation_logger.log_info("Applied stability options")
            
            # User agent
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            chrome_options.add_argument(f'--user-agent={user_agent}')
            
            # Logging - enable verbose logging
            chrome_options.add_argument('--enable-logging')
            chrome_options.add_argument('--log-level=0')
            chrome_options.add_argument('--v=1')
            chrome_options.add_argument('--enable-logging=stderr')
            
            # Set up ChromeDriver
            self.automation_logger.log_info("Installing ChromeDriver")
            service = Service(ChromeDriverManager().install())
            
            # Create driver
            self.automation_logger.log_info("Initializing Chrome WebDriver")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            
            self.automation_logger.log_success("Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            self.automation_logger.log_error(f"Failed to setup Chrome WebDriver: {e}")
            return False
    
    def setup_stealth_authentication(self) -> bool:
        """Set up stealth authentication using undetected-chromedriver."""
        try:
            self.automation_logger.log_info("Setting up stealth authentication")
            
            # Check for required credentials
            email = os.getenv('FLIPSIDE_EMAIL')
            password = os.getenv('FLIPSIDE_PASSWORD')
            
            if not email or not password:
                self.automation_logger.log_error("FLIPSIDE_EMAIL and FLIPSIDE_PASSWORD environment variables are required for stealth authentication")
                return False
            
            # Initialize stealth automation
            headless_mode = os.getenv('CHROME_HEADLESS', 'true').lower() == 'true'
            self.stealth_automation = StealthAutomation(headless=headless_mode)
            
            # Setup stealth driver
            if not self.stealth_automation.setup_driver():
                self.automation_logger.log_error("Failed to setup stealth driver")
                return False
            
            # Use the stealth driver as our main driver
            self.driver = self.stealth_automation.driver
            
            # Perform login
            if not self.stealth_automation.perform_login():
                self.automation_logger.log_error("Stealth login failed")
                return False
            
            self.automation_logger.log_success("Stealth authentication completed successfully")
            return True
            
        except Exception as e:
            self.automation_logger.log_error(f"Stealth authentication failed: {e}")
            return False

    def setup_session_with_timeout(self, timeout: int = 60, enable_fallback: bool = True) -> bool:
        """Set up session with timeout and optional login fallback."""
        try:
            # Use stealth authentication if enabled
            if self.use_stealth_auth:
                return self.setup_stealth_authentication()
            
            # Fallback to original session manager approach
            self.automation_logger.log_info("Initializing session manager")
            
            # Initialize session manager
            self.session_manager = SessionManager(self.driver)
            
            if enable_fallback:
                # Use the new fallback-enabled session setup
                self.automation_logger.log_info("Setting up session with login fallback enabled")
                max_login_wait = int(os.getenv('LOGIN_FALLBACK_TIMEOUT', '300'))  # 5 minutes default
                
                if self.session_manager.setup_session_with_fallback("flipside_cookies.txt", max_login_wait):
                    self.automation_logger.log_success("Session setup with fallback completed")
                    return True
                else:
                    self.automation_logger.log_error("Session setup with fallback failed")
                    return False
            else:
                # Use the original method without fallback
                self.automation_logger.log_info("Setting up session without fallback")
                
                # Load cookies from environment with timeout
                self.automation_logger.log_info("Loading cookies from file")
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    try:
                        cookies = self.session_manager.load_cookies_from_file("flipside_cookies.txt")
                        if cookies:
                            self.automation_logger.log_success(f"Loaded {len(cookies)} cookies")
                            break
                        else:
                            self.automation_logger.log_warning("No cookies found, retrying...")
                            time.sleep(2)
                    except Exception as e:
                        self.automation_logger.log_warning(f"Cookie loading error: {e}, retrying...")
                        time.sleep(2)
                else:
                    self.automation_logger.log_error(f"Failed to load cookies within {timeout} seconds")
                    return False
                
                # Apply cookies to driver with timeout
                self.automation_logger.log_info("Applying cookies to browser")
                start_time = time.time()
                
                while time.time() - start_time < timeout:
                    try:
                        if self.session_manager.apply_cookies_to_driver(cookies):
                            self.automation_logger.log_success("Cookies applied successfully")
                            break
                        else:
                            self.automation_logger.log_warning("Failed to apply cookies, retrying...")
                            time.sleep(2)
                    except Exception as e:
                        self.automation_logger.log_warning(f"Cookie application error: {e}, retrying...")
                        time.sleep(2)
                else:
                    self.automation_logger.log_error(f"Failed to apply cookies within {timeout} seconds")
                    return False
                
                # Wait for cookies to be processed
                time.sleep(3)
                
                self.automation_logger.log_success("Session setup completed")
                return True
            
        except Exception as e:
            self.automation_logger.log_error(f"Failed to setup session: {e}")
            return False
    
    def navigate_to_chat_with_timeout(self, timeout: int = 60) -> bool:
        """Navigate to chat page with timeout."""
        try:
            self.automation_logger.log_info("Navigating to Flipside chat page")
            
            # Navigate to chat page
            self.driver.get("https://flipsidecrypto.xyz/chat/")
            
            # Wait for page to load with timeout
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # Check if page loaded
                    if "chat" in self.driver.current_url.lower():
                        self.automation_logger.log_success("Successfully navigated to chat page")
                        
                        # Wait for page elements to load
                        time.sleep(5)
                        
                        # Take screenshot for debugging
                        self.driver.save_screenshot("debug_chat_page.png")
                        self.automation_logger.log_screenshot("debug_chat_page.png", "Chat page loaded")
                        
                        return True
                    else:
                        self.automation_logger.log_warning(f"Not on chat page yet: {self.driver.current_url}")
                        time.sleep(2)
                except Exception as e:
                    self.automation_logger.log_warning(f"Navigation error: {e}, retrying...")
                    time.sleep(2)
            else:
                self.automation_logger.log_error(f"Failed to navigate to chat page within {timeout} seconds")
                return False
                
        except Exception as e:
            self.automation_logger.log_error(f"Failed to navigate to chat: {e}")
            return False
    
    def submit_prompt_with_timeout(self, prompt: str, timeout: int = 60) -> bool:
        """Submit prompt with timeout."""
        try:
            # Use stealth automation if available
            if self.stealth_automation:
                self.automation_logger.log_info(f"Submitting prompt via stealth automation: {prompt[:50]}...")
                return self.stealth_automation.submit_prompt(prompt)
            
            # Fallback to original method
            self.automation_logger.log_info(f"Submitting prompt: {prompt[:50]}...")
            
            # Find input field with timeout
            start_time = time.time()
            input_element = None
            
            input_selectors = [
                "textarea[placeholder*='Ask FlipsideAI']",
                "textarea",
                "textarea[placeholder*='message']",
                "textarea[data-testid='chat-input']",
                ".chat-input textarea",
                "input[type='text']"
            ]
            
            while time.time() - start_time < timeout:
                for selector in input_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                input_element = element
                                self.automation_logger.log_success(f"Found input field: {selector}")
                                break
                        if input_element:
                            break
                    except:
                        continue
                
                if input_element:
                    break
                else:
                    self.automation_logger.log_warning("Input field not found, retrying...")
                    time.sleep(2)
            else:
                self.automation_logger.log_error(f"Failed to find input field within {timeout} seconds")
                return False
            
            # Clear and type prompt
            input_element.clear()
            input_element.send_keys(prompt)
            self.automation_logger.log_success("Prompt typed successfully")
            
            # Find and click submit button
            submit_selectors = [
                "button[type='submit']",
                "button",
                "input[type='submit']",
                "[data-testid='submit']",
                ".submit-button"
            ]
            
            submit_element = None
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                for selector in submit_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                submit_element = element
                                self.automation_logger.log_success(f"Found submit button: {selector}")
                                break
                        if submit_element:
                            break
                    except:
                        continue
                
                if submit_element:
                    break
                else:
                    self.automation_logger.log_warning("Submit button not found, retrying...")
                    time.sleep(2)
            else:
                self.automation_logger.log_error(f"Failed to find submit button within {timeout} seconds")
                return False
            
            # Click submit button
            submit_element.click()
            self.automation_logger.log_success("Prompt submitted successfully")
            
            return True
            
        except Exception as e:
            self.automation_logger.log_error(f"Failed to submit prompt: {e}")
            return False
    
    def wait_for_complete_response_with_timeout(self, timeout: int = 300) -> bool:
        """Wait for complete AI response including charts and visualizations (5 minutes max)."""
        try:
            # Use stealth automation if available
            if self.stealth_automation:
                self.automation_logger.log_info(f"Waiting for response via stealth automation (timeout: {timeout}s)")
                return self.stealth_automation.wait_for_response(timeout)
            
            # Fallback to original method with improved chat input monitoring
            self.automation_logger.log_info(f"Waiting for complete AI response (timeout: {timeout}s)...")
            
            start_time = time.time()
            response_complete = False
            capture_after_3min = False
            response_started = False
            
            while time.time() - start_time < timeout:
                try:
                    # Look for Twitter text output (indicates response started)
                    twitter_selectors = [
                        "[data-testid='twitter-text']",
                        ".twitter-text",
                        ".twitter-output",
                        "div:contains('TWITTER_TEXT')",
                        "div:contains('Twitter')"
                    ]
                    
                    twitter_found = False
                    for selector in twitter_selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                if element.is_displayed() and element.text.strip():
                                    twitter_found = True
                                    self.automation_logger.log_success("Twitter text output found")
                                    break
                            if twitter_found:
                                break
                        except:
                            continue
                    
                    # Look for charts/visualizations on the right panel
                    chart_selectors = [
                        ".chart-container",
                        ".visualization-panel",
                        ".report-panel",
                        "[data-testid='chart']",
                        "canvas",
                        "svg",
                        ".highcharts-container"
                    ]
                    
                    charts_found = False
                    for selector in chart_selectors:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                if element.is_displayed() and element.size['width'] > 100 and element.size['height'] > 100:
                                    charts_found = True
                                    self.automation_logger.log_success("Charts/visualizations found")
                                    break
                            if charts_found:
                                break
                        except:
                            continue
                    
                    # Check if we need to click "View Report" button to show visuals
                    view_report_selectors = [
                        # Most specific selectors first (using XPath instead of CSS)
                        "//button[contains(text(), 'View Report')]",
                        "//button[contains(text(), 'view report')]",
                        "//a[contains(text(), 'View Report')]",
                        "//a[contains(text(), 'view report')]",
                        # Data testid selectors
                        "[data-testid='view-report']",
                        "[data-testid='View Report']",
                        "[data-testid='view_report']",
                        # Class-based selectors
                        ".view-report-button",
                        ".artifact-link",
                        ".report-link",
                        "button[class*='view']",
                        "button[class*='report']",
                        "a[class*='view']",
                        "a[class*='report']",
                        # Generic link selectors
                        "a[href*='report']",
                        "a[href*='view']",
                        # Fallback selectors
                        "button",
                        "a"
                    ]
                    
                    for selector in view_report_selectors:
                        try:
                            # Use XPath for selectors starting with //
                            if selector.startswith('//'):
                                elements = self.driver.find_elements(By.XPATH, selector)
                            else:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                if element.is_displayed() and element.is_enabled():
                                    element_text = element.text.lower().strip()
                                    element_href = (element.get_attribute('href') or '').lower()
                                    
                                    # Check if it's a view report button/link
                                    if ('view report' in element_text or 
                                        'view' in element_text or 
                                        'report' in element_text or
                                        'view' in element_href or
                                        'report' in element_href or
                                        'view' in selector.lower() or
                                        'report' in selector.lower()):
                                        self.automation_logger.log_info(f"Clicking 'View Report' button: {selector} - Text: '{element_text}'")
                                        try:
                                            # Scroll to element to ensure it's clickable
                                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                            time.sleep(1)
                                            element.click()
                                            time.sleep(8)  # Wait longer for report to load
                                            self.automation_logger.log_success("View Report button clicked - visuals should now be visible")
                                            break
                                        except Exception as e:
                                            self.automation_logger.log_warning(f"Failed to click View Report button: {e}")
                                            continue
                        except Exception as e:
                            self.automation_logger.log_warning(f"Error checking View Report selector {selector}: {e}")
                            continue
                    
                    # Check if we should capture results after 3 minutes
                    elapsed = int(time.time() - start_time)
                    if elapsed >= 180 and not capture_after_3min:  # 3 minutes
                        self.automation_logger.log_info("3 minutes elapsed - will capture results regardless of completion")
                        capture_after_3min = True
                    
                    # Check if chat input is editable again (indicates response is complete)
                    chat_input_editable = False
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
                                if element and element.is_displayed() and element.is_enabled():
                                    chat_input_editable = True
                                    break
                            except Exception as stale_error:
                                # Handle stale element reference
                                if "stale element" in str(stale_error).lower():
                                    continue
                                else:
                                    continue
                    except Exception as e:
                        # Handle any other errors
                        if "stale element" in str(e).lower():
                            pass
                        else:
                            pass
                    
                    # Response is complete if chat input is editable again
                    if chat_input_editable and (twitter_found or charts_found):
                        self.automation_logger.log_success("Chat input is editable - response complete!")
                        response_complete = True
                        break
                    # Fallback: Response is complete if we have both Twitter text and charts
                    elif twitter_found and charts_found:
                        self.automation_logger.log_success("Complete response received with charts")
                        response_complete = True
                        break
                    elif twitter_found:
                        # We have text but waiting for charts
                        self.automation_logger.log_info(f"Text received, waiting for charts... ({elapsed}s elapsed)")
                        time.sleep(5)
                    else:
                        # Still waiting for any response
                        self.automation_logger.log_info(f"Waiting for response... ({elapsed}s elapsed)")
                        time.sleep(5)
                        
                except Exception as e:
                    self.automation_logger.log_warning(f"Error checking for response: {e}")
                    time.sleep(5)
            
            # If we exit the while loop due to timeout
            if not response_complete:
                self.automation_logger.log_warning(f"Complete response not received within {timeout} seconds")
                if capture_after_3min:
                    self.automation_logger.log_info("Proceeding with partial results capture")
                return False
            
            return True
            
        except Exception as e:
            self.automation_logger.log_error(f"Failed to wait for complete response: {e}")
            return False
    
    def close_artifact_view(self) -> bool:
        """Close the artifact view by clicking the X button to reveal the share button."""
        try:
            self.automation_logger.log_info("Looking for artifact view close button...")
            
            # Look for the X button in the upper right corner to close artifact view
            close_selectors = [
                # More specific selectors first
                "button[aria-label*='Close']",
                "button[title*='Close']",
                "button[aria-label*='close']",
                "button[title*='close']",
                "[data-testid*='close']",
                "[data-testid*='Close']",
                # Icon-based selectors
                "button svg[data-testid*='close']",
                "button svg[data-testid*='Close']",
                "button[class*='close']",
                "button[class*='Close']",
                # Text-based selectors (using XPath instead of CSS)
                "//button[contains(text(), '×')]",
                "//button[contains(text(), '✕')]",
                "//button[contains(text(), 'X')]",
                "//button[contains(text(), 'close')]",
                "//button[contains(text(), 'Close')]",
                # Class-based selectors
                ".close-button",
                ".artifact-close",
                ".view-close",
                ".modal-close",
                ".panel-close",
                ".header-close",
                ".toolbar-close",
                # Generic button selectors in specific areas
                ".header button",
                ".toolbar button",
                ".modal-header button",
                ".panel-header button",
                # Fallback to any button in upper right area
                "button"
            ]
            
            close_button = None
            for selector in close_selectors:
                try:
                    # Use XPath for selectors starting with //
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.automation_logger.log_info(f"Checking {len(elements)} close elements with selector: {selector}")
                    
                    for i, element in enumerate(elements):
                        if element.is_displayed() and element.is_enabled():
                            # Check if it's in the upper right area (likely the artifact close button)
                            location = element.location
                            size = self.driver.get_window_size()
                            element_text = element.text.lower().strip()
                            element_title = (element.get_attribute('title') or '').lower()
                            element_aria_label = (element.get_attribute('aria-label') or '').lower()
                            element_class = (element.get_attribute('class') or '').lower()
                            
                            self.automation_logger.log_info(f"Close element {i}: text='{element_text}', title='{element_title}', aria-label='{element_aria_label}', class='{element_class}', location=({location['x']}, {location['y']})")
                            
                            # Check if it's in the upper right area (more lenient)
                            if location['x'] > size['width'] * 0.5 and location['y'] < size['height'] * 0.4:
                                # Check for close-related content or X symbols
                                if ('close' in element_text or 
                                    'close' in element_title or
                                    'close' in element_aria_label or
                                    'close' in element_class or
                                    '×' in element_text or
                                    '✕' in element_text or
                                    'x' in element_text or
                                    'close' in selector.lower()):
                                    close_button = element
                                    self.automation_logger.log_success(f"Found artifact close button: {selector} - Element {i}")
                                    break
                                # If it's in the very upper right corner, it might be the close button
                                elif location['x'] > size['width'] * 0.8 and location['y'] < size['height'] * 0.2:
                                    close_button = element
                                    self.automation_logger.log_success(f"Found potential close button by position: {selector} - Element {i}")
                                    break
                    if close_button:
                        break
                except Exception as e:
                    self.automation_logger.log_warning(f"Error checking close selector {selector}: {e}")
                    continue
            
            if close_button:
                try:
                    # Scroll to element to ensure it's clickable
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
                    time.sleep(1)
                    close_button.click()
                    time.sleep(3)  # Wait longer for artifact view to close
                    self.automation_logger.log_success("Artifact view closed successfully")
                    return True
                except Exception as e:
                    self.automation_logger.log_warning(f"Failed to click close button: {e}")
                    return False
            else:
                self.automation_logger.log_info("No artifact view found or already closed")
                return True  # Not an error if no artifact view is open
                
        except Exception as e:
            self.automation_logger.log_warning(f"Failed to close artifact view: {e}")
            return True  # Continue even if this fails

    def extract_shareable_link(self) -> str:
        """Extract the shareable link by clicking Share -> Public -> Copy URL."""
        try:
            self.automation_logger.log_info("Extracting shareable link...")
            
            # First, try to close any open artifact view to reveal the share button
            self.close_artifact_view()
            
            # Look for Share button in the upper right corner of the chat window
            share_selectors = [
                # Most specific selectors first
                "button[aria-label*='Share']",
                "button[title*='Share']",
                "button[data-testid*='share']",
                "button[data-testid*='Share']",
                # Text-based selectors (using XPath instead of CSS)
                "//button[contains(text(), 'Share')]",
                "//button[contains(text(), 'share')]",
                # Class-based selectors
                ".share-button",
                "button[class*='share']",
                "button[class*='Share']",
                # Icon-based selectors
                "button svg[data-testid*='share']",
                "button svg[data-testid*='Share']",
                # Header/toolbar selectors
                ".header button",
                ".chat-header button",
                ".top-bar button",
                ".toolbar button",
                ".action-button",
                # Generic button selectors
                "button[class*='icon']",
                "button[role='button']",
                # Fallback selectors
                "button",
                "[role='button']"
            ]
            
            share_button = None
            for selector in share_selectors:
                try:
                    # Use XPath for selectors starting with //
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.automation_logger.log_info(f"Checking {len(elements)} elements with selector: {selector}")
                    
                    for i, element in enumerate(elements):
                        if element.is_displayed() and element.is_enabled():
                            # Get element properties for debugging
                            location = element.location
                            size = self.driver.get_window_size()
                            element_text = element.text.lower().strip()
                            element_title = (element.get_attribute('title') or '').lower()
                            element_aria_label = (element.get_attribute('aria-label') or '').lower()
                            element_class = (element.get_attribute('class') or '').lower()
                            element_data_testid = (element.get_attribute('data-testid') or '').lower()
                            
                            self.automation_logger.log_info(f"Element {i}: text='{element_text}', title='{element_title}', aria-label='{element_aria_label}', class='{element_class}', data-testid='{element_data_testid}', location=({location['x']}, {location['y']})")
                            
                            # Check if it's in the upper right area (more lenient)
                            if location['x'] > size['width'] * 0.3 and location['y'] < size['height'] * 0.5:
                                # Check for share-related content
                                if ('share' in element_text or 
                                    'share' in element_title or 
                                    'share' in element_aria_label or
                                    'share' in element_class or
                                    'share' in element_data_testid or
                                    'share' in selector.lower()):
                                    share_button = element
                                    self.automation_logger.log_success(f"Found Share button: {selector} - Element {i}")
                                    break
                                # If it's in the very upper right corner, it might be the share button
                                elif location['x'] > size['width'] * 0.7 and location['y'] < size['height'] * 0.3:
                                    # Check if it's the only button in that area or has icon-like properties
                                    if (element.size['width'] < 100 and element.size['height'] < 100) or 'icon' in element_class:
                                        share_button = element
                                        self.automation_logger.log_success(f"Found potential Share button by position and size: {selector} - Element {i}")
                                        break
                    if share_button:
                        break
                except Exception as e:
                    self.automation_logger.log_warning(f"Error checking selector {selector}: {e}")
                    continue
            
            if not share_button:
                self.automation_logger.log_warning("Share button not found")
                self._capture_warning_screenshot("share_button_not_found")
                return ""
            
            # Click Share button
            share_button.click()
            time.sleep(3)  # Wait longer for modal to appear
            
            # Look for Public option in modal
            public_selectors = [
                "input[type='radio'][value='public']",
                "input[type='radio']",
                "label:contains('Public')",
                "[data-testid='public-option']",
                ".public-option",
                "input[name*='public']"
            ]
            
            public_option = None
            for selector in public_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            # Check if it's the public option
                            element_text = element.text.lower()
                            element_value = element.get_attribute("value", "").lower()
                            if 'public' in element_text or 'public' in element_value:
                                public_option = element
                                self.automation_logger.log_success(f"Found Public option: {selector}")
                                break
                    if public_option:
                        break
                except:
                    continue
            
            if public_option:
                # Click Public option if not already selected
                if public_option.get_attribute("type") == "radio" and not public_option.is_selected():
                    public_option.click()
                    time.sleep(2)
                    self.automation_logger.log_success("Selected Public option")
                elif public_option.get_attribute("type") == "radio" and public_option.is_selected():
                    self.automation_logger.log_info("Public option already selected")
            else:
                self.automation_logger.log_warning("Public option not found, trying to proceed anyway")
            
            # Look for URL input field or copy button
            url_selectors = [
                "input[readonly]",
                "input[value*='flipsidecrypto.xyz']",
                ".share-url-input",
                "[data-testid='share-url']",
                "input[type='text']",
                ".url-input",
                ".link-input"
            ]
            
            url_input = None
            for selector in url_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.get_attribute("value"):
                            url_value = element.get_attribute("value")
                            if 'flipsidecrypto.xyz' in url_value:
                                url_input = element
                                self.automation_logger.log_success(f"Found URL input: {selector}")
                                break
                    if url_input:
                        break
                except:
                    continue
            
            if url_input:
                shareable_url = url_input.get_attribute("value")
                # Always ensure it's in the shared format
                if '/shared/chats/' not in shareable_url:
                    if '/chat/' in shareable_url:
                        # Extract chat ID and convert to shared format
                        chat_id = shareable_url.split('/chat/')[-1]
                        shareable_url = f"https://flipsidecrypto.xyz/chat/shared/chats/{chat_id}"
                        self.automation_logger.log_info(f"Converted to shared format: {shareable_url}")
                    else:
                        # If no chat ID found, use current URL
                        current_url = self.driver.current_url
                        if '/chat/' in current_url:
                            chat_id = current_url.split('/chat/')[-1]
                            shareable_url = f"https://flipsidecrypto.xyz/chat/shared/chats/{chat_id}"
                            self.automation_logger.log_info(f"Constructed from current URL: {shareable_url}")
                
                self.automation_logger.log_success(f"Extracted shareable URL: {shareable_url}")
                
                # Close the modal (click outside or press Escape)
                try:
                    self.driver.find_element(By.TAG_NAME, "body").click()
                    time.sleep(1)
                except:
                    pass
                
                return shareable_url
            else:
                self.automation_logger.log_warning("URL input field not found")
                self._capture_warning_screenshot("url_input_not_found")
                # Always construct URL from current page URL in shared format
                current_url = self.driver.current_url
                if '/chat/' in current_url:
                    chat_id = current_url.split('/chat/')[-1]
                    constructed_url = f"https://flipsidecrypto.xyz/chat/shared/chats/{chat_id}"
                    self.automation_logger.log_info(f"Constructed shareable URL: {constructed_url}")
                    return constructed_url
                return ""
                
        except Exception as e:
            self.automation_logger.log_error(f"Failed to extract shareable link: {e}")
            return ""
    
    def _try_copy_response(self) -> bool:
        """Try to find and click the copy button to get the full response."""
        try:
            self.automation_logger.log_info("Looking for copy button...")
            
            # Look for copy button with more comprehensive selectors
            copy_selectors = [
                # Most specific selectors first
                "button[aria-label*='Copy']",
                "button[title*='Copy']",
                "button[data-testid*='copy']",
                "button[data-testid*='Copy']",
                # Text-based selectors (using XPath instead of CSS)
                "//button[contains(text(), 'Copy')]",
                "//button[contains(text(), 'copy')]",
                # Class-based selectors
                ".copy-button",
                "button[class*='copy']",
                "button[class*='Copy']",
                # Icon-based selectors
                "button svg[data-testid*='copy']",
                "button svg[data-testid*='Copy']",
                # Action button selectors (using XPath instead of CSS)
                "//button[contains(@class, 'action-button') and contains(text(), 'Copy')]",
                "//button[contains(@class, 'action-button') and contains(text(), 'copy')]",
                "//button[contains(@class, 'icon') and contains(text(), 'Copy')]",
                "//button[contains(@class, 'icon') and contains(text(), 'copy')]",
                # Generic button selectors
                "button[class*='action']",
                ".message-actions button",
                ".response-actions button",
                ".chat-actions button"
            ]
            
            copy_button = None
            for selector in copy_selectors:
                try:
                    # Use XPath for selectors starting with //
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.automation_logger.log_info(f"Checking {len(elements)} copy elements with selector: {selector}")
                    
                    for i, element in enumerate(elements):
                        if element.is_displayed() and element.is_enabled():
                            element_text = element.text.lower().strip()
                            element_title = (element.get_attribute('title') or '').lower()
                            element_aria_label = (element.get_attribute('aria-label') or '').lower()
                            element_class = (element.get_attribute('class') or '').lower()
                            element_data_testid = (element.get_attribute('data-testid') or '').lower()
                            
                            self.automation_logger.log_info(f"Copy element {i}: text='{element_text}', title='{element_title}', aria-label='{element_aria_label}', class='{element_class}', data-testid='{element_data_testid}'")
                            
                            # Check for copy-related content
                            if ('copy' in element_text or 
                                'copy' in element_title or 
                                'copy' in element_aria_label or
                                'copy' in element_class or
                                'copy' in element_data_testid or
                                'copy' in selector.lower()):
                                copy_button = element
                                self.automation_logger.log_success(f"Found copy button: {selector} - Element {i}")
                                break
                    if copy_button:
                        break
                except Exception as e:
                    self.automation_logger.log_warning(f"Error checking copy selector {selector}: {e}")
                    continue
            
            if copy_button:
                try:
                    # Scroll to element to ensure it's clickable
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", copy_button)
                    time.sleep(1)
                    copy_button.click()
                    time.sleep(2)  # Wait longer for copy action
                    self.automation_logger.log_success("Copy button clicked")
                    return True
                except Exception as e:
                    self.automation_logger.log_warning(f"Failed to click copy button: {e}")
                    return False
            else:
                self.automation_logger.log_info("Copy button not found")
                return False
                
        except Exception as e:
            self.automation_logger.log_warning(f"Failed to use copy button: {e}")
            return False
    
    def _capture_warning_screenshot(self, warning_type: str):
        """Capture a screenshot when a warning or error occurs."""
        try:
            if self.driver:
                screenshot_path = ScreenshotUtils.capture_screenshot(
                    self.driver, 
                    description=f"warning_{warning_type}"
                )
                if screenshot_path:
                    self.automation_logger.log_screenshot(screenshot_path, f"Warning screenshot: {warning_type}")
        except Exception as e:
            self.automation_logger.log_warning(f"Failed to capture warning screenshot: {e}")

    def capture_published_artifact_screenshot(self) -> Optional[str]:
        """Capture a screenshot of the published artifact by following Publish -> View -> New Window workflow."""
        self.automation_logger.log_info("📸 Starting published artifact screenshot workflow...")
        
        try:
            # Step 1: Look for and click the Publish button
            self.automation_logger.log_info("🔍 Looking for Publish button...")
            
            publish_selectors = [
                '//span[text()="Publish"]',
                '//span[contains(text(), "Publish")]',
                '//button[.//span[text()="Publish"]]',
                '//button[contains(text(), "Publish")]',
            ]
            
            publish_button = None
            for selector in publish_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            text = element.text.strip()
                            if "Publish" in text:
                                # Check if it's in the upper right area
                                location = element.location
                                size = self.driver.get_window_size()
                                if location['x'] > size['width'] * 0.5:  # Right half of screen
                                    publish_button = element
                                    self.automation_logger.log_info(f"✅ Found Publish button: '{text}' at x={location['x']}, y={location['y']}")
                                    break
                    if publish_button:
                        break
                except Exception as e:
                    self.automation_logger.log_warning(f"Publish selector {selector} failed: {e}")
                    continue
            
            if publish_button:
                # Click the Publish button
                self.automation_logger.log_info("📤 Clicking Publish button...")
                self.driver.execute_script("arguments[0].click();", publish_button)
                time.sleep(5)  # Wait for publish action
            else:
                self.automation_logger.log_info("ℹ️ Publish button not found, assuming already published")
            
            # Step 2: Look for and click the View button
            self.automation_logger.log_info("🔍 Looking for View button...")
            
            view_selectors = [
                '//span[text()="View"]',
                '//span[contains(text(), "View")]',
                '//button[.//span[text()="View"]]',
                '//button[contains(text(), "View")]',
            ]
            
            view_button = None
            for selector in view_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            text = element.text.strip()
                            if "View" in text:
                                # Check if it's in the upper right area
                                location = element.location
                                size = self.driver.get_window_size()
                                if location['x'] > size['width'] * 0.5:  # Right half of screen
                                    view_button = element
                                    self.automation_logger.log_info(f"✅ Found View button: '{text}' at x={location['x']}, y={location['y']}")
                                    break
                    if view_button:
                        break
                except Exception as e:
                    self.automation_logger.log_warning(f"View selector {selector} failed: {e}")
                    continue
            
            if not view_button:
                self.automation_logger.log_error("❌ View button not found")
                return None
            
            # Step 3: Get current window handles before clicking View
            original_window = self.driver.current_window_handle
            self.automation_logger.log_info(f"📋 Original window handle: {original_window}")
            
            # Step 4: Click the View button
            self.automation_logger.log_info("👁️ Clicking View button...")
            self.driver.execute_script("arguments[0].click();", view_button)
            time.sleep(3)  # Wait for new window to open
            
            # Step 5: Get all window handles after clicking View
            all_windows = self.driver.window_handles
            self.automation_logger.log_info(f"📋 All window handles after click: {all_windows}")
            
            # Step 6: Find and switch to the new window
            new_window = None
            for window in all_windows:
                if window != original_window:
                    new_window = window
                    break
            
            if not new_window:
                self.automation_logger.log_error("❌ No new window opened")
                return None
            
            # Step 7: Switch to the new window
            self.automation_logger.log_info(f"🔄 Switching to new window: {new_window}")
            self.driver.switch_to.window(new_window)
            
            # Step 8: Wait for the new page to load
            self.automation_logger.log_info("⏳ Waiting for new page to load...")
            time.sleep(10)
            
            # Step 9: Take screenshot of the new window
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = f"charts/published_artifact_{timestamp}.png"
            
            self.automation_logger.log_info("📸 Taking screenshot of published artifact...")
            self.driver.save_screenshot(screenshot_path)
            
            # Step 10: Get file details and return path
            if os.path.exists(screenshot_path):
                file_size = os.path.getsize(screenshot_path)
                self.automation_logger.log_info(f"✅ Published artifact screenshot saved: {screenshot_path}")
                self.automation_logger.log_info(f"📁 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                
                if file_size < 5 * 1024 * 1024:  # Under 5MB
                    self.automation_logger.log_info("✅ Twitter-friendly file size")
                else:
                    self.automation_logger.log_warning("⚠️ Large file size for Twitter")
                
                return screenshot_path
            else:
                self.automation_logger.log_error("❌ Screenshot file was not created")
                return None
                
        except Exception as e:
            self.automation_logger.log_error(f"❌ Error during published artifact screenshot: {e}")
            return None

    def capture_results(self) -> Dict[str, Any]:
        """Capture analysis results quickly and efficiently."""
        try:
            self.automation_logger.log_info("Capturing analysis results")
            
            # Extract shareable link first
            shareable_url = self.extract_shareable_link()
            
            results = {
                "timestamp": datetime.now().isoformat(),
                "chat_url": shareable_url if shareable_url else self.driver.current_url,
                "response_text": "",
                "screenshots": [],
                "artifacts": [],
                "response_metadata": {}
            }
            
            # First try to use the copy button to get the full response
            copy_button_found = self._try_copy_response()
            if copy_button_found:
                # Try to get text from clipboard
                try:
                    from selenium.webdriver.common.keys import Keys
                    # Use Ctrl+A to select all, then Ctrl+C to copy
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + "a")
                    time.sleep(0.5)
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.CONTROL + "c")
                    time.sleep(0.5)
                    
                    # Try to get clipboard content (this might not work in headless mode)
                    # For now, we'll fall back to the text extraction method
                except:
                    pass
            
            # Extract Twitter text output with more comprehensive selectors
            twitter_selectors = [
                # Most specific selectors first (using XPath instead of CSS)
                "//div[contains(text(), 'TWITTER_TEXT')]",
                "//div[contains(text(), '**TWITTER_TEXT**')]",
                "[data-testid='twitter-text']",
                ".twitter-text",
                ".twitter-output",
                # Message and response selectors
                ".message-content",
                ".chat-response",
                ".response-text",
                ".analysis-result",
                ".message",
                ".response",
                "[class*='message']",
                "[class*='response']",
                "[class*='content']",
                # Generic text containers
                "div[class*='text']",
                "p",
                "span",
                "div"
            ]
            
            for selector in twitter_selectors:
                try:
                    # Use XPath for selectors starting with //
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.automation_logger.log_info(f"Checking {len(elements)} elements with selector: {selector}")
                    
                    for i, element in enumerate(elements):
                        if element.is_displayed() and element.text.strip():
                            text_content = element.text.strip()
                            self.automation_logger.log_info(f"Element {i} text content: {text_content[:100]}...")
                            
                            # Look for TWITTER_TEXT specifically
                            if "TWITTER_TEXT" in text_content or "**TWITTER_TEXT**" in text_content:
                                # Extract just the Twitter content part
                                lines = text_content.split('\n')
                                twitter_content = ""
                                in_twitter_section = False
                                
                                for line in lines:
                                    if "TWITTER_TEXT" in line or "**TWITTER_TEXT**" in line:
                                        in_twitter_section = True
                                        continue
                                    elif in_twitter_section and line.strip():
                                        # Stop at HTML_CHART or other sections
                                        if (line.startswith("HTML_CHART") or 
                                            line.startswith("**HTML_CHART**") or
                                            line.startswith("View Report") or
                                            line.startswith("Based on my comprehensive analysis")):
                                            break
                                        # Skip empty lines and section headers
                                        if line.strip() and not line.startswith("**") and not line.startswith("##"):
                                            twitter_content += line.strip() + " "
                                
                                if twitter_content.strip():
                                    results["response_text"] = twitter_content.strip()
                                    self.automation_logger.log_success(f"Extracted Twitter text: {len(results['response_text'])} characters")
                                    break
                            elif not results["response_text"] and len(text_content) > 50:
                                # Fallback to any substantial text content that looks like a response
                                if ("analysis" in text_content.lower() or 
                                    "stablecoin" in text_content.lower() or
                                    "market" in text_content.lower() or
                                    "data" in text_content.lower()):
                                    results["response_text"] = text_content
                                    self.automation_logger.log_success(f"Extracted response text: {len(results['response_text'])} characters")
                                    break
                    if results["response_text"]:
                        break
                except Exception as e:
                    self.automation_logger.log_warning(f"Error checking Twitter selector {selector}: {e}")
                    continue
            
            # Look for the right panel with charts/visualizations
            right_panel_selectors = [
                ".right-panel",
                ".visualization-panel",
                ".report-panel",
                ".chart-panel",
                "[data-testid='right-panel']",
                ".dashboard-panel"
            ]
            
            right_panel = None
            for selector in right_panel_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.size['width'] > 200:
                            right_panel = element
                            self.automation_logger.log_success(f"Found right panel: {selector}")
                            break
                    if right_panel:
                        break
                except:
                    continue
            
            # If no specific right panel found, look for chart containers
            if not right_panel:
                chart_container_selectors = [
                    ".chart-container",
                    ".highcharts-container",
                    ".visualization-container",
                    "[data-testid='chart-container']"
                ]
                
                for selector in chart_container_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and element.size['width'] > 200:
                                right_panel = element
                                self.automation_logger.log_success(f"Found chart container: {selector}")
                                break
                        if right_panel:
                            break
                    except:
                        continue
            
            # Take screenshot of the right panel (charts area)
            if right_panel:
                try:
                    # Scroll to make sure the panel is visible
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", right_panel)
                    time.sleep(2)
                    
                    # Take screenshot of the right panel
                    panel_screenshot = ScreenshotUtils.capture_element_screenshot(
                        self.driver,
                        right_panel,
                        filename="charts_panel.png",
                        description="charts_panel"
                    )
                    
                    if panel_screenshot:
                        results["screenshots"].append(panel_screenshot)
                        self.automation_logger.log_screenshot(panel_screenshot, "Charts panel screenshot")
                        
                        # Add as artifact
                        artifact_info = {
                            "type": "charts_panel",
                            "index": 1,
                            "screenshot": panel_screenshot,
                            "selector": "right_panel",
                            "tag_name": right_panel.tag_name
                        }
                        results["artifacts"].append(artifact_info)
                        
                except Exception as e:
                    self.automation_logger.log_warning(f"Failed to screenshot right panel: {e}")
            
            # Also look for individual charts and analysis artifacts within the panel
            artifact_selectors = [
                "canvas",
                "svg",
                ".highcharts-container",
                "[class*='chart']",
                "[class*='graph']",
                ".analysis-artifact",
                ".artifact-container",
                ".visualization-container",
                ".report-container",
                ".chart-container",
                ".graph-container",
                "[data-testid*='chart']",
                "[data-testid*='artifact']",
                "[data-testid*='visualization']"
            ]
            
            for selector in artifact_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for i, element in enumerate(elements):
                        if element.is_displayed() and element.size['width'] > 100 and element.size['height'] > 100:
                            artifact_screenshot = ScreenshotUtils.capture_element_screenshot(
                                self.driver,
                                element,
                                filename=f"artifact_{len(results['artifacts'])+1}.png",
                                description=f"artifact_{len(results['artifacts'])+1}"
                            )
                            
                            if artifact_screenshot:
                                artifact_info = {
                                    "type": "analysis_artifact",
                                    "index": len(results["artifacts"]) + 1,
                                    "screenshot": artifact_screenshot,
                                    "selector": selector,
                                    "tag_name": element.tag_name
                                }
                                results["artifacts"].append(artifact_info)
                                results["screenshots"].append(artifact_screenshot)
                                self.automation_logger.log_screenshot(artifact_screenshot, f"Analysis artifact {len(results['artifacts'])}")
                except:
                    continue
            
            # Create response metadata
            results["response_metadata"] = {
                "word_count": len(results["response_text"].split()) if results["response_text"] else 0,
                "has_charts": any("chart" in a["type"] for a in results["artifacts"]),
                "has_tables": any("table" in a["type"] for a in results["artifacts"]),
                "has_code": "code" in results["response_text"].lower() if results["response_text"] else False,
                "analysis_type": "market_analysis"  # Default, could be improved
            }
            
            self.automation_logger.log_analysis_result(
                len(results["response_text"]),
                len(results["artifacts"]),
                len(results["screenshots"])
            )
            
            return results
            
        except Exception as e:
            self.automation_logger.log_error(f"Failed to capture results: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "chat_url": "",
                "response_text": "",
                "screenshots": [],
                "artifacts": [],
                "response_metadata": {}
            }
    
    def run_analysis(self, custom_prompt: str = None, response_timeout: int = 240) -> Dict[str, Any]:
        """Run the complete analysis workflow with timeouts."""
        results = {
            "success": False,
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }
        
        try:
            # Step 1: Initialization
            self.automation_logger.start_step(AutomationStep.INITIALIZATION, "Setting up automation environment")
            self.logger.info("Starting Flipside chat analysis")
            self.automation_logger.end_step(True, "Environment ready")
            
            # Step 2: WebDriver Setup
            self.automation_logger.start_step(AutomationStep.WEBDRIVER_SETUP, "Initializing Chrome WebDriver")
            if not self.setup_chrome_driver():
                raise Exception("Failed to setup Chrome driver")
            self.automation_logger.end_step(True, "Chrome WebDriver ready")
            
            # Step 3: Session Loading
            self.automation_logger.start_step(AutomationStep.SESSION_LOADING, "Loading authentication cookies")
            if not self.setup_session_with_timeout(60):
                raise Exception("Failed to setup session within timeout")
            self.automation_logger.end_step(True, "Session cookies loaded")
            
            # Step 4: Navigation
            self.automation_logger.start_step(AutomationStep.NAVIGATION, "Navigating to Flipside chat page")
            if not self.navigate_to_chat_with_timeout(60):
                raise Exception("Failed to navigate to chat within timeout")
            self.automation_logger.end_step(True, "Successfully navigated to chat page")
            
            # Step 5: Authentication
            self.automation_logger.start_step(AutomationStep.AUTHENTICATION, "Applying session cookies")
            # Cookies are applied in setup_session, so this step is informational
            self.automation_logger.end_step(True, "Authentication cookies applied")
            
            # Step 6: Chat Access
            self.automation_logger.start_step(AutomationStep.CHAT_ACCESS, "Accessing chat interface")
            # Get prompt (custom or today's)
            prompt = custom_prompt or get_prompt_for_today()
            if not prompt:
                raise Exception("No prompt available")
            self.automation_logger.log_info(f"Using prompt: {prompt[:50]}...")
            self.automation_logger.end_step(True, "Chat interface accessible")
            
            # Step 7: Prompt Submission
            self.automation_logger.start_step(AutomationStep.PROMPT_SUBMISSION, "Submitting analysis prompt")
            if not self.submit_prompt_with_timeout(prompt, 60):
                raise Exception("Failed to submit analysis prompt within timeout")
            self.automation_logger.end_step(True, "Prompt submitted successfully")
            
            # Step 8: Response Waiting
            self.automation_logger.start_step(AutomationStep.RESPONSE_WAITING, f"Waiting for complete AI response with charts ({response_timeout//60} min timeout)")
            if not self.wait_for_complete_response_with_timeout(response_timeout):
                self.automation_logger.log_warning("Complete response timeout, but continuing...")
            self.automation_logger.end_step(True, "AI response processing completed")
            
            # Step 9: Result Capture
            self.automation_logger.start_step(AutomationStep.RESULT_CAPTURE, "Capturing analysis results")
            results["data"] = self.capture_results()
            results["success"] = True
            
            # Log the complete result
            log_path = self.results_logger.log_analysis_result(results)
            if log_path:
                self.automation_logger.log_success(f"Results logged to: {log_path}")
            
            # Log analysis summary
            response_length = len(results["data"].get("response_text", ""))
            artifacts_count = len(results["data"].get("artifacts", []))
            screenshots_count = len(results["data"].get("screenshots", []))
            self.automation_logger.log_analysis_result(response_length, artifacts_count, screenshots_count)
            
            self.automation_logger.end_step(True, f"Captured {artifacts_count} artifacts, {screenshots_count} screenshots")
            
            # Step 9.5: Published Artifact Screenshot
            self.automation_logger.start_step(AutomationStep.RESULT_CAPTURE, "Capturing published artifact screenshot")
            try:
                published_screenshot = self.capture_published_artifact_screenshot()
                if published_screenshot:
                    self.automation_logger.log_success(f"Published artifact screenshot: {published_screenshot}")
                    results["data"]["published_screenshot"] = published_screenshot
                    results["data"]["screenshots"].append(published_screenshot)
                else:
                    self.automation_logger.log_warning("Failed to capture published artifact screenshot")
            except Exception as screenshot_error:
                self.automation_logger.log_warning(f"Error capturing published artifact screenshot: {screenshot_error}")
            self.automation_logger.end_step(True, "Published artifact screenshot workflow completed")
            
            # Step 10: Final Screenshot
            self.automation_logger.start_step(AutomationStep.CLEANUP, "Capturing final screenshot")
            try:
                final_screenshot = ScreenshotUtils.capture_screenshot(
                    self.driver, description="final_state"
                )
                if final_screenshot:
                    self.automation_logger.log_screenshot(final_screenshot, "Final state screenshot captured")
                    results["data"]["screenshots"].append(final_screenshot)
            except Exception as screenshot_error:
                self.automation_logger.log_warning(f"Failed to capture final screenshot: {screenshot_error}")
            self.automation_logger.end_step(True, "Final screenshot captured")
            
        except Exception as e:
            error_msg = f"Analysis failed: {e}"
            self.automation_logger.log_error(error_msg)
            results["error"] = error_msg
            
            # Capture error screenshot
            if self.driver:
                try:
                    ScreenshotUtils.capture_screenshot(
                        self.driver, description="error_state"
                    )
                    self.automation_logger.log_screenshot("error_state.png", "Error state captured")
                except Exception as screenshot_error:
                    self.automation_logger.log_error(f"Failed to capture error screenshot: {screenshot_error}")
        
        finally:
            # Step 11: Cleanup
            self.automation_logger.start_step(AutomationStep.CLEANUP, "Cleaning up resources")
            
            # Cleanup stealth automation if used
            if self.stealth_automation:
                try:
                    self.stealth_automation.cleanup()
                    self.automation_logger.log_success("Stealth automation cleanup complete")
                except Exception as e:
                    self.automation_logger.log_warning(f"Error during stealth automation cleanup: {e}")
            elif self.driver:
                try:
                    self.driver.quit()
                    self.automation_logger.log_success("WebDriver cleanup complete")
                except Exception as e:
                    self.automation_logger.log_warning(f"Error during WebDriver cleanup: {e}")
            
            self.automation_logger.end_step(True, "Cleanup completed")
            
            # Print final summary
            self.automation_logger.print_summary()
        
        return results
