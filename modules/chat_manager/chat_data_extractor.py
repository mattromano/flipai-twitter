"""
Chat Data Extractor

A focused module for extracting Twitter text and capturing artifacts from a completed chat.
"""

import os
import time
import re
import json
from typing import Dict, Any, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    import pyperclip
except ImportError:
    pyperclip = None

from modules.shared.authentication import StealthAuthenticator
from modules.shared.logger import AutomationLogger


class ChatDataExtractor:
    """Extracts Twitter text and captures artifacts from a completed chat."""
    
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.authenticator: Optional[StealthAuthenticator] = None
        self.logger = AutomationLogger()
        self._driver_owned_by_extractor: bool = False  # Track if we created the driver or it was passed in
        self._authenticator_owned_by_extractor: bool = False  # Track if we created the authenticator or it was passed in
        
        # Setup directories
        os.makedirs("screenshots", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
    
    def _is_user_message(self, element) -> bool:
        """Check if an element is part of a user message (not assistant response)."""
        try:
            # Use JavaScript to traverse up the DOM tree and check for data-message-role="user"
            script = """
            var element = arguments[0];
            var current = element;
            var maxDepth = 10;
            var depth = 0;
            
            while (current && depth < maxDepth) {
                var role = current.getAttribute('data-message-role');
                if (role === 'user') {
                    return true;
                }
                // Also check if element is inside a container with data-message-role="user"
                var parent = current.parentElement;
                if (!parent) break;
                current = parent;
                depth++;
            }
            return false;
            """
            is_user = self.driver.execute_script(script, element)
            return bool(is_user)
        except Exception as e:
            # If JavaScript check fails, fallback to checking the element directly
            try:
                role = element.get_attribute("data-message-role")
                if role == "user":
                    return True
            except:
                pass
            return False
    
    def extract_from_chat_url(self, chat_url: str, pre_extracted_twitter_text: str = "") -> Dict[str, Any]:
        """Extract Twitter text and capture artifacts from a chat URL.
        
        Args:
            chat_url: The URL of the chat to extract data from
            pre_extracted_twitter_text: Optional pre-extracted Twitter text (skips extraction if provided)
        """
        results = {
            "success": False,
            "error": None,
            "timestamp": datetime.now().isoformat(),
            "chat_url": chat_url,
            "artifact_url": "",
            "twitter_text": "",
            "response_text": "",
            "artifact_screenshot": "",
            "screenshots": []
        }
        
        try:
            self.logger.log_info(f"🔍 Extracting data from chat: {chat_url}")
            
            # Step 1: Setup and authenticate
            if not self._setup_and_authenticate():
                raise Exception("Failed to setup and authenticate")
            
            # Step 2: Convert shared URL to non-shared URL for artifact viewing
            non_shared_url = self._convert_to_non_shared_url(chat_url)
            self.logger.log_info(f"🔄 Using non-shared URL for artifact viewing: {non_shared_url}")
            
            # Step 3: Navigate to non-shared chat (skip if already on the page)
            # Check if we're already on the correct page
            current_url = self.driver.current_url if self.driver else ""
            if non_shared_url not in current_url and chat_url not in current_url:
                if not self._navigate_to_chat(non_shared_url):
                    raise Exception("Failed to navigate to chat")
            else:
                self.logger.log_info("ℹ️ Already on the correct chat page, skipping navigation")
            
            # Step 4: Extract Twitter text (skip if pre-extracted)
            if pre_extracted_twitter_text:
                self.logger.log_info("ℹ️ Using pre-extracted Twitter text, skipping extraction")
                results["twitter_text"] = pre_extracted_twitter_text
            else:
                twitter_text = self._extract_twitter_text()
                results["twitter_text"] = twitter_text
            
            # Step 5: Extract full response text
            response_text = self._extract_response_text()
            results["response_text"] = response_text
            
            # Step 6: Capture artifact screenshot (this will open new window)
            artifact_result = self._capture_artifact_screenshot()
            if isinstance(artifact_result, dict):
                artifact_screenshot = artifact_result.get("screenshot", "")
                artifact_url = artifact_result.get("artifact_url", "")
            else:
                # Backward compatibility: if it returns a string (screenshot path)
                artifact_screenshot = artifact_result
                artifact_url = getattr(self, 'artifact_url', '')
            
            results["artifact_screenshot"] = artifact_screenshot
            results["artifact_url"] = artifact_url
            if artifact_screenshot:
                results["screenshots"].append(artifact_screenshot)
            
            # Step 7: Take final screenshot of main chat
            final_screenshot = self._capture_final_screenshot()
            if final_screenshot:
                results["screenshots"].append(final_screenshot)
            
            results["success"] = True
            self.logger.log_success("✅ Data extraction completed successfully")
            
        except Exception as e:
            error_msg = f"Data extraction failed: {e}"
            self.logger.log_error(error_msg)
            results["error"] = error_msg
            
            # Capture error screenshot
            if self.driver:
                try:
                    error_screenshot = f"screenshots/error_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    self.driver.save_screenshot(error_screenshot)
                    results["screenshots"].append(error_screenshot)
                except:
                    pass
        
        finally:
            self._cleanup()
        
        return results
    
    def _convert_to_non_shared_url(self, chat_url: str) -> str:
        """Convert shared chat URL to non-shared URL for artifact viewing."""
        try:
            # Extract chat ID from shared URL
            if "/shared/chats/" in chat_url:
                chat_id = chat_url.split("/shared/chats/")[-1]
                non_shared_url = f"https://flipsidecrypto.xyz/chat/{chat_id}"
                self.logger.log_info(f"🔄 Converted shared URL to: {non_shared_url}")
                return non_shared_url
            else:
                # Already non-shared
                self.logger.log_info("ℹ️ URL is already non-shared")
                return chat_url
        except Exception as e:
            self.logger.log_warning(f"URL conversion failed: {e}")
            return chat_url
    
    def _setup_and_authenticate(self) -> bool:
        """Setup driver and authenticate."""
        try:
            # Check if driver/authenticator were provided externally
            driver_provided = self.driver is not None
            authenticator_provided = self.authenticator is not None
            
            # If driver is already set (e.g., passed from FlipsideChatManager), skip setup
            if driver_provided:
                self.logger.log_info("ℹ️ Driver already set, skipping authentication setup")
                self._driver_owned_by_extractor = False  # Driver was passed in, don't clean it up
                # If authenticator was also provided, we don't own it. If not provided, we don't own it either (we didn't create it)
                self._authenticator_owned_by_extractor = False  # Don't clean up authenticator if driver was provided externally
                return True
            
            self.logger.log_info("🤖 Setting up stealth authentication")
            
            self.authenticator = StealthAuthenticator(self.logger)
            self._authenticator_owned_by_extractor = True  # We created the authenticator, we should clean it up
            
            if not self.authenticator.setup_driver():
                self.logger.log_error("❌ Failed to setup stealth driver")
                return False
            
            self.driver = self.authenticator.driver
            self._driver_owned_by_extractor = True  # We created the driver, we should clean it up
            
            if not self.authenticator.login():
                self.logger.log_error("❌ Failed to authenticate")
                return False
            
            self.logger.log_success("✅ Authentication successful")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Setup and authentication failed: {e}")
            return False
    
    def _navigate_to_chat(self, chat_url: str) -> bool:
        """Navigate to the specific chat URL."""
        try:
            self.logger.log_info(f"🧭 Navigating to chat: {chat_url}")
            
            self.driver.get(chat_url)
            time.sleep(5)
            
            # Wait for page to load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Take screenshot for debugging
            screenshot_path = f"screenshots/chat_loaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(screenshot_path)
            self.logger.log_info(f"📸 Chat loaded screenshot: {screenshot_path}")
            
            self.logger.log_success("✅ Successfully navigated to chat")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Navigation failed: {e}")
            return False
    
    def _extract_twitter_text(self) -> str:
        """Extract Twitter text from the chat."""
        try:
            self.logger.log_info("🐦 Extracting Twitter text")
            
            # First, take a screenshot for debugging
            debug_screenshot = f"screenshots/twitter_extraction_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(debug_screenshot)
            self.logger.log_info(f"📸 Debug screenshot saved: {debug_screenshot}")
            
            # Look for the new Twitter text format with comprehensive selectors (excluding user messages)
            twitter_selectors = [
                "//div[contains(text(), 'TWITTER_TEXT:') and not(ancestor::*[@data-message-role='user'])]",
                "//div[contains(text(), 'Add a quick 260 character summary') and not(ancestor::*[@data-message-role='user'])]",
                "//span[contains(text(), 'TWITTER_TEXT:') and not(ancestor::*[@data-message-role='user'])]",
                "//p[contains(text(), 'TWITTER_TEXT:') and not(ancestor::*[@data-message-role='user'])]",
                "//*[contains(text(), 'TWITTER_TEXT:') and not(ancestor::*[@data-message-role='user'])]",
                "//*[contains(text(), 'Add a quick 260 character summary') and not(ancestor::*[@data-message-role='user'])]"
            ]
            
            for selector in twitter_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    self.logger.log_debug(f"Found {len(elements)} elements for selector: {selector}")
                    
                    for i, element in enumerate(elements):
                        # Skip user messages - only process assistant responses
                        if self._is_user_message(element):
                            self.logger.log_debug(f"Skipping element {i} - user message")
                            continue
                            
                        if element.is_displayed() and element.text.strip():
                            text_content = element.text.strip()
                            self.logger.log_debug(f"Element {i} text: {text_content[:100]}...")
                            
                            # Extract content after "TWITTER_TEXT:"
                            if "TWITTER_TEXT:" in text_content:
                                lines = text_content.split('\n')
                                twitter_content = ""
                                
                                for line in lines:
                                    if "TWITTER_TEXT:" in line:
                                        # Use regex to extract content after "TWITTER_TEXT:" and clean it up
                                        # This handles emoji and unicode characters properly
                                        twitter_match = re.search(r'TWITTER_TEXT:\s*[^\w]*([^**\n]+)', line)
                                        if twitter_match:
                                            twitter_part = twitter_match.group(1).strip()
                                            # Remove any remaining emoji/unicode characters
                                            twitter_part = re.sub(r'[\ud83c-\udbff\udc00-\udfff]', '', twitter_part).strip()
                                            if twitter_part:
                                                twitter_content += twitter_part + "\n"
                                        else:
                                            # Fallback to simple split if regex fails
                                            twitter_part = line.split("TWITTER_TEXT:")[1].strip()
                                            # Remove emoji and extra characters
                                            twitter_part = re.sub(r'[\ud83c-\udbff\udc00-\udfff]', '', twitter_part).strip()
                                            if twitter_part:
                                                twitter_content += twitter_part + "\n"
                                    elif twitter_content and line.strip():
                                        # Continue collecting until we hit a section break
                                        if (line.startswith("**THIS_CONCLUDES_THE_ANALYSIS**") or
                                            line.startswith("THIS_CONCLUDES_THE_ANALYSIS") or
                                            line.startswith("HTML_CHART") or 
                                            line.startswith("**HTML_CHART**") or
                                            line.startswith("View Report") or
                                            line.startswith("Based on my comprehensive analysis")):
                                            break
                                        # Skip empty lines and section headers, but preserve bullet points
                                        if line.strip() and not line.startswith("**") and not line.startswith("##"):
                                            # Preserve bullet point formatting
                                            if line.strip().startswith(("•", "-", "*", "◦", "▪", "▫")):
                                                twitter_content += line.strip() + "\n"
                                            else:
                                                twitter_content += line.strip() + " "
                                
                                if twitter_content.strip():
                                    # Clean up the final result
                                    clean_twitter_text = twitter_content.strip()
                                    # Remove any remaining "TWITTER_TEXT:" prefix
                                    if clean_twitter_text.startswith("TWITTER_TEXT:"):
                                        clean_twitter_text = clean_twitter_text[12:].strip()
                                    # Remove emoji and clean up, but preserve line breaks for bullet points
                                    clean_twitter_text = re.sub(r'[\ud83c-\udbff\udc00-\udfff]', '', clean_twitter_text).strip()
                                    # Normalize bullet points to use consistent formatting
                                    clean_twitter_text = self._normalize_bullet_points(clean_twitter_text)
                                    # Convert inline bullet points to separate lines
                                    clean_twitter_text = self._convert_inline_bullets_to_lines(clean_twitter_text)
                                    self.logger.log_success(f"✅ Extracted Twitter text with bullet points: {len(clean_twitter_text)} characters")
                                    return clean_twitter_text
                except Exception as e:
                    self.logger.log_debug(f"Twitter selector {selector} failed: {e}")
                    continue
            
            # Fallback: Look for any text that might be Twitter content
            self.logger.log_info("🔍 Trying fallback Twitter text extraction")
            try:
                # Look for text containing "260 character" or similar (excluding user messages)
                twitter_fallback_selectors = [
                    "//div[contains(text(), '260') and not(ancestor::*[@data-message-role='user'])]",
                    "//div[contains(text(), 'character') and not(ancestor::*[@data-message-role='user'])]",
                    "//div[contains(text(), 'summary') and not(ancestor::*[@data-message-role='user'])]",
                    "//*[contains(text(), '260') and not(ancestor::*[@data-message-role='user'])]",
                    "//*[contains(text(), 'character') and not(ancestor::*[@data-message-role='user'])]"
                ]
                
                for selector in twitter_fallback_selectors:
                    try:
                        elements = self.driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            # Skip user messages - only process assistant responses
                            if self._is_user_message(element):
                                continue
                                
                            if element.is_displayed() and element.text.strip():
                                text_content = element.text.strip()
                                if len(text_content) > 50 and len(text_content) < 300:
                                    self.logger.log_info(f"✅ Found potential Twitter text: {len(text_content)} characters")
                                    return text_content
                    except:
                        continue
            except:
                pass
            
            # Last resort: Look for any substantial text that might be the analysis
            self.logger.log_info("🔍 Trying last resort text extraction")
            try:
                # Get all text content from the page
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                
                # Look for patterns that might indicate Twitter content
                lines = page_text.split('\n')
                for i, line in enumerate(lines):
                    if "TWITTER_TEXT:" in line:
                        # Found the Twitter text line, collect following lines
                        twitter_content = ""
                        for j in range(i, min(i + 10, len(lines))):  # Look at next 10 lines
                            current_line = lines[j].strip()
                            if current_line and not current_line.startswith("**") and not current_line.startswith("##"):
                                if "THIS_CONCLUDES_THE_ANALYSIS" in current_line:
                                    break
                                twitter_content += current_line + " "
                        
                        if twitter_content.strip():
                            # Clean up the final result
                            clean_twitter_text = twitter_content.strip()
                            # Remove any remaining "TWITTER_TEXT:" prefix
                            if clean_twitter_text.startswith("TWITTER_TEXT:"):
                                clean_twitter_text = clean_twitter_text[12:].strip()
                            # Remove emoji and clean up
                            clean_twitter_text = re.sub(r'[\ud83c-\udbff\udc00-\udfff]', '', clean_twitter_text).strip()
                            self.logger.log_success(f"✅ Extracted Twitter text from page text: {len(clean_twitter_text)} characters")
                            return clean_twitter_text
            except Exception as e:
                self.logger.log_debug(f"Last resort extraction failed: {e}")
            
            self.logger.log_warning("⚠️ No Twitter text found")
            return ""
            
        except Exception as e:
            self.logger.log_error(f"Twitter text extraction failed: {e}")
            return ""
    
    def _normalize_bullet_points(self, text: str) -> str:
        """Normalize bullet points to use consistent formatting for Twitter."""
        try:
            lines = text.split('\n')
            normalized_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if line starts with a bullet point
                if line.startswith(("•", "-", "*", "◦", "▪", "▫")):
                    # Normalize to use bullet point symbol with proper spacing
                    if line.startswith(("-", "*")):
                        line = "• " + line[1:].strip()
                    elif line.startswith(("◦", "▪", "▫")):
                        line = "• " + line[1:].strip()
                    elif line.startswith("•") and not line.startswith("• "):
                        line = "• " + line[1:].strip()
                    normalized_lines.append(line)
                else:
                    normalized_lines.append(line)
            
            return '\n'.join(normalized_lines)
            
        except Exception as e:
            self.logger.log_debug(f"Bullet point normalization failed: {e}")
            return text
    
    def _convert_inline_bullets_to_lines(self, text: str) -> str:
        """Convert inline bullet points to separate lines."""
        try:
            # Look for patterns like "• item1 • item2 • item3"
            # Split on bullet points that are not at the start of a line
            lines = text.split('\n')
            converted_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line contains multiple bullet points (inline format)
                if line.count('•') > 1 and not line.startswith('•'):
                    # Split on bullet points and create separate lines
                    parts = line.split('•')
                    for i, part in enumerate(parts):
                        part = part.strip()
                        if part:
                            if i == 0:
                                # First part (before first bullet)
                                converted_lines.append(part)
                            else:
                                # Parts after bullets
                                converted_lines.append('• ' + part)
                else:
                    # Single line or already properly formatted
                    converted_lines.append(line)
            
            return '\n'.join(converted_lines)
            
        except Exception as e:
            self.logger.log_debug(f"Inline bullet conversion failed: {e}")
            return text
    
    def _extract_response_text(self) -> str:
        """Extract the full response text from the chat."""
        try:
            self.logger.log_info("📝 Extracting response text")
            
            # Look for the main chat content area
            content_selectors = [
                ".message-content",
                ".chat-response",
                ".response-text",
                ".analysis-result",
                ".message",
                ".response",
                "[class*='message']",
                "[class*='response']",
                "[class*='content']"
            ]
            
            for selector in content_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.text.strip():
                            text_content = element.text.strip()
                            # Look for substantial content (not just navigation)
                            if len(text_content) > 100 and not any(nav_word in text_content.lower() for nav_word in [
                                "toggle sidebar", "start a chat", "artifacts", "rules", "recent chats"
                            ]):
                                self.logger.log_success(f"✅ Extracted response text: {len(text_content)} characters")
                                return text_content
                except Exception as e:
                    self.logger.log_debug(f"Content selector {selector} failed: {e}")
                    continue
            
            self.logger.log_warning("⚠️ No substantial response text found")
            return ""
            
        except Exception as e:
            self.logger.log_error(f"Response text extraction failed: {e}")
            return ""
    
    def _capture_artifact_screenshot(self) -> str:
        """Capture artifact screenshot by clicking publish button, copying link from clipboard, and navigating to it."""
        try:
            self.logger.log_info("📸 Capturing artifact screenshot")
            
            # Step 1: Intercept clipboard copy using JavaScript before clicking publish
            self.logger.log_info("🔧 Setting up clipboard interception")
            clipboard_intercepted = False
            try:
                # Inject code to intercept clipboard.writeText calls and store the value
                self.driver.execute_script("""
                    window.__intercepted_clipboard_url = null;
                    const originalWriteText = navigator.clipboard.writeText.bind(navigator.clipboard);
                    navigator.clipboard.writeText = function(text) {
                        console.log('Intercepted clipboard.writeText:', text);
                        window.__intercepted_clipboard_url = text;
                        return originalWriteText(text);
                    };
                """)
                clipboard_intercepted = True
                self.logger.log_success("✅ Clipboard interception set up")
            except Exception as e:
                self.logger.log_warning(f"⚠️ Could not set up clipboard interception: {e}")
            
            # Initialize variables
            artifact_url = None
            copy_link_button = None
            
            # Step 2: Look for and click the Publish button (this will copy link to clipboard automatically)
            publish_button = self._find_publish_button()
            if publish_button:
                self.logger.log_info("📤 Clicking Publish button (will copy link to clipboard)")
                self.driver.execute_script("arguments[0].click();", publish_button)
                time.sleep(3)  # Wait for publish to complete and button to transform
                
                # Try to read the intercepted URL first
                if clipboard_intercepted:
                    try:
                        intercepted_url = self.driver.execute_script("return window.__intercepted_clipboard_url")
                        if intercepted_url and 'flipsidecrypto.xyz' in intercepted_url:
                            self.logger.log_success(f"✅ Got artifact URL from clipboard interception: {intercepted_url}")
                            artifact_url = intercepted_url
                            # Skip to navigation
                            self.logger.log_info(f"🔗 Extracted artifact URL: {artifact_url}")
                            # Store artifact_url as instance variable
                            self.artifact_url = artifact_url
                            self.logger.log_info("🧭 Navigating to artifact URL")
                            self.driver.get(artifact_url)
                            time.sleep(5)
                            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                            screenshot_path = self._continue_artifact_screenshot()
                            # Return both screenshot path and artifact URL
                            return {
                                "screenshot": screenshot_path,
                                "artifact_url": artifact_url
                            }
                    except Exception as e:
                        self.logger.log_warning(f"⚠️ Could not read intercepted clipboard: {e}")
                
                # Wait for Copy link button to appear (up to 10 seconds)
                self.logger.log_info("⏳ Waiting for Copy link button to appear after publish...")
                for attempt in range(10):
                    copy_link_button = self._find_copy_link_button()
                    if copy_link_button:
                        self.logger.log_success(f"✅ Copy link button appeared after {attempt + 1} second(s)")
                        break
                    time.sleep(1)
            else:
                self.logger.log_info("ℹ️ Publish button not found, assuming already published")
            
            # Step 3: Read the artifact URL from clipboard (if we didn't get it from interception)
            if not artifact_url:
                artifact_url = self._extract_artifact_url_from_clipboard()
            
            # Step 4: If clipboard reading failed, try clicking the Copy link button (appears after publish)
            if not artifact_url:
                self.logger.log_info("🔄 Clipboard empty, looking for Copy link button...")
                if not copy_link_button:
                    copy_link_button = self._find_copy_link_button()
                    
                if copy_link_button:
                    self.logger.log_info("🔗 Clicking Copy link button (will copy link to clipboard)")
                    self.driver.execute_script("arguments[0].click();", copy_link_button)
                    time.sleep(2)  # Wait for clipboard copy to complete
                    # Try reading from clipboard again
                    artifact_url = self._extract_artifact_url_from_clipboard()
            
            # Step 5: Final fallback - Try extracting from View button
            if not artifact_url:
                self.logger.log_warning("⚠️ Could not read URL from clipboard, trying View button extraction...")
                artifact_url = self._extract_artifact_url()
            
            if not artifact_url:
                self.logger.log_error("❌ Could not extract artifact URL")
                return {"screenshot": "", "artifact_url": ""}
            
            self.logger.log_info(f"🔗 Extracted artifact URL: {artifact_url}")
            
            # Store artifact_url as instance variable for access later
            self.artifact_url = artifact_url
            
            # Step 6: Navigate directly to the artifact URL
            self.logger.log_info("🧭 Navigating to artifact URL")
            self.driver.get(artifact_url)
            time.sleep(5)
            
            # Wait for page to load
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            screenshot_path = self._continue_artifact_screenshot()
            # Return both screenshot path and artifact URL
            return {
                "screenshot": screenshot_path,
                "artifact_url": artifact_url
            }
            
        except Exception as e:
            self.logger.log_error(f"Artifact screenshot capture failed: {e}")
            return {"screenshot": "", "artifact_url": ""}
    
    def _continue_artifact_screenshot(self) -> str:
        """Continue artifact screenshot after navigation."""
        try:
            # Wait for artifact title to appear (e.g., "Chain Health Radar")
            self.logger.log_info("⏳ Waiting for artifact title to load...")
            try:
                WebDriverWait(self.driver, 15).until(
                    lambda d: "Chain Health" in d.page_source or "Health Radar" in d.page_source or len(d.find_elements(By.TAG_NAME, "h1")) > 0
                )
                self.logger.log_info("✅ Artifact title detected")
            except:
                self.logger.log_warning("⚠️ Title not found, proceeding anyway")
            
            time.sleep(3)  # Additional wait for all content to render
            
            # Step 6: Scroll through entire page to ensure all content loads
            self.logger.log_info("📜 Scrolling through page to load all content...")
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_pause = 1
            max_scrolls = 10
            scroll_count = 0
            
            while scroll_count < max_scrolls:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_count += 1
            
            # Scroll back to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # Step 7: Get full page dimensions and set window size
            total_width = self.driver.execute_script("return Math.max(document.body.scrollWidth, document.documentElement.scrollWidth);")
            total_height = self.driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);")
            
            self.logger.log_info(f"📏 Full page dimensions: {total_width}x{total_height}")
            
            # Set window to full page size with buffer
            adjusted_height = total_height + 200  # Extra buffer for header/footer
            self.driver.set_window_size(max(total_width, 1200), adjusted_height)
            time.sleep(2)
            
            # Scroll to top one more time to ensure we start from beginning
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Step 8: Take full page screenshot of the artifact
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = f"screenshots/artifact_{timestamp}.png"
            
            self.logger.log_info("📸 Taking full page screenshot...")
            self.driver.save_screenshot(screenshot_path)
            
            self.logger.log_success(f"✅ Full page screenshot captured: {screenshot_path}")
            self.logger.log_info(f"📐 Screenshot size: {total_width}x{adjusted_height}")
            
            # Step 10: Get file details and return path
            if os.path.exists(screenshot_path):
                file_size = os.path.getsize(screenshot_path)
                self.logger.log_success(f"✅ Artifact screenshot saved: {screenshot_path}")
                self.logger.log_info(f"📁 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                
                # Log screenshot dimensions for verification
                try:
                    from PIL import Image
                    with Image.open(screenshot_path) as img:
                        width, height = img.size
                        self.logger.log_info(f"📐 Screenshot dimensions: {width}x{height}")
                except ImportError:
                    self.logger.log_info("ℹ️ PIL not available for dimension verification")
                except Exception as e:
                    self.logger.log_debug(f"Could not get image dimensions: {e}")
                
                return screenshot_path
            else:
                self.logger.log_error("❌ Screenshot file was not created")
                return ""
                
        except Exception as e:
            self.logger.log_error(f"❌ Error during artifact screenshot: {e}")
            return ""
    
    def _extract_artifact_url(self) -> str:
        """Extract the artifact URL from the View button or page."""
        try:
            self.logger.log_info("🔍 Extracting artifact URL")
            
            # Method 1: Look for href attribute in View button
            view_button = self._find_view_button()
            if view_button:
                try:
                    # Check if it's a link
                    href = view_button.get_attribute("href")
                    if href and "artifacts" in href and not href.endswith('/artifacts'):
                        self.logger.log_success(f"✅ Found artifact URL in View button href: {href}")
                        return href
                    
                    # Check parent elements for href
                    parent = view_button.find_element(By.XPATH, "..")
                    href = parent.get_attribute("href")
                    if href and "artifacts" in href and not href.endswith('/artifacts'):
                        self.logger.log_success(f"✅ Found artifact URL in parent href: {href}")
                        return href
                    
                    # Check for onclick or data attributes that might contain the URL
                    onclick = view_button.get_attribute("onclick")
                    if onclick and "artifacts" in onclick:
                        # Extract URL from onclick JavaScript
                        url_match = re.search(r'https://flipsidecrypto\.xyz/chat/shared/artifacts/[^"\s]+-[a-zA-Z0-9]+', onclick)
                        if url_match:
                            artifact_url = url_match.group(0)
                            self.logger.log_success(f"✅ Found artifact URL in View button onclick: {artifact_url}")
                            return artifact_url
                    
                    # Check data attributes
                    for attr in ["data-url", "data-href", "data-link", "data-artifact-url"]:
                        value = view_button.get_attribute(attr)
                        if value and "artifacts" in value and not value.endswith('/artifacts'):
                            self.logger.log_success(f"✅ Found artifact URL in View button {attr}: {value}")
                            return value
                            
                except Exception as e:
                    self.logger.log_debug(f"Could not extract href from View button: {e}")
            
            # Method 2: Look for any links containing "artifacts" in the page
            try:
                artifact_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'artifacts')]")
                for link in artifact_links:
                    href = link.get_attribute("href")
                    if href and "artifacts" in href and not href.endswith('/artifacts'):
                        # Check if it matches the specific pattern with title and hash
                        if re.search(r'/shared/artifacts/[^/]+-[a-zA-Z0-9]+', href):
                            self.logger.log_success(f"✅ Found specific artifact URL in page links: {href}")
                            return href
            except Exception as e:
                self.logger.log_debug(f"Could not find artifact links: {e}")
            
            # Method 3: Look for data attributes or other indicators
            try:
                # Look for elements with data attributes that might contain the URL
                elements_with_data = self.driver.find_elements(By.XPATH, "//*[@data-url or @data-href or @data-link]")
                for element in elements_with_data:
                    for attr in ["data-url", "data-href", "data-link"]:
                        value = element.get_attribute(attr)
                        if value and "artifacts" in value:
                            self.logger.log_success(f"✅ Found artifact URL in data attribute: {value}")
                            return value
            except Exception as e:
                self.logger.log_debug(f"Could not find data attributes: {e}")
            
            # Method 4: Try clicking the View button and monitoring for URL changes
            try:
                self.logger.log_info("🔍 Trying to click View button and monitor for URL changes...")
                
                view_button = self._find_view_button()
                if view_button:
                    # Get current URL before clicking
                    current_url = self.driver.current_url
                    self.logger.log_info(f"📋 Current URL before click: {current_url}")
                    
                    # Try to intercept the click and see what happens
                    try:
                        # Try different click methods
                        self.logger.log_info("🖱️ Trying different click methods...")
                        
                        # Method 1: JavaScript click
                        self.driver.execute_script("arguments[0].click();", view_button)
                        time.sleep(2)
                        
                        # Check if anything happened
                        if len(self.driver.window_handles) > 1 or self.driver.current_url != current_url:
                            self.logger.log_info("✅ JavaScript click worked")
                        else:
                            # Method 2: Regular click
                            self.logger.log_info("🖱️ Trying regular click...")
                            view_button.click()
                            time.sleep(2)
                            
                            # Method 3: ActionChains click
                            if len(self.driver.window_handles) == 1 and self.driver.current_url == current_url:
                                self.logger.log_info("🖱️ Trying ActionChains click...")
                                from selenium.webdriver.common.action_chains import ActionChains
                                ActionChains(self.driver).move_to_element(view_button).click().perform()
                                time.sleep(2)
                        
                        time.sleep(1)  # Additional wait
                        
                        # Check if URL changed
                        new_url = self.driver.current_url
                        if new_url != current_url:
                            self.logger.log_success(f"✅ URL changed after click: {new_url}")
                            if "artifacts" in new_url and not new_url.endswith('/artifacts'):
                                return new_url
                        
                        # Check if a new window/tab opened
                        all_windows = self.driver.window_handles
                        if len(all_windows) > 1:
                            self.logger.log_info(f"📋 New window opened: {all_windows}")
                            # Switch to new window and get its URL
                            original_window = self.driver.current_window_handle
                            for window in all_windows:
                                if window != original_window:
                                    self.driver.switch_to.window(window)
                                    new_window_url = self.driver.current_url
                                    self.logger.log_info(f"📋 New window URL: {new_window_url}")
                                    if "artifacts" in new_window_url and not new_window_url.endswith('/artifacts'):
                                        # Switch back to original window
                                        self.driver.switch_to.window(original_window)
                                        return new_window_url
                                    # Switch back to original window
                                    self.driver.switch_to.window(original_window)
                                    break
                        
                        # Check for any network requests or redirects
                        # Look for any new links that might have appeared
                        new_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'artifacts')]")
                        for link in new_links:
                            href = link.get_attribute("href")
                            if href and "artifacts" in href and not href.endswith('/artifacts'):
                                if re.search(r'/shared/artifacts/[^/]+-[a-zA-Z0-9]+', href):
                                    self.logger.log_success(f"✅ Found new artifact link after click: {href}")
                                    return href
                        
                    except Exception as e:
                        self.logger.log_debug(f"Click monitoring failed: {e}")
                
            except Exception as e:
                self.logger.log_debug(f"View button click monitoring failed: {e}")
            
            # Method 5: Browser console debugging - inspect View button and page state
            try:
                self.logger.log_info("🔍 Running browser console debugging...")
                
                # Get View button and inspect it thoroughly
                view_button = self._find_view_button()
                if view_button:
                    # Execute JavaScript to inspect the View button
                    button_inspection = self.driver.execute_script("""
                        var button = arguments[0];
                        var result = {
                            tagName: button.tagName,
                            className: button.className,
                            id: button.id,
                            innerHTML: button.innerHTML,
                            outerHTML: button.outerHTML,
                            attributes: {},
                            parentElement: null,
                            onclick: button.onclick ? button.onclick.toString() : null,
                            href: button.href || null
                        };
                        
                        // Get all attributes
                        for (var i = 0; i < button.attributes.length; i++) {
                            var attr = button.attributes[i];
                            result.attributes[attr.name] = attr.value;
                        }
                        
                        // Get parent element info
                        if (button.parentElement) {
                            result.parentElement = {
                                tagName: button.parentElement.tagName,
                                className: button.parentElement.className,
                                href: button.parentElement.href || null,
                                onclick: button.parentElement.onclick ? button.parentElement.onclick.toString() : null
                            };
                        }
                        
                        return result;
                    """, view_button)
                    
                    self.logger.log_info(f"🔍 View button inspection: {json.dumps(button_inspection, indent=2)}")
                
                # Look for any JavaScript variables or functions that might contain the URL
                js_variables = self.driver.execute_script("""
                    var variables = {};
                    
                    // Check common variable names that might contain artifact URLs
                    var possibleVars = ['artifactUrl', 'artifact_url', 'viewUrl', 'view_url', 'shareUrl', 'share_url', 'reportUrl', 'report_url'];
                    
                    for (var i = 0; i < possibleVars.length; i++) {
                        try {
                            if (window[possibleVars[i]]) {
                                variables[possibleVars[i]] = window[possibleVars[i]];
                            }
                        } catch(e) {}
                    }
                    
                    // Check for any global variables containing 'artifact' or 'view'
                    for (var prop in window) {
                        try {
                            if (typeof window[prop] === 'string' && (prop.toLowerCase().includes('artifact') || prop.toLowerCase().includes('view'))) {
                                if (window[prop].includes('flipsidecrypto.xyz') && window[prop].includes('artifacts')) {
                                    variables[prop] = window[prop];
                                }
                            }
                        } catch(e) {}
                    }
                    
                    return variables;
                """)
                
                if js_variables:
                    self.logger.log_info(f"🔍 JavaScript variables found: {json.dumps(js_variables, indent=2)}")
                    
                    # Check if any of these variables contain the artifact URL
                    for var_name, var_value in js_variables.items():
                        if isinstance(var_value, str) and "artifacts" in var_value and not var_value.endswith('/artifacts'):
                            if re.search(r'/shared/artifacts/[^/]+-[a-zA-Z0-9]+', var_value):
                                self.logger.log_success(f"✅ Found artifact URL in JavaScript variable {var_name}: {var_value}")
                                return var_value
                
            except Exception as e:
                self.logger.log_debug(f"Browser console debugging failed: {e}")
            
            # Method 5: Look in the page source for specific artifact URLs
            try:
                page_source = self.driver.page_source
                # Look for URLs matching the specific pattern: /shared/artifacts/[title]-[hash]
                # This excludes the general artifacts dashboard
                artifact_url_pattern = r'https://flipsidecrypto\.xyz/chat/shared/artifacts/[^"\s]+-[a-zA-Z0-9]+'
                matches = re.findall(artifact_url_pattern, page_source)
                
                # Filter out the general artifacts dashboard
                specific_artifacts = [url for url in matches if not url.endswith('/artifacts')]
                
                if specific_artifacts:
                    artifact_url = specific_artifacts[0]
                    self.logger.log_success(f"✅ Found specific artifact URL in page source: {artifact_url}")
                    return artifact_url
                elif matches:
                    # If we only found the dashboard, log it but don't use it
                    self.logger.log_warning(f"⚠️ Found artifacts dashboard URL but not specific artifact: {matches[0]}")
            except Exception as e:
                self.logger.log_debug(f"Could not find artifact URL in page source: {e}")
            
            self.logger.log_warning("⚠️ Could not extract artifact URL")
            return ""
            
        except Exception as e:
            self.logger.log_error(f"Error extracting artifact URL: {e}")
            return ""
    
    def _find_publish_button(self):
        """Find the Publish button - ONLY searches for buttons with 'Publish' text. NO share icons."""
        try:
            self.logger.log_info("🔍 Looking for Publish button (Publish text only - NO share icons)")
            
            # Method 1: Text-based XPath selectors (most reliable if text doesn't change)
            # ONLY search for buttons that contain "Publish" text - NEVER search for share icons
            publish_selectors = [
                '//span[text()="Publish"]',
                '//span[contains(text(), "Publish")]',
                '//button[.//span[text()="Publish"]]',
                '//button[contains(text(), "Publish")]',
                '//button[normalize-space()="Publish"]',
            ]
            
            for selector in publish_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            text = element.text.strip()
                            if "Publish" in text and "Share" not in text:
                                self.logger.log_success(f"✅ Found Publish button by text: '{text}'")
                                return element
                except Exception as e:
                    self.logger.log_debug(f"Publish selector {selector} failed: {e}")
                    continue
            
            # Method 2: Search all buttons and check their text content
            self.logger.log_info("🔄 Searching all buttons for 'Publish' text")
            all_buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            for i, button in enumerate(all_buttons):
                if not button.is_displayed():
                    continue
                try:
                    button_text = button.text.strip()
                    # ONLY match if it says "Publish" and does NOT say "Share"
                    if "Publish" in button_text and "Share" not in button_text:
                        self.logger.log_success(f"✅ Found Publish button by text content: '{button_text}' - Element {i}")
                        return button
                except Exception as e:
                    self.logger.log_debug(f"Error checking button {i}: {e}")
                    continue
            
            # Method 3: Fallback - Absolute XPath (last resort, fragile but useful if structure is stable)
            # This is the specific XPath provided: /html/body/div[1]/div/main/main/div/div/div[2]/div/div/div[1]/div[2]/button[3]
            try:
                self.logger.log_info("🔄 Trying fallback absolute XPath for Publish button")
                absolute_xpath = '/html/body/div[1]/div/main/main/div/div/div[2]/div/div/div[1]/div[2]/button[3]'
                element = self.driver.find_element(By.XPATH, absolute_xpath)
                if element.is_displayed():
                    # Verify it's actually a publish button (not a share button)
                    button_text = element.text.strip()
                    if "Share" not in button_text:
                        self.logger.log_success(f"✅ Found Publish button via absolute XPath: '{button_text}'")
                        return element
                    else:
                        self.logger.log_debug(f"Absolute XPath found button but it's a share button: '{button_text}'")
            except Exception as e:
                self.logger.log_debug(f"Absolute XPath fallback failed: {e}")
            
            self.logger.log_warning("⚠️ Publish button not found")
            return None
            
        except Exception as e:
            self.logger.log_error(f"Error finding Publish button: {e}")
            return None
    
    def _find_copy_link_button(self):
        """Find the Copy link button that appears after publishing (has lucide-link SVG)."""
        try:
            self.logger.log_info("🔍 Looking for Copy link button (lucide-link icon)")
            
            # Method 1: XPath - Find button with data attributes AND specific SVG path pattern
            # This matches the exact structure: button[data-state="closed"][data-slot="tooltip-trigger"] with SVG containing path d="M10 13..."
            xpath_selectors = [
                # XPath: button with both data attributes and SVG with the specific link path
                '//button[@data-state="closed" and @data-slot="tooltip-trigger" and .//svg[contains(@class, "lucide-link")]]',
                # XPath: button with SVG containing the specific path pattern for link icon
                '//button[.//svg[.//path[@d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"]]]',
                # XPath: button with SVG containing both link path patterns
                '//button[.//svg[.//path[contains(@d, "M10 13")] and .//path[contains(@d, "M14 11")]]]',
                # XPath: button with data attributes (more flexible)
                '//button[@data-slot="tooltip-trigger"][.//svg[contains(@class, "lucide") and contains(@class, "link")]]',
                # XPath: button with SVG class containing lucide-link
                '//button[.//svg[contains(@class, "lucide-link")]]',
            ]
            
            for xpath in xpath_selectors:
                try:
                    buttons = self.driver.find_elements(By.XPATH, xpath)
                    self.logger.log_debug(f"XPath '{xpath}' found {len(buttons)} buttons")
                    
                    for i, button in enumerate(buttons):
                        if not button.is_displayed():
                            continue
                        
                        try:
                            # CRITICAL: Exclude any button with share2 SVG or "Share" text
                            button_text = button.text.strip().lower()
                            share2_svgs = button.find_elements(By.XPATH, './/svg[contains(@class, "lucide-share2")]')
                            if share2_svgs or 'share' in button_text:
                                self.logger.log_debug(f"Skipping button {i} - share button")
                                continue
                            
                            # Verify it has the link SVG structure
                            link_paths = button.find_elements(By.XPATH, './/path[contains(@d, "M10 13") or contains(@d, "M14 11")]')
                            if link_paths:
                                self.logger.log_success(f"✅ Found Copy link button via XPath - Element {i}")
                                return button
                        except Exception as e:
                            self.logger.log_debug(f"Error verifying button {i}: {e}")
                            continue
                            
                except Exception as e:
                    self.logger.log_debug(f"XPath selector '{xpath}' failed: {e}")
                    continue
            
            # Method 2: CSS Selectors - More flexible class matching
            css_selectors = [
                # Combined data attributes
                'button[data-state="closed"][data-slot="tooltip-trigger"]',
                # Individual data attributes
                'button[data-slot="tooltip-trigger"]',
                'button[data-state="closed"]',
            ]
            
            for selector in css_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    self.logger.log_debug(f"CSS selector '{selector}' found {len(buttons)} buttons")
                    
                    for button in buttons:
                        if not button.is_displayed():
                            continue
                        
                        try:
                            # CRITICAL: Exclude share buttons
                            button_text = button.text.strip().lower()
                            share2_svgs = button.find_elements(By.CSS_SELECTOR, 'svg.lucide-share2, svg[class*="lucide-share2"]')
                            if share2_svgs or 'share' in button_text:
                                continue
                            
                            # Check for link SVG - handle multiple classes (lucide lucide-link)
                            svgs = button.find_elements(By.CSS_SELECTOR, 'svg[class*="lucide-link"]')
                            if svgs:
                                self.logger.log_success(f"✅ Found Copy link button via CSS selector: {selector}")
                                return button
                            
                            # Check SVG HTML for link icon characteristics
                            all_svgs = button.find_elements(By.CSS_SELECTOR, 'svg')
                            for svg in all_svgs:
                                svg_html = svg.get_attribute('outerHTML') or ''
                                svg_class = svg.get_attribute('class') or ''
                                
                                # Skip if it has share2 icon
                                if 'lucide-share2' in svg_class or 'lucide-share2' in svg_html:
                                    continue
                                
                                # Check for link icon characteristics
                                if ('lucide-link' in svg_class or 
                                    'lucide-link' in svg_html or
                                    (svg_html.count('<path') >= 2 and 'M10 13' in svg_html)):
                                    self.logger.log_success(f"✅ Found Copy link button via SVG HTML check")
                                    return button
                        except Exception as e:
                            self.logger.log_debug(f"Error checking button: {e}")
                            continue
                            
                except Exception as e:
                    self.logger.log_debug(f"CSS selector '{selector}' failed: {e}")
                    continue
            
            # Method 3: Fallback - Search all buttons and check SVG structure
            self.logger.log_info("🔄 Searching all buttons for link icon structure")
            all_buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            self.logger.log_debug(f"Found {len(all_buttons)} total buttons on page")
            
            for i, button in enumerate(all_buttons):
                if not button.is_displayed():
                    continue
                
                try:
                    # CRITICAL: Exclude any button with share2 SVG or "Share" text
                    button_text = button.text.strip().lower()
                    share2_svgs = button.find_elements(By.XPATH, './/svg[contains(@class, "lucide-share2")]')
                    if share2_svgs or 'share' in button_text:
                        continue
                    
                    # Check for SVG with link path patterns using XPath
                    link_paths = button.find_elements(By.XPATH, './/path[contains(@d, "M10 13") or contains(@d, "M14 11")]')
                    if link_paths:
                        # Verify it has both paths (link icon has 2 specific paths)
                        all_paths = button.find_elements(By.XPATH, './/path')
                        if len(all_paths) >= 2:
                            # Check if paths match link icon pattern
                            path_d_values = [p.get_attribute('d') or '' for p in all_paths]
                            has_m10_13 = any('M10 13' in d for d in path_d_values)
                            has_m14_11 = any('M14 11' in d for d in path_d_values)
                            
                            if has_m10_13 and has_m14_11:
                                self.logger.log_success(f"✅ Found Copy link button via path pattern - Element {i}")
                                return button
                            
                except Exception as e:
                    self.logger.log_debug(f"Error checking button {i}: {e}")
                    continue
            
            self.logger.log_warning("⚠️ Copy link button not found")
            return None
            
        except Exception as e:
            self.logger.log_error(f"Error finding Copy link button: {e}")
            return None
    
    def _extract_artifact_url_from_clipboard(self) -> str:
        """Extract the artifact URL from the clipboard after clicking the publish button."""
        try:
            self.logger.log_info("📋 Reading artifact URL from clipboard")
            
            if not pyperclip:
                self.logger.log_warning("⚠️ pyperclip not available, cannot read from clipboard")
                return ""
            
            # Read from clipboard
            clipboard_content = pyperclip.paste()
            
            if not clipboard_content:
                self.logger.log_warning("⚠️ Clipboard is empty")
                return ""
            
            # Check if clipboard contains a URL
            if 'flipsidecrypto.xyz' in clipboard_content or 'http' in clipboard_content:
                # Extract URL if it's part of a larger string
                url_pattern = r'https?://[^\s]+flipsidecrypto\.xyz[^\s]*'
                url_matches = re.findall(url_pattern, clipboard_content)
                
                if url_matches:
                    artifact_url = url_matches[0]
                    # Clean up the URL (remove trailing characters if needed)
                    artifact_url = artifact_url.rstrip('.,;:!?')
                    self.logger.log_success(f"✅ Found artifact URL in clipboard: {artifact_url}")
                    return artifact_url
                elif 'flipsidecrypto.xyz' in clipboard_content:
                    # Try to extract just the URL part
                    self.logger.log_info(f"📋 Clipboard content: {clipboard_content[:100]}...")
                    # Use the entire clipboard content if it looks like a URL
                    if clipboard_content.strip().startswith('http'):
                        self.logger.log_success(f"✅ Using clipboard content as URL: {clipboard_content.strip()}")
                        return clipboard_content.strip()
            else:
                self.logger.log_warning(f"⚠️ Clipboard does not contain a URL: {clipboard_content[:50]}...")
            
            return ""
            
        except Exception as e:
            # Silently handle clipboard errors in headless environments (expected to fail)
            # This is not an error since we have fallback methods
            self.logger.log_debug(f"Clipboard not available (expected in headless): {e}")
            return ""
    
    def _find_view_button(self):
        """Find the View button."""
        try:
            # Use the specific selector from the provided element
            view_selectors = [
                'button[data-slot="tooltip-trigger"]:has(span:contains("View"))',
                'button[data-slot="tooltip-trigger"]',
                '//button[@data-slot="tooltip-trigger"]//span[text()="View"]',
                '//button[@data-slot="tooltip-trigger"]//span[contains(text(), "View")]',
                '//span[text()="View"]',
                '//span[contains(text(), "View")]',
                '//button[.//span[text()="View"]]',
                '//button[contains(text(), "View")]'
            ]
            
            for selector in view_selectors:
                try:
                    if selector.startswith('//'):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    self.logger.log_debug(f"Found {len(elements)} elements for View selector: {selector}")
                    
                    for i, element in enumerate(elements):
                        if element.is_displayed():
                            # Get element details for debugging
                            element_text = element.text.strip()
                            element_tag = element.tag_name
                            location = element.location
                            size = self.driver.get_window_size()
                            
                            self.logger.log_debug(f"View element {i}: tag={element_tag}, text='{element_text}', x={location['x']}, width={size['width']}")
                            
                            # Check if it contains "View" text and is in the right area
                            if "View" in element_text and location['x'] > size['width'] * 0.3:
                                self.logger.log_success(f"✅ Found View button: {selector} - '{element_text}' at x={location['x']}")
                                return element
                except Exception as e:
                    self.logger.log_debug(f"View selector {selector} failed: {e}")
                    continue
            
            # Fallback: Look for any button with "View" text
            self.logger.log_info("🔍 Trying fallback View button search")
            try:
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                for i, button in enumerate(all_buttons):
                    if button.is_displayed():
                        button_text = button.text.strip()
                        if "View" in button_text:
                            location = button.location
                            size = self.driver.get_window_size()
                            self.logger.log_debug(f"Fallback View button {i}: '{button_text}' at x={location['x']}")
                            if location['x'] > size['width'] * 0.3:
                                self.logger.log_success(f"✅ Found View button via fallback: '{button_text}' at x={location['x']}")
                                return button
            except Exception as e:
                self.logger.log_debug(f"Fallback View search failed: {e}")
            
            self.logger.log_warning("⚠️ View button not found")
            return None
            
        except Exception as e:
            self.logger.log_error(f"View button search failed: {e}")
            return None
    
    def _scroll_through_page(self):
        """Scroll through the entire page to ensure all content is loaded."""
        try:
            self.logger.log_info("📜 Starting page scroll to load all content...")
            
            # Get initial page height
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_pause_time = 1
            max_scrolls = 10  # Prevent infinite scrolling
            scroll_count = 0
            
            while scroll_count < max_scrolls:
                # Scroll down to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Wait for new content to load
                time.sleep(scroll_pause_time)
                
                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    # No new content loaded, we've reached the bottom
                    self.logger.log_info("📜 Reached bottom of page, all content loaded")
                    break
                
                last_height = new_height
                scroll_count += 1
                self.logger.log_debug(f"📜 Scrolled {scroll_count} times, page height: {new_height}")
            
            # Scroll back to top to capture from beginning
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Also scroll horizontally if needed (for wide charts)
            self.logger.log_info("📜 Checking for horizontal scrolling needs...")
            page_width = self.driver.execute_script("return document.body.scrollWidth")
            window_width = self.driver.get_window_size()["width"]
            
            if page_width > window_width:
                self.logger.log_info(f"📜 Page is wider ({page_width}px) than window ({window_width}px), scrolling horizontally")
                self.driver.execute_script("window.scrollTo(document.body.scrollWidth/2, 0);")
                time.sleep(1)
                self.driver.execute_script("window.scrollTo(0, 0);")
                time.sleep(1)
            
            self.logger.log_success("✅ Page scrolling completed")
            
        except Exception as e:
            self.logger.log_error(f"Error during page scrolling: {e}")

    def _capture_final_screenshot(self) -> str:
        """Capture final screenshot of the chat."""
        try:
            screenshot_path = f"screenshots/final_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(screenshot_path)
            self.logger.log_info(f"📸 Final screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            self.logger.log_error(f"Failed to capture final screenshot: {e}")
            return ""
    
    def _cleanup(self):
        """Clean up resources.
        
        Only cleans up if we created the driver/authenticator ourselves.
        If the driver/authenticator was passed in from outside (e.g., FlipsideChatManager),
        we don't clean it up as the caller is responsible for it.
        """
        try:
            # Only cleanup if we created the authenticator ourselves
            if self._authenticator_owned_by_extractor and self.authenticator:
                self.authenticator.cleanup()
                self.logger.log_info("🧹 Cleanup completed")
            else:
                self.logger.log_info("ℹ️ Skipping cleanup - driver/authenticator was provided externally")
        except Exception as e:
            self.logger.log_error(f"Cleanup error: {e}")
