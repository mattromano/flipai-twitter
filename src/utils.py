"""
Utilities for Flipside Chat Automation

Helper functions for waiting, element detection, screenshots, and text extraction.
"""

import os
import time
import logging
import random
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from PIL import Image

logger = logging.getLogger(__name__)


class WaitUtils:
    """Utility class for various wait strategies."""
    
    @staticmethod
    def wait_for_element(
        driver: WebDriver, 
        by: By, 
        value: str, 
        timeout: int = 10,
        description: str = "element"
    ) -> Optional[Any]:
        """
        Wait for an element to be present and return it.
        
        Args:
            driver: WebDriver instance
            by: Selenium By strategy
            value: Element selector
            timeout: Maximum time to wait in seconds
            description: Description for logging
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            logger.debug(f"Found {description}: {value}")
            return element
        except TimeoutException:
            logger.warning(f"Timeout waiting for {description}: {value}")
            return None
    
    @staticmethod
    def wait_for_clickable(
        driver: WebDriver, 
        by: By, 
        value: str, 
        timeout: int = 10,
        description: str = "clickable element"
    ) -> Optional[Any]:
        """
        Wait for an element to be clickable and return it.
        
        Args:
            driver: WebDriver instance
            by: Selenium By strategy
            value: Element selector
            timeout: Maximum time to wait in seconds
            description: Description for logging
            
        Returns:
            WebElement if found and clickable, None otherwise
        """
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            logger.debug(f"Found clickable {description}: {value}")
            return element
        except TimeoutException:
            logger.warning(f"Timeout waiting for clickable {description}: {value}")
            return None
    
    @staticmethod
    def wait_for_text_in_element(
        driver: WebDriver,
        by: By,
        value: str,
        text: str,
        timeout: int = 10,
        description: str = "element with text"
    ) -> bool:
        """
        Wait for specific text to appear in an element.
        
        Args:
            driver: WebDriver instance
            by: Selenium By strategy
            value: Element selector
            text: Text to wait for
            timeout: Maximum time to wait in seconds
            description: Description for logging
            
        Returns:
            True if text found, False otherwise
        """
        try:
            WebDriverWait(driver, timeout).until(
                EC.text_to_be_present_in_element((by, value), text)
            )
            logger.debug(f"Found text '{text}' in {description}")
            return True
        except TimeoutException:
            logger.warning(f"Timeout waiting for text '{text}' in {description}")
            return False
    
    @staticmethod
    def wait_for_loading_to_complete(
        driver: WebDriver,
        timeout: int = 60,
        loading_selectors: List[str] = None
    ) -> bool:
        """
        Wait for loading indicators to disappear.
        
        Args:
            driver: WebDriver instance
            timeout: Maximum time to wait in seconds
            loading_selectors: List of CSS selectors for loading indicators
            
        Returns:
            True if loading completed, False if timeout
        """
        if loading_selectors is None:
            loading_selectors = [
                ".loading",
                ".spinner", 
                "[data-testid='loading']",
                ".animate-spin",
                ".loading-spinner"
            ]
        
        try:
            # Wait for any loading indicators to disappear
            for selector in loading_selectors:
                try:
                    WebDriverWait(driver, 5).until_not(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                except TimeoutException:
                    # This selector might not exist, continue checking others
                    continue
            
            # Additional wait to ensure content is fully loaded
            time.sleep(2)
            logger.info("Loading completed successfully")
            return True
            
        except Exception as e:
            logger.warning(f"Loading completion check failed: {e}")
            return False


class ElementUtils:
    """Utility class for element detection and interaction."""
    
    @staticmethod
    def find_element_safe(
        driver: WebDriver,
        by: By,
        value: str,
        description: str = "element"
    ) -> Optional[Any]:
        """
        Safely find an element without throwing exceptions.
        
        Args:
            driver: WebDriver instance
            by: Selenium By strategy
            value: Element selector
            description: Description for logging
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            element = driver.find_element(by, value)
            logger.debug(f"Found {description}: {value}")
            return element
        except NoSuchElementException:
            logger.debug(f"Element not found: {description} - {value}")
            return None
        except Exception as e:
            logger.warning(f"Error finding {description}: {e}")
            return None
    
    @staticmethod
    def find_elements_safe(
        driver: WebDriver,
        by: By,
        value: str,
        description: str = "elements"
    ) -> List[Any]:
        """
        Safely find multiple elements without throwing exceptions.
        
        Args:
            driver: WebDriver instance
            by: Selenium By strategy
            value: Element selector
            description: Description for logging
            
        Returns:
            List of WebElements found
        """
        try:
            elements = driver.find_elements(by, value)
            logger.debug(f"Found {len(elements)} {description}: {value}")
            return elements
        except Exception as e:
            logger.warning(f"Error finding {description}: {e}")
            return []
    
    @staticmethod
    def get_element_text_safe(element: Any, default: str = "") -> str:
        """
        Safely get text from an element.
        
        Args:
            element: WebElement
            default: Default text if element is None or text is empty
            
        Returns:
            Element text or default
        """
        if element is None:
            return default
        
        try:
            text = element.text.strip()
            return text if text else default
        except Exception as e:
            logger.warning(f"Error getting element text: {e}")
            return default
    
    @staticmethod
    def click_element_safe(element: Any, description: str = "element") -> bool:
        """
        Safely click an element.
        
        Args:
            element: WebElement to click
            description: Description for logging
            
        Returns:
            True if click successful, False otherwise
        """
        if element is None:
            logger.warning(f"Cannot click {description}: element is None")
            return False
        
        try:
            element.click()
            logger.debug(f"Successfully clicked {description}")
            return True
        except Exception as e:
            logger.warning(f"Failed to click {description}: {e}")
            return False


