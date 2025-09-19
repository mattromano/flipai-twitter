"""
Main Chat Automation Script for Flipside Crypto

Automates chat analysis using Selenium with comprehensive error handling,
session management, and screenshot capture.
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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from src.session_manager import SessionManager
from src.utils import (
    WaitUtils, ElementUtils, ScreenshotUtils, TextUtils, 
    PromptUtils, RetryUtils
)
from src.results_logger import ResultsLogger
from config.prompts import get_prompt_for_today


class FlipsideChatAutomation:
    """Main automation class for Flipside Crypto chat analysis."""
    
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.session_manager: Optional[SessionManager] = None
        self.results_logger: Optional[ResultsLogger] = None
        self.automation_logger: AutomationLogger = get_automation_logger()
        self.setup_logging()
        self.setup_directories()
        self.results_logger = ResultsLogger()
        
    def setup_logging(self):
        """Set up logging configuration."""
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        # Configure logging
        log_level = logging.DEBUG if os.getenv('DEBUG_MODE', 'false').lower() == 'true' else logging.INFO
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # File handler
        log_filename = f"logs/flipside_automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(log_format))
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            handlers=[file_handler, console_handler],
            format=log_format
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Logging setup complete")
    
    def setup_directories(self):
        """Create necessary directories."""
        directories = ["screenshots", "logs", "artifacts"]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        self.logger.info("Directory setup complete")
    
    def setup_chrome_driver(self) -> bool:
        """
        Set up Chrome WebDriver with optimized configuration.
        
        Returns:
            True if setup successful, False otherwise
        """
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
            
            # Logging
            chrome_options.add_argument('--enable-logging')
            chrome_options.add_argument('--log-level=0')
            
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
    
    def setup_session(self) -> bool:
        """
        Set up session management and authentication.
        
        Returns:
            True if session setup successful, False otherwise
        """
        try:
            if not self.driver:
                self.logger.error("WebDriver not initialized")
                return False
            
            # Initialize session manager
            self.session_manager = SessionManager(self.driver)
            
            # Load cookies from environment
            try:
                cookies = self.session_manager.load_cookies_from_env()
                if not cookies:
                    self.logger.error("No cookies found in environment")
                    return False
                
                # Apply cookies to driver
                if not self.session_manager.apply_cookies_to_driver(cookies):
                    self.logger.error("Failed to apply cookies to driver")
                    return False
                
                self.logger.info("Session cookies loaded and applied")
                
            except Exception as e:
                self.logger.error(f"Failed to load session cookies: {e}")
                return False
            
            # Validate session
            if not self.session_manager.validate_session():
                self.logger.error("Session validation failed")
                return False
            
            self.logger.info("Session setup complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Session setup failed: {e}")
            return False
    
    def navigate_to_chat(self) -> bool:
        """
        Navigate to the Flipside Crypto chat page.
        
        Returns:
            True if navigation successful, False otherwise
        """
        try:
            chat_url = "https://flipsidecrypto.xyz/chat/"
            self.logger.info(f"Navigating to chat: {chat_url}")
            
            self.driver.get(chat_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for chat interface to load
            chat_selectors = [
                "textarea[placeholder*='Ask FlipsideAI']",
                "textarea",
                "textarea[placeholder*='message']",
                "textarea[data-testid='chat-input']",
                ".chat-input",
                "[data-testid='chat-interface']"
            ]
            
            chat_loaded = False
            for selector in chat_selectors:
                element = WaitUtils.wait_for_element(
                    self.driver, By.CSS_SELECTOR, selector, 10, f"chat interface ({selector})"
                )
                if element:
                    chat_loaded = True
                    break
            
            if not chat_loaded:
                self.logger.error("Chat interface not found")
                return False
            
            self.logger.info("Successfully navigated to chat page")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to chat: {e}")
            return False
    
    def submit_analysis_prompt(self, prompt: str) -> bool:
        """
        Submit an analysis prompt to the chat.
        
        Args:
            prompt: Analysis prompt to submit
            
        Returns:
            True if submission successful, False otherwise
        """
        try:
            self.logger.info(f"Submitting analysis prompt: {prompt[:100]}...")
            
            # Find chat input
            input_selectors = [
                "textarea[placeholder*='Ask FlipsideAI']",
                "textarea",
                "textarea[placeholder*='message']",
                "textarea[data-testid='chat-input']",
                ".chat-input textarea",
                "input[type='text']"
            ]
            
            chat_input = None
            for selector in input_selectors:
                chat_input = WaitUtils.wait_for_element(
                    self.driver, By.CSS_SELECTOR, selector, 10, f"chat input ({selector})"
                )
                if chat_input:
                    break
            
            if not chat_input:
                self.logger.error("Chat input not found")
                return False
            
            # Clear and type prompt
            chat_input.clear()
            chat_input.send_keys(prompt)
            
            # Find and click submit button
            submit_selectors = [
                "button[type='submit']",
                "button[data-testid='send']",
                ".send-button",
                "button:contains('Send')",
                "button:contains('Submit')",
                "button"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                submit_button = WaitUtils.wait_for_clickable(
                    self.driver, By.CSS_SELECTOR, selector, 10, f"submit button ({selector})"
                )
                if submit_button:
                    break
            
            if not submit_button:
                # Try pressing Enter as fallback
                from selenium.webdriver.common.keys import Keys
                chat_input.send_keys(Keys.RETURN)
                self.logger.info("Submitted prompt using Enter key")
            else:
                submit_button.click()
                self.logger.info("Submitted prompt using submit button")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to submit analysis prompt: {e}")
            return False
    
    def wait_for_analysis_completion(self) -> bool:
        """
        Wait for the analysis to complete.
        
        Returns:
            True if analysis completed, False if timeout
        """
        try:
            timeout = int(os.getenv('ANALYSIS_TIMEOUT', '60'))
            self.logger.info(f"Waiting for analysis completion (timeout: {timeout}s)")
            
            # Wait for loading indicators to disappear
            WaitUtils.wait_for_loading_to_complete(self.driver, timeout)
            
            # Wait for response to appear
            response_selectors = [
                ".message-content",
                ".chat-response",
                "[data-testid='response']",
                ".response-text",
                ".analysis-result"
            ]
            
            response_found = False
            for selector in response_selectors:
                element = WaitUtils.wait_for_element(
                    self.driver, By.CSS_SELECTOR, selector, 30, f"response ({selector})"
                )
                if element:
                    response_found = True
                    break
            
            if not response_found:
                self.logger.warning("No response found, but continuing...")
            
            self.logger.info("Analysis completion check finished")
            return True
            
        except Exception as e:
            self.logger.error(f"Error waiting for analysis completion: {e}")
            return False
    
    def capture_results(self) -> Dict[str, Any]:
        """
        Capture analysis results including screenshots and text.
        
        Returns:
            Dictionary containing results data
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "chat_url": "",
            "response_text": "",
            "screenshots": [],
            "chart_elements": []
        }
        
        try:
            # Capture full page screenshot
            full_screenshot = ScreenshotUtils.capture_screenshot(
                self.driver, description="full_page"
            )
            if full_screenshot:
                results["screenshots"].append(full_screenshot)
            
            # Extract chat URL
            results["chat_url"] = TextUtils.extract_chat_url(self.driver)
            
            # Extract response text with metadata
            response_data = self._extract_response_with_metadata()
            results["response_text"] = response_data.get("text", "")
            results["response_metadata"] = response_data.get("metadata", {})
            
            # Find and capture all artifacts (charts, tables, code blocks)
            artifacts = self._find_and_capture_artifacts()
            results["artifacts"] = artifacts
            
            # Add artifact screenshots to main screenshots list
            for artifact in artifacts:
                if artifact.get("screenshot"):
                    results["screenshots"].append(artifact["screenshot"])
            
            self.logger.info(f"Captured results: {len(results['screenshots'])} screenshots, "
                           f"{len(results['artifacts'])} artifacts, "
                           f"{len(results['response_text'])} chars of text")
            
        except Exception as e:
            self.logger.error(f"Error capturing results: {e}")
        
        return results
    
    def _extract_response_with_metadata(self) -> Dict[str, Any]:
        """
        Extract response text with enhanced metadata about the analysis.
        
        Returns:
            Dictionary with response text and metadata
        """
        try:
            response_data = {
                "text": "",
                "metadata": {
                    "word_count": 0,
                    "has_charts": False,
                    "has_tables": False,
                    "has_code": False,
                    "analysis_type": "unknown",
                    "confidence_score": None
                }
            }
            
            # Extract response text using multiple selectors
            response_selectors = [
                ".message-content",
                ".chat-response", 
                "[data-testid='response']",
                ".response-text",
                ".analysis-result",
                ".message",
                ".response",
                "[class*='message']",
                "[class*='response']"
            ]
            
            response_text = ""
            for selector in response_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element and element.text.strip():
                        response_text = element.text.strip()
                        break
                except:
                    continue
            
            if response_text:
                response_data["text"] = response_text
                response_data["metadata"]["word_count"] = len(response_text.split())
                
                # Analyze content type
                text_lower = response_text.lower()
                if any(word in text_lower for word in ['chart', 'graph', 'visualization', 'plot']):
                    response_data["metadata"]["has_charts"] = True
                if any(word in text_lower for word in ['table', 'data', 'rows', 'columns']):
                    response_data["metadata"]["has_tables"] = True
                if any(word in text_lower for word in ['code', 'sql', 'query', 'function']):
                    response_data["metadata"]["has_code"] = True
                
                # Determine analysis type
                if any(word in text_lower for word in ['price', 'trading', 'market']):
                    response_data["metadata"]["analysis_type"] = "market_analysis"
                elif any(word in text_lower for word in ['volume', 'transaction', 'activity']):
                    response_data["metadata"]["analysis_type"] = "volume_analysis"
                elif any(word in text_lower for word in ['user', 'address', 'wallet']):
                    response_data["metadata"]["analysis_type"] = "user_analysis"
                elif any(word in text_lower for word in ['defi', 'protocol', 'yield']):
                    response_data["metadata"]["analysis_type"] = "defi_analysis"
                
                self.logger.info(f"Response metadata: {response_data['metadata']}")
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"Error extracting response metadata: {e}")
            return {"text": "", "metadata": {}}
    
    def _find_and_capture_artifacts(self) -> List[Dict[str, Any]]:
        """
        Find and capture screenshots of analysis artifacts (charts, tables, etc.).
        
        Returns:
            List of artifact information with screenshots
        """
        artifacts = []
        
        try:
            # Look for common chart/visualization elements
            chart_selectors = [
                "canvas",  # HTML5 canvas elements
                "svg",     # SVG charts
                "[class*='chart']",
                "[class*='graph']", 
                "[class*='visualization']",
                "[class*='plot']",
                "[data-testid*='chart']",
                "[data-testid*='graph']",
                ".recharts-wrapper",  # Recharts library
                ".plotly",            # Plotly charts
                ".highcharts-container",  # Highcharts
                ".d3-chart"           # D3.js charts
            ]
            
            # Look for table elements
            table_selectors = [
                "table",
                "[class*='table']",
                "[data-testid*='table']",
                ".data-table",
                ".results-table"
            ]
            
            # Look for code blocks
            code_selectors = [
                "pre",
                "code",
                "[class*='code']",
                "[class*='sql']",
                ".code-block",
                ".sql-query"
            ]
            
            all_selectors = [
                ("chart", chart_selectors),
                ("table", table_selectors), 
                ("code", code_selectors)
            ]
            
            for artifact_type, selectors in all_selectors:
                for selector in selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for i, element in enumerate(elements):
                            if element.is_displayed() and element.size['width'] > 50 and element.size['height'] > 50:
                                # Take screenshot of this element
                                screenshot_path = ScreenshotUtils.capture_element_screenshot(
                                    self.driver,
                                    element,
                                    filename=f"{artifact_type}_{len(artifacts)+1}.png",
                                    description=f"{artifact_type}_{len(artifacts)+1}"
                                )
                                
                                if screenshot_path:
                                    artifact_info = {
                                        "type": artifact_type,
                                        "index": len(artifacts) + 1,
                                        "screenshot": screenshot_path,
                                        "selector": selector,
                                        "tag_name": element.tag_name,
                                        "size": element.size,
                                        "location": element.location
                                    }
                                    artifacts.append(artifact_info)
                                    self.logger.info(f"Captured {artifact_type} artifact: {screenshot_path}")
                                    
                    except Exception as e:
                        self.logger.debug(f"Error checking selector {selector}: {e}")
                        continue
            
            self.logger.info(f"Found and captured {len(artifacts)} artifacts")
            
        except Exception as e:
            self.logger.error(f"Error finding artifacts: {e}")
        
        return artifacts
    
    def run_analysis(self) -> Dict[str, Any]:
        """
        Run the complete analysis workflow.
        
        Returns:
            Dictionary containing analysis results
        """
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
            if not self.setup_session():
                raise Exception("Failed to setup session")
            self.automation_logger.end_step(True, "Session cookies loaded")
            
            # Step 4: Navigation
            self.automation_logger.start_step(AutomationStep.NAVIGATION, "Navigating to Flipside chat page")
            if not self.navigate_to_chat():
                raise Exception("Failed to navigate to chat")
            self.automation_logger.end_step(True, "Successfully navigated to chat page")
            
            # Step 5: Authentication
            self.automation_logger.start_step(AutomationStep.AUTHENTICATION, "Applying session cookies")
            # Cookies are applied in setup_session, so this step is informational
            self.automation_logger.end_step(True, "Authentication cookies applied")
            
            # Step 6: Chat Access
            self.automation_logger.start_step(AutomationStep.CHAT_ACCESS, "Accessing chat interface")
            # Get today's prompt
            prompt = get_prompt_for_today()
            if not prompt:
                raise Exception("No prompt available")
            self.automation_logger.log_info(f"Using prompt: {prompt[:50]}...")
            self.automation_logger.end_step(True, "Chat interface accessible")
            
            # Step 7: Prompt Submission
            self.automation_logger.start_step(AutomationStep.PROMPT_SUBMISSION, "Submitting analysis prompt")
            if not self.submit_analysis_prompt(prompt):
                raise Exception("Failed to submit analysis prompt")
            self.automation_logger.end_step(True, "Prompt submitted successfully")
            
            # Step 8: Response Waiting
            self.automation_logger.start_step(AutomationStep.RESPONSE_WAITING, "Waiting for AI response")
            if not self.wait_for_analysis_completion():
                self.automation_logger.log_warning("Analysis completion timeout, but continuing...")
            self.automation_logger.end_step(True, "AI response received")
            
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
            # Step 10: Cleanup
            self.automation_logger.start_step(AutomationStep.CLEANUP, "Cleaning up resources")
            if self.driver:
                try:
                    self.driver.quit()
                    self.automation_logger.log_success("WebDriver cleanup complete")
                except Exception as e:
                    self.automation_logger.log_warning(f"Error during WebDriver cleanup: {e}")
            self.automation_logger.end_step(True, "Cleanup completed")
            
            # Print final summary
            self.automation_logger.print_summary()
        
        return results
    
    def run_with_retry(self, max_retries: int = 3) -> Dict[str, Any]:
        """
        Run analysis with retry logic.
        
        Args:
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dictionary containing analysis results
        """
        def run_analysis_func():
            return self.run_analysis()
        
        try:
            return RetryUtils.retry_on_exception(
                run_analysis_func,
                max_retries=max_retries,
                delay=5.0,
                backoff_factor=2.0,
                exceptions=(Exception,)
            )
        except Exception as e:
            self.logger.error(f"All retry attempts failed: {e}")
            return {
                "success": False,
                "error": f"All retry attempts failed: {e}",
                "timestamp": datetime.now().isoformat(),
                "data": {}
            }


def main():
    """Main entry point for the automation script."""
    automation = FlipsideChatAutomation()
    
    try:
        # Run analysis with retry
        results = automation.run_with_retry(max_retries=3)
        
        # Log results
        if results["success"]:
            print("✅ Analysis completed successfully!")
            print(f"📊 Chat URL: {results['data'].get('chat_url', 'N/A')}")
            print(f"📝 Response length: {len(results['data'].get('response_text', ''))} characters")
            print(f"📸 Screenshots captured: {len(results['data'].get('screenshots', []))}")
            print(f"📈 Charts found: {len(results['data'].get('chart_elements', []))}")
        else:
            print("❌ Analysis failed!")
            print(f"Error: {results.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
