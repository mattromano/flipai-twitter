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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from modules.shared.authentication import StealthAuthenticator
from modules.shared.logger import AutomationLogger


class FlipsideChatManager:
    """Manages Flipside AI chat automation workflow."""
    
    def __init__(self, use_stealth_auth: bool = True):  # Default to True for automated login
        self.driver: Optional[webdriver.Chrome] = None
        self.authenticator: Optional[StealthAuthenticator] = None
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
                self.logger.log_info("🤖 Setting up stealth Chrome driver")
                self.authenticator = StealthAuthenticator(self.logger)
                if not self.authenticator.setup_driver():
                    self.logger.log_error("❌ Failed to setup stealth driver")
                    return False
                self.driver = self.authenticator.driver
                self.logger.log_success("✅ ✅ Stealth Chrome driver setup complete")
            else:
                self.logger.log_info("🤖 Setting up regular Chrome driver")
                self.driver = self._setup_standard_driver()
                if not self.driver:
                    self.logger.log_error("❌ Failed to setup regular driver")
                    return False
                self.logger.log_success("✅ ✅ Regular Chrome driver setup complete")
            
            self.logger.log_success("✅ ✅ Automation environment initialized")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Initialization failed: {e}")
            return False
    
    def authenticate(self) -> bool:
        """Authenticate with Flipside."""
        try:
            self.logger.log_info("🔐 Starting authentication")
            
            if self.use_stealth_auth and self.authenticator:
                self.logger.log_info("🔐 Starting stealth login process")
                success = self.authenticator.login()
                if success:
                    self.logger.log_success("✅ Stealth authentication successful")
                    return True
                else:
                    self.logger.log_error("❌ Stealth authentication failed")
                    return False
            else:
                # For regular driver, we'll skip authentication for now
                # This assumes the user is already logged in or will log in manually
                self.logger.log_info("ℹ️ Using regular driver - skipping automatic authentication")
                self.logger.log_info("ℹ️ Please ensure you are logged into Flipside in the browser")
                return True
                
        except Exception as e:
            self.logger.log_error(f"Authentication failed: {e}")
            return False
    
    def navigate_to_chat(self) -> bool:
        """Navigate to the Flipside chat page."""
        try:
            self.logger.log_info("🧭 Navigating to chat page")
            
            # Try different chat URLs
            chat_urls = [
                "https://flipsidecrypto.xyz/chat/",
                "https://app.flipsidecrypto.xyz/chat/",
                "https://flipsidecrypto.xyz/chat",
                "https://app.flipsidecrypto.xyz/chat"
            ]
            
            navigation_successful = False
            for chat_url in chat_urls:
                try:
                    self.logger.log_info(f"🌐 Trying chat URL: {chat_url}")
                    self.driver.get(chat_url)
                    time.sleep(5)
                    
                    # Check if we're on a chat page (not login page)
                    current_url = self.driver.current_url
                    page_title = self.driver.title
                    
                    self.logger.log_info(f"📍 Current URL: {current_url}")
                    self.logger.log_info(f"📄 Page title: {page_title}")
                    
                    # Check if we're not on login page and page has loaded
                    if "login" not in current_url.lower() and "signin" not in current_url.lower():
                        # Look for chat-specific elements
                        chat_indicators = [
                            "textarea",
                            "input[placeholder*='message']",
                            "input[placeholder*='ask']",
                            "[data-testid*='chat']",
                            ".chat",
                            ".message"
                        ]
                        
                        chat_found = False
                        for indicator in chat_indicators:
                            try:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                                if elements:
                                    chat_found = True
                                    self.logger.log_info(f"✅ Found chat indicator: {indicator}")
                                    break
                            except:
                                continue
                        
                        if chat_found or "chat" in current_url.lower():
                            self.logger.log_info(f"✅ Successfully navigated to chat page: {current_url}")
                            navigation_successful = True
                            break
                        else:
                            self.logger.log_info(f"❌ No chat elements found at {current_url}")
                    else:
                        self.logger.log_info(f"❌ Still on login page: {current_url}")
                        
                except Exception as e:
                    self.logger.log_warning(f"Failed to navigate to {chat_url}: {e}")
                    continue
            
            if not navigation_successful:
                self.logger.log_error("❌ Could not navigate to chat page")
                return False
            
            # Wait for page to fully load
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
            
            # Wait for page to fully load
            time.sleep(5)
            
            # Take screenshot for debugging
            self.driver.save_screenshot("screenshots/chat_page_before_input.png")
            self.logger.log_info("📸 Chat page screenshot saved for debugging")
            
            # Find chat input with comprehensive selectors
            chat_input = None
            chat_selectors = [
                "textarea[placeholder*='Ask FlipsideAI']",
                "textarea[placeholder*='message']",
                "textarea[placeholder*='Message']",
                "textarea[placeholder*='ask']",
                "textarea[placeholder*='Ask']",
                "textarea[data-testid='chat-input']",
                "textarea[data-testid='message-input']",
                "textarea[data-testid='input']",
                "textarea[class*='input']",
                "textarea[class*='message']",
                "textarea[class*='chat']",
                "textarea[id*='input']",
                "textarea[id*='message']",
                "textarea[id*='chat']",
                "textarea[aria-label*='message']",
                "textarea[aria-label*='input']",
                "textarea[aria-label*='chat']",
                "textarea",
                "input[type='text']",
                "input[placeholder*='message']",
                "input[placeholder*='ask']",
                "input[data-testid='chat-input']",
                "input[data-testid='message-input']"
            ]
            
            for selector in chat_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element and element.is_displayed() and element.is_enabled():
                            chat_input = element
                            self.logger.log_info(f"✅ Found chat input with selector: {selector}")
                            break
                    if chat_input:
                        break
                except Exception as e:
                    self.logger.log_debug(f"Chat selector {selector} failed: {e}")
                    continue
            
            if not chat_input:
                # Debug: List all input and textarea elements
                try:
                    all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    all_textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                    self.logger.log_info(f"🔍 Found {len(all_inputs)} input elements and {len(all_textareas)} textarea elements")
                    
                    for i, elem in enumerate(all_inputs + all_textareas):
                        try:
                            elem_type = elem.get_attribute("type") or elem.tag_name
                            elem_placeholder = elem.get_attribute("placeholder") or "unknown"
                            elem_id = elem.get_attribute("id") or "unknown"
                            elem_class = elem.get_attribute("class") or "unknown"
                            elem_data_testid = elem.get_attribute("data-testid") or "unknown"
                            is_displayed = elem.is_displayed()
                            is_enabled = elem.is_enabled()
                            self.logger.log_info(f"   Element {i}: {elem_type}, placeholder='{elem_placeholder}', id='{elem_id}', class='{elem_class}', data-testid='{elem_data_testid}', displayed={is_displayed}, enabled={is_enabled}")
                        except:
                            pass
                except Exception as e:
                    self.logger.log_warning(f"Could not enumerate elements: {e}")
                
                self.logger.log_error("❌ Chat input not found")
                return False
            
            # Clear and type prompt
            self.logger.log_info("⌨️ Typing prompt into chat input")
            chat_input.clear()
            time.sleep(1)
            chat_input.send_keys(prompt)
            time.sleep(2)
            
            # Submit (usually Enter key or submit button)
            self.logger.log_info("📤 Submitting prompt")
            chat_input.send_keys("\n")
            time.sleep(2)
            
            self.logger.log_success("✅ Prompt submitted successfully")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Prompt submission failed: {e}")
            return False
    
    def wait_for_response(self, timeout: int = 600) -> bool:
        """Wait for complete AI response including charts and visualizations."""
        try:
            self.logger.log_info(f"⏳ Waiting for complete AI response (timeout: {timeout}s)")
            
            start_time = time.time()
            response_complete = False
            capture_after_3min = False
            response_started = False
            chat_input_was_disabled = False
            
            while time.time() - start_time < timeout:
                try:
                    # Look for the new analysis conclusion marker
                    conclusion_found = False
                    conclusion_selectors = [
                        "//div[contains(text(), 'THIS_CONCLUDES_THE_ANALYSIS')]",
                        "//div[contains(text(), '**THIS_CONCLUDES_THE_ANALYSIS**')]",
                        "//span[contains(text(), 'THIS_CONCLUDES_THE_ANALYSIS')]",
                        "//p[contains(text(), 'THIS_CONCLUDES_THE_ANALYSIS')]"
                    ]
                    
                    for selector in conclusion_selectors:
                        try:
                            elements = self.driver.find_elements(By.XPATH, selector)
                            for element in elements:
                                if element.is_displayed() and element.text.strip():
                                    conclusion_found = True
                                    self.logger.log_success("Analysis conclusion marker found!")
                                    break
                            if conclusion_found:
                                break
                        except:
                            continue
                    
                    # Look for Twitter text output (indicates response started)
                    twitter_found = False
                    twitter_selectors = [
                        "//div[contains(text(), 'TWITTER_TEXT:')]",
                        "//div[contains(text(), 'Add a quick 260 character summary')]",
                        "[data-testid='twitter-text']",
                        ".twitter-text",
                        ".twitter-output",
                        "div:contains('TWITTER_TEXT')",
                        "div:contains('Twitter')"
                    ]
                    
                    for selector in twitter_selectors:
                        try:
                            if selector.startswith('//'):
                                elements = self.driver.find_elements(By.XPATH, selector)
                            else:
                                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                if element.is_displayed() and element.text.strip():
                                    twitter_found = True
                                    self.logger.log_success("Twitter text output found")
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
                                    self.logger.log_success("Charts/visualizations found")
                                    break
                            if charts_found:
                                break
                        except:
                            continue
                    
                    # Check if we need to click "View Report" button to show visuals
                    self._click_view_report_buttons()
                    
                    # Check if we should capture results after 3 minutes
                    elapsed = int(time.time() - start_time)
                    if elapsed >= 180 and not capture_after_3min:  # 3 minutes
                        self.logger.log_info("3 minutes elapsed - will capture results regardless of completion")
                        capture_after_3min = True
                    
                    # Check if chat input is editable again (indicates response is complete)
                    chat_input_editable = False
                    try:
                        chat_input = self._find_chat_input()
                        if chat_input and chat_input.is_displayed() and chat_input.is_enabled():
                            chat_input_editable = True
                    except Exception as e:
                        # Handle stale element reference
                        if "stale element" in str(e).lower():
                            continue
                    
                    # Response is complete if we found the conclusion marker
                    if conclusion_found:
                        self.logger.log_success("Analysis conclusion marker found - response complete!")
                        response_complete = True
                        break
                    # Response is complete if chat input is editable again
                    elif chat_input_editable and (twitter_found or charts_found):
                        self.logger.log_success("Chat input is editable - response complete!")
                        response_complete = True
                        break
                    # Fallback: Response is complete if we have both Twitter text and charts
                    elif twitter_found and charts_found:
                        self.logger.log_success("Complete response received with charts")
                        response_complete = True
                        break
                    elif twitter_found:
                        # We have text but waiting for charts
                        self.logger.log_info(f"Text received, waiting for charts... ({elapsed}s elapsed)")
                        time.sleep(5)
                    else:
                        # Still waiting for any response
                        self.logger.log_info(f"Waiting for response... ({elapsed}s elapsed)")
                        time.sleep(5)
                        
                except Exception as e:
                    self.logger.log_warning(f"Error checking for response: {e}")
                    time.sleep(5)
            
            # If we exit the while loop due to timeout
            if not response_complete:
                self.logger.log_warning(f"Complete response not received within {timeout} seconds")
                if capture_after_3min:
                    self.logger.log_info("Proceeding with partial results capture")
                return False
            
            return True
            
        except Exception as e:
            self.logger.log_error(f"Failed to wait for complete response: {e}")
            return False
    
    def extract_data(self) -> Dict[str, Any]:
        """Extract all data from the chat response with comprehensive capture."""
        try:
            self.logger.log_info("📊 Extracting chat data")
            
            # Extract shareable link first
            shareable_url = self.extract_shareable_link()
            
            # Use the chat data extractor for better extraction
            from modules.chat_manager.chat_data_extractor import ChatDataExtractor
            extractor = ChatDataExtractor()
            
            # Extract data using the specialized extractor
            extraction_result = extractor.extract_from_chat_url(shareable_url)
            
            if extraction_result["success"]:
                results = {
                    "timestamp": datetime.now().isoformat(),
                    "chat_url": shareable_url if shareable_url else self.driver.current_url,
                    "response_text": extraction_result["response_text"],
                    "twitter_text": extraction_result["twitter_text"],
                    "artifacts": [],
                    "screenshots": extraction_result["screenshots"],
                    "response_metadata": {}
                }
                
                # Add artifact screenshot if available
                if extraction_result["artifact_screenshot"]:
                    artifact_info = {
                        "type": "analysis_artifact",
                        "index": 1,
                        "screenshot": extraction_result["artifact_screenshot"],
                        "selector": "artifact_page",
                        "tag_name": "page"
                    }
                    results["artifacts"].append(artifact_info)
                    results["screenshots"].append(extraction_result["artifact_screenshot"])
                
                self.logger.log_success(f"✅ Data extracted using specialized extractor: {len(results['twitter_text'])} chars Twitter, {len(results['response_text'])} chars response")
                return results
            
            # Fallback to original extraction if specialized extractor fails
            self.logger.log_warning("⚠️ Specialized extractor failed, using fallback extraction")
            
            results = {
                "timestamp": datetime.now().isoformat(),
                "chat_url": shareable_url if shareable_url else self.driver.current_url,
                "response_text": "",
                "twitter_text": "",
                "artifacts": [],
                "screenshots": [],
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
                except:
                    pass
            
            # Extract Twitter text output with new format
            twitter_selectors = [
                "//div[contains(text(), 'TWITTER_TEXT:')]",
                "//div[contains(text(), 'Add a quick 260 character summary')]",
                "//div[contains(text(), 'TWITTER_TEXT')]",
                "//div[contains(text(), '**TWITTER_TEXT**')]",
                "[data-testid='twitter-text']",
                ".twitter-text",
                ".twitter-output",
                ".message-content",
                ".chat-response",
                ".response-text",
                ".analysis-result",
                ".message",
                ".response",
                "[class*='message']",
                "[class*='response']",
                "[class*='content']",
                "div[class*='text']",
                "p",
                "span",
                "div"
            ]
            
            for selector in twitter_selectors:
                try:
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for i, element in enumerate(elements):
                        if element.is_displayed() and element.text.strip():
                            text_content = element.text.strip()
                            
                            # Look for new Twitter text format: "TWITTER_TEXT: [content]"
                            if "TWITTER_TEXT:" in text_content:
                                # Extract content after "TWITTER_TEXT:"
                                lines = text_content.split('\n')
                                twitter_content = ""
                                
                                for line in lines:
                                    if "TWITTER_TEXT:" in line:
                                        # Extract everything after "TWITTER_TEXT:"
                                        twitter_part = line.split("TWITTER_TEXT:")[1].strip()
                                        if twitter_part:
                                            twitter_content += twitter_part + " "
                                    elif twitter_content and line.strip():
                                        # Continue collecting until we hit a section break
                                        if (line.startswith("**THIS_CONCLUDES_THE_ANALYSIS**") or
                                            line.startswith("THIS_CONCLUDES_THE_ANALYSIS") or
                                            line.startswith("HTML_CHART") or 
                                            line.startswith("**HTML_CHART**") or
                                            line.startswith("View Report") or
                                            line.startswith("Based on my comprehensive analysis")):
                                            break
                                        # Skip empty lines and section headers
                                        if line.strip() and not line.startswith("**") and not line.startswith("##"):
                                            twitter_content += line.strip() + " "
                                
                                if twitter_content.strip():
                                    results["twitter_text"] = twitter_content.strip()
                                    results["response_text"] = twitter_content.strip()
                                    self.logger.log_success(f"Extracted Twitter text: {len(results['twitter_text'])} characters")
                                    break
                            
                            # Look for old TWITTER_TEXT format as fallback
                            elif "TWITTER_TEXT" in text_content or "**TWITTER_TEXT**" in text_content:
                                # Extract just the Twitter content part
                                lines = text_content.split('\n')
                                twitter_content = ""
                                in_twitter_section = False
                                
                                for line in lines:
                                    if "TWITTER_TEXT" in line or "**TWITTER_TEXT**" in line:
                                        in_twitter_section = True
                                        continue
                                    elif in_twitter_section and line.strip():
                                        # Stop at conclusion marker or other sections
                                        if (line.startswith("**THIS_CONCLUDES_THE_ANALYSIS**") or
                                            line.startswith("THIS_CONCLUDES_THE_ANALYSIS") or
                                            line.startswith("HTML_CHART") or 
                                            line.startswith("**HTML_CHART**") or
                                            line.startswith("View Report") or
                                            line.startswith("Based on my comprehensive analysis")):
                                            break
                                        # Skip empty lines and section headers
                                        if line.strip() and not line.startswith("**") and not line.startswith("##"):
                                            twitter_content += line.strip() + " "
                                
                                if twitter_content.strip():
                                    results["twitter_text"] = twitter_content.strip()
                                    results["response_text"] = twitter_content.strip()
                                    self.logger.log_success(f"Extracted Twitter text: {len(results['twitter_text'])} characters")
                                    break
                            
                            elif not results["response_text"] and len(text_content) > 50:
                                # Fallback to any substantial text content that looks like a response
                                if ("analysis" in text_content.lower() or 
                                    "stablecoin" in text_content.lower() or
                                    "market" in text_content.lower() or
                                    "data" in text_content.lower()):
                                    results["response_text"] = text_content
                                    self.logger.log_success(f"Extracted response text: {len(results['response_text'])} characters")
                                    break
                    if results["response_text"]:
                        break
                except Exception as e:
                    self.logger.log_warning(f"Error checking Twitter selector {selector}: {e}")
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
                            self.logger.log_success(f"Found right panel: {selector}")
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
                                self.logger.log_success(f"Found chart container: {selector}")
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
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    panel_screenshot = f"screenshots/charts_panel_{timestamp}.png"
                    right_panel.screenshot(panel_screenshot)
                    
                    if os.path.exists(panel_screenshot):
                        results["screenshots"].append(panel_screenshot)
                        self.logger.log_info(f"📸 Charts panel screenshot saved: {panel_screenshot}")
                        
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
                    self.logger.log_warning(f"Failed to screenshot right panel: {e}")
            
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
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            artifact_screenshot = f"screenshots/artifact_{len(results['artifacts'])+1}_{timestamp}.png"
                            
                            try:
                                element.screenshot(artifact_screenshot)
                                if os.path.exists(artifact_screenshot):
                                    artifact_info = {
                                        "type": "analysis_artifact",
                                        "index": len(results["artifacts"]) + 1,
                                        "screenshot": artifact_screenshot,
                                        "selector": selector,
                                        "tag_name": element.tag_name
                                    }
                                    results["artifacts"].append(artifact_info)
                                    results["screenshots"].append(artifact_screenshot)
                                    self.logger.log_info(f"📸 Analysis artifact {len(results['artifacts'])} screenshot saved: {artifact_screenshot}")
                            except Exception as e:
                                self.logger.log_warning(f"Failed to screenshot artifact: {e}")
                                continue
                except:
                    continue
            
            # Check if analysis conclusion marker was found
            conclusion_found = False
            try:
                conclusion_selectors = [
                    "//div[contains(text(), 'THIS_CONCLUDES_THE_ANALYSIS')]",
                    "//div[contains(text(), '**THIS_CONCLUDES_THE_ANALYSIS**')]",
                    "//span[contains(text(), 'THIS_CONCLUDES_THE_ANALYSIS')]",
                    "//p[contains(text(), 'THIS_CONCLUDES_THE_ANALYSIS')]"
                ]
                
                for selector in conclusion_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            if element.is_displayed() and element.text.strip():
                                conclusion_found = True
                                break
                        if conclusion_found:
                            break
                    except:
                        continue
            except:
                pass
            
            # Create response metadata
            results["response_metadata"] = {
                "word_count": len(results["response_text"].split()) if results["response_text"] else 0,
                "has_charts": any("chart" in a["type"] for a in results["artifacts"]),
                "has_tables": any("table" in a["type"] for a in results["artifacts"]),
                "has_code": "code" in results["response_text"].lower() if results["response_text"] else False,
                "analysis_type": "market_analysis",
                "conclusion_marker_found": conclusion_found,
                "twitter_text_format": "new" if "TWITTER_TEXT:" in results.get("response_text", "") else "old"
            }
            
            self.logger.log_success(f"✅ Data extracted: {len(results['response_text'])} chars, {len(results['artifacts'])} artifacts")
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
    
    def run_analysis(self, prompt: str, response_timeout: int = 600) -> Dict[str, Any]:
        """Run the complete analysis workflow with comprehensive features."""
        results = {
            "success": False,
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "data": {}
        }
        
        try:
            # Step 1: Initialization
            self.logger.log_info("🚀 Starting Flipside AI Analysis Workflow")
            self.logger.log_info("=" * 60)
            
            if not self.initialize():
                raise Exception("Failed to initialize automation environment")
            
            # Step 2: Authentication
            self.logger.log_info("🔐 Starting authentication")
            if not self.authenticate():
                raise Exception("Authentication failed")
            self.logger.log_success("✅ Authentication successful")
            
            # Step 3: Navigation
            self.logger.log_info("🧭 Navigating to chat page")
            if not self.navigate_to_chat():
                raise Exception("Failed to navigate to chat page")
            self.logger.log_success("✅ Successfully navigated to chat page")
            
            # Step 4: Submit Prompt
            self.logger.log_info(f"📝 Submitting prompt: {prompt[:50]}...")
            if not self.submit_prompt(prompt):
                raise Exception("Failed to submit prompt")
            self.logger.log_success("✅ Prompt submitted successfully")
            
            # Step 5: Wait for Response
            self.logger.log_info(f"⏳ Waiting for AI response (timeout: {response_timeout}s)")
            response_complete = self.wait_for_response(response_timeout)
            if not response_complete:
                self.logger.log_warning("⚠️ Response timeout, but continuing with data capture...")
            else:
                self.logger.log_success("✅ AI response completed")
            
            # Step 6: Extract Data
            self.logger.log_info("📊 Extracting analysis data")
            results["data"] = self.extract_data()
            
            # Step 7: Capture Published Artifact Screenshot
            self.logger.log_info("📸 Capturing published artifact screenshot")
            try:
                published_screenshot = self.capture_published_artifact_screenshot()
                if published_screenshot:
                    results["data"]["published_artifact_screenshot"] = published_screenshot
                    results["data"]["screenshots"].append(published_screenshot)
                    self.logger.log_success(f"✅ Published artifact screenshot: {published_screenshot}")
                else:
                    self.logger.log_warning("⚠️ Failed to capture published artifact screenshot")
            except Exception as screenshot_error:
                self.logger.log_warning(f"Error capturing published artifact screenshot: {screenshot_error}")
            
            # Step 8: Final Screenshot
            self.logger.log_info("📸 Capturing final screenshot")
            try:
                final_screenshot = self.capture_final_screenshot()
                if final_screenshot:
                    results["data"]["screenshots"].append(final_screenshot)
                    self.logger.log_success(f"✅ Final screenshot: {final_screenshot}")
            except Exception as screenshot_error:
                self.logger.log_warning(f"Failed to capture final screenshot: {screenshot_error}")
            
            # Mark as successful
            results["success"] = True
            
            # Log summary
            response_length = len(results["data"].get("response_text", ""))
            twitter_length = len(results["data"].get("twitter_text", ""))
            artifacts_count = len(results["data"].get("artifacts", []))
            screenshots_count = len(results["data"].get("screenshots", []))
            
            self.logger.log_success("🎉 Analysis workflow completed successfully!")
            self.logger.log_info(f"📊 Results Summary:")
            self.logger.log_info(f"   📝 Response text: {response_length} characters")
            self.logger.log_info(f"   🐦 Twitter text: {twitter_length} characters")
            self.logger.log_info(f"   📈 Artifacts: {artifacts_count}")
            self.logger.log_info(f"   📸 Screenshots: {screenshots_count}")
            self.logger.log_info(f"   🔗 Chat URL: {results['data'].get('chat_url', 'N/A')}")
            
        except Exception as e:
            error_msg = f"Analysis failed: {e}"
            self.logger.log_error(error_msg)
            results["error"] = error_msg
            
            # Capture error screenshot
            if self.driver:
                try:
                    error_screenshot = f"screenshots/error_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    self.driver.save_screenshot(error_screenshot)
                    self.logger.log_info(f"📸 Error screenshot saved: {error_screenshot}")
                except Exception as screenshot_error:
                    self.logger.log_error(f"Failed to capture error screenshot: {screenshot_error}")
        
        finally:
            # Cleanup
            self.logger.log_info("🧹 Cleaning up resources")
            self.cleanup()
            self.logger.log_info("🧹 Cleanup completed")
        
        return results
    
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
        """Setup standard Chrome driver with comprehensive options."""
        try:
            self.logger.log_info("Configuring Chrome WebDriver options")
            chrome_options = Options()
            
            # Headless mode for GitHub Actions
            headless_mode = os.getenv('CHROME_HEADLESS', 'false').lower() == 'true'
            if headless_mode:
                chrome_options.add_argument('--headless')
                self.logger.log_info("Headless mode enabled")
            else:
                self.logger.log_info("Headless mode disabled (visible browser)")
            
            # Window size for consistent screenshots
            window_size = os.getenv('CHROME_WINDOW_SIZE', '1920,1080')
            chrome_options.add_argument(f'--window-size={window_size}')
            self.logger.log_info(f"Window size set to: {window_size}")
            
            # Performance and stability options
            stability_options = [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',
                '--disable-web-security',
                '--allow-running-insecure-content'
            ]
            
            for option in stability_options:
                chrome_options.add_argument(option)
            
            self.logger.log_info("Applied stability options")
            
            # User agent
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            chrome_options.add_argument(f'--user-agent={user_agent}')
            
            # Logging - enable verbose logging
            chrome_options.add_argument('--enable-logging')
            chrome_options.add_argument('--log-level=0')
            chrome_options.add_argument('--v=1')
            chrome_options.add_argument('--enable-logging=stderr')
            
            # Set up ChromeDriver
            self.logger.log_info("Installing ChromeDriver")
            service = Service(ChromeDriverManager().install())
            
            # Create driver
            self.logger.log_info("Initializing Chrome WebDriver")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)
            
            self.logger.log_success("Chrome WebDriver initialized successfully")
            return driver
            
        except Exception as e:
            self.logger.log_error(f"Failed to setup Chrome WebDriver: {e}")
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
    
    def _click_view_report_buttons(self):
        """Click View Report buttons to show visuals."""
        try:
            view_report_selectors = [
                "//button[contains(text(), 'View Report')]",
                "//button[contains(text(), 'view report')]",
                "//a[contains(text(), 'View Report')]",
                "//a[contains(text(), 'view report')]",
                "[data-testid='view-report']",
                "[data-testid='View Report']",
                "[data-testid='view_report']",
                ".view-report-button",
                ".artifact-link",
                ".report-link",
                "button[class*='view']",
                "button[class*='report']",
                "a[class*='view']",
                "a[class*='report']",
                "a[href*='report']",
                "a[href*='view']"
            ]
            
            for selector in view_report_selectors:
                try:
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element_text = element.text.lower().strip()
                            element_href = (element.get_attribute('href') or '').lower()
                            
                            if ('view report' in element_text or 
                                'view' in element_text or 
                                'report' in element_text or
                                'view' in element_href or
                                'report' in element_href or
                                'view' in selector.lower() or
                                'report' in selector.lower()):
                                self.logger.log_info(f"Clicking 'View Report' button: {selector} - Text: '{element_text}'")
                                try:
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                    time.sleep(1)
                                    element.click()
                                    time.sleep(8)  # Wait longer for report to load
                                    self.logger.log_success("View Report button clicked - visuals should now be visible")
                                    break
                                except Exception as e:
                                    self.logger.log_warning(f"Failed to click View Report button: {e}")
                                    continue
                except Exception as e:
                    self.logger.log_warning(f"Error checking View Report selector {selector}: {e}")
                    continue
        except Exception as e:
            self.logger.log_warning(f"Error in _click_view_report_buttons: {e}")
    
    def close_artifact_view(self) -> bool:
        """Close the artifact view by clicking the X button to reveal the share button."""
        try:
            self.logger.log_info("Looking for artifact view close button...")
            
            close_selectors = [
                "button[aria-label*='Close']",
                "button[title*='Close']",
                "button[aria-label*='close']",
                "button[title*='close']",
                "[data-testid*='close']",
                "[data-testid*='Close']",
                "//button[contains(text(), '×')]",
                "//button[contains(text(), '✕')]",
                "//button[contains(text(), 'X')]",
                "//button[contains(text(), 'close')]",
                "//button[contains(text(), 'Close')]",
                ".close-button",
                ".artifact-close",
                ".view-close",
                ".modal-close",
                ".panel-close",
                ".header-close",
                ".toolbar-close",
                ".header button",
                ".toolbar button",
                ".modal-header button",
                ".panel-header button",
                "button"
            ]
            
            close_button = None
            for selector in close_selectors:
                try:
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for i, element in enumerate(elements):
                        if element.is_displayed() and element.is_enabled():
                            location = element.location
                            size = self.driver.get_window_size()
                            element_text = element.text.lower().strip()
                            element_title = (element.get_attribute('title') or '').lower()
                            element_aria_label = (element.get_attribute('aria-label') or '').lower()
                            element_class = (element.get_attribute('class') or '').lower()
                            
                            # Check if it's in the upper right area
                            if location['x'] > size['width'] * 0.5 and location['y'] < size['height'] * 0.4:
                                if ('close' in element_text or 
                                    'close' in element_title or
                                    'close' in element_aria_label or
                                    'close' in element_class or
                                    '×' in element_text or
                                    '✕' in element_text or
                                    'x' in element_text or
                                    'close' in selector.lower()):
                                    close_button = element
                                    self.logger.log_success(f"Found artifact close button: {selector} - Element {i}")
                                    break
                                elif location['x'] > size['width'] * 0.8 and location['y'] < size['height'] * 0.2:
                                    close_button = element
                                    self.logger.log_success(f"Found potential close button by position: {selector} - Element {i}")
                                    break
                    if close_button:
                        break
                except Exception as e:
                    self.logger.log_warning(f"Error checking close selector {selector}: {e}")
                    continue
            
            if close_button:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
                    time.sleep(1)
                    close_button.click()
                    time.sleep(3)
                    self.logger.log_success("Artifact view closed successfully")
                    return True
                except Exception as e:
                    self.logger.log_warning(f"Failed to click close button: {e}")
                    return False
            else:
                self.logger.log_info("No artifact view found or already closed")
                return True
                
        except Exception as e:
            self.logger.log_warning(f"Failed to close artifact view: {e}")
            return True
    
    def extract_shareable_link(self) -> str:
        """Extract the shareable link by clicking Share -> Public -> Copy URL."""
        try:
            self.logger.log_info("Extracting shareable link...")
            
            # First, try to close any open artifact view to reveal the share button
            self.close_artifact_view()
            
            share_selectors = [
                "button[aria-label*='Share']",
                "button[title*='Share']",
                "button[data-testid*='share']",
                "button[data-testid*='Share']",
                "//button[contains(text(), 'Share')]",
                "//button[contains(text(), 'share')]",
                ".share-button",
                "button[class*='share']",
                "button[class*='Share']",
                "button svg[data-testid*='share']",
                "button svg[data-testid*='Share']",
                ".header button",
                ".chat-header button",
                ".top-bar button",
                ".toolbar button",
                ".action-button",
                "button[class*='icon']",
                "button[role='button']",
                "button",
                "[role='button']"
            ]
            
            share_button = None
            for selector in share_selectors:
                try:
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for i, element in enumerate(elements):
                        if element.is_displayed() and element.is_enabled():
                            location = element.location
                            size = self.driver.get_window_size()
                            element_text = element.text.lower().strip()
                            element_title = (element.get_attribute('title') or '').lower()
                            element_aria_label = (element.get_attribute('aria-label') or '').lower()
                            element_class = (element.get_attribute('class') or '').lower()
                            element_data_testid = (element.get_attribute('data-testid') or '').lower()
                            
                            # Check if it's in the upper right area
                            if location['x'] > size['width'] * 0.3 and location['y'] < size['height'] * 0.5:
                                if ('share' in element_text or 
                                    'share' in element_title or 
                                    'share' in element_aria_label or
                                    'share' in element_class or
                                    'share' in element_data_testid or
                                    'share' in selector.lower()):
                                    share_button = element
                                    self.logger.log_success(f"Found Share button: {selector} - Element {i}")
                                    break
                                elif location['x'] > size['width'] * 0.7 and location['y'] < size['height'] * 0.3:
                                    if (element.size['width'] < 100 and element.size['height'] < 100) or 'icon' in element_class:
                                        share_button = element
                                        self.logger.log_success(f"Found potential Share button by position and size: {selector} - Element {i}")
                                        break
                    if share_button:
                        break
                except Exception as e:
                    self.logger.log_warning(f"Error checking selector {selector}: {e}")
                    continue
            
            if not share_button:
                self.logger.log_warning("Share button not found")
                self._capture_warning_screenshot("share_button_not_found")
                return ""
            
            # Click Share button
            share_button.click()
            time.sleep(3)
            
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
                            element_text = element.text.lower()
                            element_value = element.get_attribute("value", "").lower()
                            if 'public' in element_text or 'public' in element_value:
                                public_option = element
                                self.logger.log_success(f"Found Public option: {selector}")
                                break
                    if public_option:
                        break
                except:
                    continue
            
            if public_option:
                if public_option.get_attribute("type") == "radio" and not public_option.is_selected():
                    public_option.click()
                    time.sleep(2)
                    self.logger.log_success("Selected Public option")
                elif public_option.get_attribute("type") == "radio" and public_option.is_selected():
                    self.logger.log_info("Public option already selected")
            else:
                self.logger.log_warning("Public option not found, trying to proceed anyway")
            
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
                                self.logger.log_success(f"Found URL input: {selector}")
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
                        chat_id = shareable_url.split('/chat/')[-1]
                        shareable_url = f"https://flipsidecrypto.xyz/chat/shared/chats/{chat_id}"
                        self.logger.log_info(f"Converted to shared format: {shareable_url}")
                    else:
                        current_url = self.driver.current_url
                        if '/chat/' in current_url:
                            chat_id = current_url.split('/chat/')[-1]
                            shareable_url = f"https://flipsidecrypto.xyz/chat/shared/chats/{chat_id}"
                            self.logger.log_info(f"Constructed from current URL: {shareable_url}")
                
                self.logger.log_success(f"Extracted shareable URL: {shareable_url}")
                
                # Close the modal
                try:
                    self.driver.find_element(By.TAG_NAME, "body").click()
                    time.sleep(1)
                except:
                    pass
                
                return shareable_url
            else:
                self.logger.log_warning("URL input field not found")
                self._capture_warning_screenshot("url_input_not_found")
                # Always construct URL from current page URL in shared format
                current_url = self.driver.current_url
                if '/chat/' in current_url:
                    chat_id = current_url.split('/chat/')[-1]
                    constructed_url = f"https://flipsidecrypto.xyz/chat/shared/chats/{chat_id}"
                    self.logger.log_info(f"Constructed shareable URL: {constructed_url}")
                    return constructed_url
                return ""
                
        except Exception as e:
            self.logger.log_error(f"Failed to extract shareable link: {e}")
            return ""
    
    def _try_copy_response(self) -> bool:
        """Try to find and click the copy button to get the full response."""
        try:
            self.logger.log_info("Looking for copy button...")
            
            copy_selectors = [
                "button[aria-label*='Copy']",
                "button[title*='Copy']",
                "button[data-testid*='copy']",
                "button[data-testid*='Copy']",
                "//button[contains(text(), 'Copy')]",
                "//button[contains(text(), 'copy')]",
                ".copy-button",
                "button[class*='copy']",
                "button[class*='Copy']",
                "button svg[data-testid*='copy']",
                "button svg[data-testid*='Copy']",
                "//button[contains(@class, 'action-button') and contains(text(), 'Copy')]",
                "//button[contains(@class, 'action-button') and contains(text(), 'copy')]",
                "//button[contains(@class, 'icon') and contains(text(), 'Copy')]",
                "//button[contains(@class, 'icon') and contains(text(), 'copy')]",
                "button[class*='action']",
                ".message-actions button",
                ".response-actions button",
                ".chat-actions button"
            ]
            
            copy_button = None
            for selector in copy_selectors:
                try:
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for i, element in enumerate(elements):
                        if element.is_displayed() and element.is_enabled():
                            element_text = element.text.lower().strip()
                            element_title = (element.get_attribute('title') or '').lower()
                            element_aria_label = (element.get_attribute('aria-label') or '').lower()
                            element_class = (element.get_attribute('class') or '').lower()
                            element_data_testid = (element.get_attribute('data-testid') or '').lower()
                            
                            if ('copy' in element_text or 
                                'copy' in element_title or 
                                'copy' in element_aria_label or
                                'copy' in element_class or
                                'copy' in element_data_testid or
                                'copy' in selector.lower()):
                                copy_button = element
                                self.logger.log_success(f"Found copy button: {selector} - Element {i}")
                                break
                    if copy_button:
                        break
                except Exception as e:
                    self.logger.log_warning(f"Error checking copy selector {selector}: {e}")
                    continue
            
            if copy_button:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", copy_button)
                    time.sleep(1)
                    copy_button.click()
                    time.sleep(2)
                    self.logger.log_success("Copy button clicked")
                    return True
                except Exception as e:
                    self.logger.log_warning(f"Failed to click copy button: {e}")
                    return False
            else:
                self.logger.log_info("Copy button not found")
                return False
                
        except Exception as e:
            self.logger.log_warning(f"Failed to use copy button: {e}")
            return False
    
    def _capture_warning_screenshot(self, warning_type: str):
        """Capture a screenshot when a warning or error occurs."""
        try:
            if self.driver:
                screenshot_path = f"screenshots/warning_{warning_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(screenshot_path)
                self.logger.log_info(f"📸 Warning screenshot saved: {screenshot_path}")
        except Exception as e:
            self.logger.log_warning(f"Failed to capture warning screenshot: {e}")
    
    def capture_published_artifact_screenshot(self) -> Optional[str]:
        """Capture a screenshot of the published artifact by following Publish -> View -> New Window workflow."""
        self.logger.log_info("📸 Starting published artifact screenshot workflow...")
        
        try:
            # Step 1: Look for and click the Publish button
            self.logger.log_info("🔍 Looking for Publish button...")
            
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
                                location = element.location
                                size = self.driver.get_window_size()
                                if location['x'] > size['width'] * 0.5:  # Right half of screen
                                    publish_button = element
                                    self.logger.log_info(f"✅ Found Publish button: '{text}' at x={location['x']}, y={location['y']}")
                                    break
                    if publish_button:
                        break
                except Exception as e:
                    self.logger.log_warning(f"Publish selector {selector} failed: {e}")
                    continue
            
            if publish_button:
                self.logger.log_info("📤 Clicking Publish button...")
                self.driver.execute_script("arguments[0].click();", publish_button)
                time.sleep(5)
            else:
                self.logger.log_info("ℹ️ Publish button not found, assuming already published")
            
            # Step 2: Look for and click the View button
            self.logger.log_info("🔍 Looking for View button...")
            
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
                                location = element.location
                                size = self.driver.get_window_size()
                                if location['x'] > size['width'] * 0.5:  # Right half of screen
                                    view_button = element
                                    self.logger.log_info(f"✅ Found View button: '{text}' at x={location['x']}, y={location['y']}")
                                    break
                    if view_button:
                        break
                except Exception as e:
                    self.logger.log_warning(f"View selector {selector} failed: {e}")
                    continue
            
            if not view_button:
                self.logger.log_error("❌ View button not found")
                return None
            
            # Step 3: Get current window handles before clicking View
            original_window = self.driver.current_window_handle
            self.logger.log_info(f"📋 Original window handle: {original_window}")
            
            # Step 4: Click the View button
            self.logger.log_info("👁️ Clicking View button...")
            self.driver.execute_script("arguments[0].click();", view_button)
            time.sleep(3)
            
            # Step 5: Get all window handles after clicking View
            all_windows = self.driver.window_handles
            self.logger.log_info(f"📋 All window handles after click: {all_windows}")
            
            # Step 6: Find and switch to the new window
            new_window = None
            for window in all_windows:
                if window != original_window:
                    new_window = window
                    break
            
            if not new_window:
                self.logger.log_error("❌ No new window opened")
                return None
            
            # Step 7: Switch to the new window
            self.logger.log_info(f"🔄 Switching to new window: {new_window}")
            self.driver.switch_to.window(new_window)
            
            # Step 8: Wait for the new page to load
            self.logger.log_info("⏳ Waiting for new page to load...")
            time.sleep(10)
            
            # Step 9: Take screenshot of the new window
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = f"screenshots/published_artifact_{timestamp}.png"
            
            self.logger.log_info("📸 Taking screenshot of published artifact...")
            self.driver.save_screenshot(screenshot_path)
            
            # Step 10: Get file details and return path
            if os.path.exists(screenshot_path):
                file_size = os.path.getsize(screenshot_path)
                self.logger.log_info(f"✅ Published artifact screenshot saved: {screenshot_path}")
                self.logger.log_info(f"📁 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                
                if file_size < 5 * 1024 * 1024:  # Under 5MB
                    self.logger.log_info("✅ Twitter-friendly file size")
                else:
                    self.logger.log_warning("⚠️ Large file size for Twitter")
                
                return screenshot_path
            else:
                self.logger.log_error("❌ Screenshot file was not created")
                return None
                
        except Exception as e:
            self.logger.log_error(f"❌ Error during published artifact screenshot: {e}")
            return None