class ScreenshotUtils:
    """Utility class for screenshot capture and management."""
    
    @staticmethod
    def ensure_screenshots_dir() -> str:
        """
        Ensure screenshots directory exists.
        
        Returns:
            Path to screenshots directory
        """
        screenshots_dir = "screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)
        return screenshots_dir
    
    @staticmethod
    def capture_screenshot(
        driver: WebDriver,
        filename: str = None,
        description: str = "screenshot"
    ) -> Optional[str]:
        """
        Capture a screenshot and save it.
        
        Args:
            driver: WebDriver instance
            filename: Custom filename (optional)
            description: Description for logging
            
        Returns:
            Path to saved screenshot or None if failed
        """
        try:
            screenshots_dir = ScreenshotUtils.ensure_screenshots_dir()
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{description}_{timestamp}.png"
            
            filepath = os.path.join(screenshots_dir, filename)
            
            # Take screenshot
            driver.save_screenshot(filepath)
            logger.info(f"Captured {description}: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to capture {description}: {e}")
            return None
    
    @staticmethod
    def capture_element_screenshot(
        driver: WebDriver,
        element: Any,
        filename: str = None,
        description: str = "element screenshot"
    ) -> Optional[str]:
        """
        Capture screenshot of a specific element.
        
        Args:
            driver: WebDriver instance
            element: WebElement to capture
            filename: Custom filename (optional)
            description: Description for logging
            
        Returns:
            Path to saved screenshot or None if failed
        """
        try:
            screenshots_dir = ScreenshotUtils.ensure_screenshots_dir()
            
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{description}_{timestamp}.png"
            
            filepath = os.path.join(screenshots_dir, filename)
            
            # Capture element screenshot
            element.screenshot(filepath)
            logger.info(f"Captured {description}: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to capture {description}: {e}")
            return None
    
    @staticmethod
    def find_chart_elements(driver: WebDriver) -> List[Any]:
        """
        Find chart/visualization elements on the page.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            List of chart elements found
        """
        chart_selectors = [
            "canvas",
            "svg",
            ".highcharts-container",
            "[data-testid='chart']",
            ".chart-container",
            ".visualization",
            ".plotly",
            ".d3-chart"
        ]
        
        chart_elements = []
        for selector in chart_selectors:
            elements = ElementUtils.find_elements_safe(driver, By.CSS_SELECTOR, selector, f"chart ({selector})")
            chart_elements.extend(elements)
        
        logger.info(f"Found {len(chart_elements)} chart elements")
        return chart_elements


