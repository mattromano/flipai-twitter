"""
Data Extractor

Handles extraction of text data from chat responses.
"""

import re
from typing import Dict, Any, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from modules.shared.logger import AutomationLogger


class DataExtractor:
    """Extracts text data from chat responses."""
    
    def __init__(self):
        self.logger = AutomationLogger()
    
    def extract_text_data(self, driver: WebDriver) -> Dict[str, str]:
        """Extract text data from the chat page."""
        try:
            # Extract main response text
            response_text = self._extract_response_text(driver)
            
            # Extract Twitter-specific text
            twitter_text = self._extract_twitter_text(response_text)
            
            return {
                "response_text": response_text,
                "twitter_text": twitter_text
            }
            
        except Exception as e:
            self.logger.log_error(f"Text extraction failed: {e}")
            return {"response_text": "", "twitter_text": ""}
    
    def _extract_response_text(self, driver: WebDriver) -> str:
        """Extract the main response text from the chat."""
        try:
            # Try to find the main chat content area
            chat_selectors = [
                '[data-testid="chat-messages"]',
                '.chat-messages',
                '.conversation',
                '.messages',
                'main',
                '[role="main"]'
            ]
            
            chat_text = ""
            for selector in chat_selectors:
                try:
                    chat_element = driver.find_element(By.CSS_SELECTOR, selector)
                    if chat_element and chat_element.is_displayed():
                        chat_text = chat_element.text
                        if len(chat_text) > 100:  # Make sure we got substantial content
                            break
                except NoSuchElementException:
                    continue
            
            # Fallback to body text if no specific chat area found
            if not chat_text or len(chat_text) < 100:
                body_text = driver.find_element(By.TAG_NAME, "body").text
                chat_text = self._filter_sidebar_content(body_text)
            
            self.logger.log_info(f"Extracted response text: {len(chat_text)} characters")
            return chat_text
            
        except Exception as e:
            self.logger.log_error(f"Response text extraction failed: {e}")
            return ""
    
    def _extract_twitter_text(self, response_text: str) -> str:
        """Extract Twitter-specific text from the response."""
        try:
            if not response_text:
                return ""
            
            # Look for TWITTER_TEXT marker
            if "TWITTER_TEXT:" in response_text:
                lines = response_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if "TWITTER_TEXT:" in line:
                        # Extract content after "TWITTER_TEXT:"
                        twitter_content = line.split("TWITTER_TEXT:", 1)[1].strip()
                        # Remove any HTML_CHART markers
                        twitter_content = twitter_content.replace("HTML_CHART:", "").strip()
                        if twitter_content:
                            self.logger.log_info(f"Extracted Twitter text: {len(twitter_content)} characters")
                            return twitter_content
            
            # Fallback: extract a summary from the response
            return self._create_twitter_summary(response_text)
            
        except Exception as e:
            self.logger.log_error(f"Twitter text extraction failed: {e}")
            return ""
    
    def _filter_sidebar_content(self, body_text: str) -> str:
        """Filter out sidebar content from body text."""
        try:
            lines = body_text.split('\n')
            filtered_lines = []
            skip_sidebar = True
            
            for line in lines:
                line = line.strip()
                # Skip sidebar content
                if any(sidebar_word in line.lower() for sidebar_word in [
                    'toggle sidebar', 'start a chat', 'artifacts', 'rules', 
                    'recent chats', 'flipsideai', 'beta'
                ]):
                    skip_sidebar = True
                    continue
                
                # Start capturing when we see actual content
                if len(line) > 20 and not skip_sidebar:
                    filtered_lines.append(line)
                
                # Look for analysis indicators
                if any(indicator in line.lower() for indicator in [
                    'analysis', 'data shows', 'according to', 'the results', 'key findings'
                ]):
                    skip_sidebar = False
                    filtered_lines.append(line)
            
            return '\n'.join(filtered_lines)
            
        except Exception as e:
            self.logger.log_error(f"Sidebar filtering failed: {e}")
            return body_text
    
    def _create_twitter_summary(self, response_text: str) -> str:
        """Create a Twitter summary from the response text."""
        try:
            # Find the first substantial paragraph
            paragraphs = response_text.split('\n\n')
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if len(paragraph) > 50 and len(paragraph) < 200:
                    # Clean up the paragraph
                    paragraph = re.sub(r'\s+', ' ', paragraph)
                    paragraph = paragraph.replace('\n', ' ')
                    return paragraph
            
            # Fallback: take first 200 characters
            summary = response_text[:200].strip()
            summary = re.sub(r'\s+', ' ', summary)
            return summary
            
        except Exception as e:
            self.logger.log_error(f"Twitter summary creation failed: {e}")
            return ""
