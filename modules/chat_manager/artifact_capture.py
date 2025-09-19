"""
Artifact Capture

Handles detection and capture of charts, visualizations, and other artifacts.
"""

from typing import List, Dict, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from modules.shared.logger import AutomationLogger


class ArtifactCapture:
    """Captures charts and visualizations from the chat."""
    
    def __init__(self):
        self.logger = AutomationLogger()
    
    def capture_artifacts(self, driver: WebDriver) -> List[Dict[str, Any]]:
        """Capture all artifacts from the current page."""
        try:
            self.logger.log_info("🔍 Searching for artifacts")
            
            artifacts = []
            
            # Look for various chart/visualization elements
            artifact_selectors = [
                "canvas",
                "svg", 
                "[data-testid*='chart']",
                "[class*='chart']",
                "[class*='visualization']",
                "[class*='graph']",
                ".recharts-wrapper",
                ".plotly",
                ".highcharts-container",
                "iframe[src*='chart']",
                "iframe[src*='visualization']",
                "[class*='plotly']",
                "[class*='d3']",
                "[class*='echarts']"
            ]
            
            for selector in artifact_selectors:
                try:
                    if selector.startswith('[') or selector.startswith('.'):
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    else:
                        elements = driver.find_elements(By.TAG_NAME, selector)
                    
                    for element in elements:
                        try:
                            if self._is_valid_artifact(element):
                                artifact_info = {
                                    "type": "visualization",
                                    "tag": element.tag_name,
                                    "selector": selector,
                                    "size": element.size,
                                    "location": element.location,
                                    "is_displayed": element.is_displayed()
                                }
                                artifacts.append(artifact_info)
                                self.logger.log_info(f"Found artifact: {element.tag_name} ({selector})")
                        except Exception as e:
                            self.logger.log_debug(f"Error processing element: {e}")
                            continue
                            
                except Exception as e:
                    self.logger.log_debug(f"Error with selector {selector}: {e}")
                    continue
            
            self.logger.log_info(f"Found {len(artifacts)} artifacts")
            return artifacts
            
        except Exception as e:
            self.logger.log_error(f"Artifact capture failed: {e}")
            return []
    
    def _is_valid_artifact(self, element) -> bool:
        """Check if an element is a valid artifact."""
        try:
            # Must be displayed
            if not element.is_displayed():
                return False
            
            # Must have reasonable size
            size = element.size
            if size['width'] < 50 or size['height'] < 50:
                return False
            
            # Check for chart-like content
            if element.tag_name.lower() in ['canvas', 'svg']:
                return True
            
            # Check for chart-related classes or attributes
            class_name = element.get_attribute('class') or ''
            if any(chart_word in class_name.lower() for chart_word in [
                'chart', 'graph', 'plot', 'visualization', 'recharts', 'plotly', 'highcharts'
            ]):
                return True
            
            # Check for chart-related data attributes
            data_testid = element.get_attribute('data-testid') or ''
            if 'chart' in data_testid.lower():
                return True
            
            return False
            
        except Exception:
            return False
    
    def capture_artifact_screenshot(self, driver: WebDriver, artifact: Dict[str, Any]) -> str:
        """Capture a screenshot of a specific artifact."""
        try:
            # This would implement artifact-specific screenshot capture
            # For now, return empty string as placeholder
            self.logger.log_info(f"Capturing screenshot for artifact: {artifact['tag']}")
            return ""
        except Exception as e:
            self.logger.log_error(f"Artifact screenshot capture failed: {e}")
            return ""