class TextUtils:
    """Utility class for text extraction and cleaning."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = " ".join(text.split())
        
        # Remove common unwanted characters
        cleaned = cleaned.replace("\u00a0", " ")  # Non-breaking space
        cleaned = cleaned.replace("\u2019", "'")  # Right single quotation mark
        cleaned = cleaned.replace("\u201c", '"')  # Left double quotation mark
        cleaned = cleaned.replace("\u201d", '"')  # Right double quotation mark
        
        return cleaned.strip()
    
    @staticmethod
    def extract_chat_response(driver: WebDriver) -> str:
        """
        Extract chat response text from the page.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            Extracted response text
        """
        response_selectors = [
            ".message-content",
            ".chat-response",
            "[data-testid='response']",
            ".response-text",
            ".analysis-result",
            ".chat-message:last-child",
            ".message",
            ".response",
            "[class*='message']",
            "[class*='response']"
        ]
        
        for selector in response_selectors:
            element = ElementUtils.find_element_safe(driver, By.CSS_SELECTOR, selector, f"response ({selector})")
            if element:
                text = ElementUtils.get_element_text_safe(element)
                if text:
                    cleaned_text = TextUtils.clean_text(text)
                    logger.info(f"Extracted response text ({len(cleaned_text)} characters)")
                    return cleaned_text
        
        logger.warning("No response text found")
        return ""
    
    @staticmethod
    def extract_chat_url(driver: WebDriver) -> str:
        """
        Extract the current chat URL.
        
        Args:
            driver: WebDriver instance
            
        Returns:
            Current URL
        """
        try:
            url = driver.current_url
            logger.info(f"Extracted chat URL: {url}")
            return url
        except Exception as e:
            logger.error(f"Failed to extract chat URL: {e}")
            return ""


class PromptUtils:
    """Utility class for prompt rotation and management."""
    
    @staticmethod
    def get_random_prompt(prompts: List[str]) -> str:
        """
        Get a random prompt from the list.
        
        Args:
            prompts: List of available prompts
            
        Returns:
            Randomly selected prompt
        """
        if not prompts:
            return ""
        
        prompt = random.choice(prompts)
        logger.info(f"Selected random prompt: {prompt[:50]}...")
        return prompt
    
    @staticmethod
    def get_daily_prompt(prompts: List[str]) -> str:
        """
        Get a prompt based on the current day (deterministic rotation).
        
        Args:
            prompts: List of available prompts
            
        Returns:
            Daily prompt
        """
        if not prompts:
            return ""
        
        # Use day of year to get consistent daily rotation
        day_of_year = datetime.now().timetuple().tm_yday
        prompt_index = day_of_year % len(prompts)
        prompt = prompts[prompt_index]
        
        logger.info(f"Selected daily prompt (day {day_of_year}): {prompt[:50]}...")
        return prompt


class RetryUtils:
    """Utility class for retry logic."""
    
    @staticmethod
    def retry_on_exception(
        func,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: Tuple = (Exception,)
    ):
        """
        Retry a function on specific exceptions.
        
        Args:
            func: Function to retry
            max_retries: Maximum number of retries
            delay: Initial delay between retries
            backoff_factor: Multiplier for delay on each retry
            exceptions: Tuple of exceptions to catch and retry on
            
        Returns:
            Function result or raises last exception
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return func()
            except exceptions as e:
                last_exception = e
                if attempt < max_retries:
                    wait_time = delay * (backoff_factor ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries + 1} attempts failed. Last error: {e}")
        
        raise last_exception
