"""
Stealth Authentication

Handles stealth authentication for Flipside using undetected-chromedriver.
"""

import os
import time
from typing import Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from modules.shared.logger import AutomationLogger


class StealthAuthenticator:
    """Handles stealth authentication for Flipside."""
    
    def __init__(self):
        self.driver = None
        self.logger = AutomationLogger()
    
    def setup_driver(self):
        """Setup stealth Chrome driver."""
        try:
            self.logger.log_info("🤖 Setting up stealth Chrome driver")
            
            import undetected_chromedriver as uc
            
            options = uc.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            
            self.driver = uc.Chrome(options=options)
            
            # Apply stealth scripts
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            self.logger.log_success("✅ Stealth Chrome driver setup complete")
            return self.driver
            
        except Exception as e:
            self.logger.log_error(f"Stealth driver setup failed: {e}")
            return None
    
    def login(self) -> bool:
        """Perform stealth login."""
        try:
            self.logger.log_info("🔐 Starting stealth login process")
            
            # Navigate to login page
            self.driver.get("https://flipsidecrypto.xyz/login")
            
            # Wait for login form
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            
            # Get credentials from environment
            email = os.getenv("FLIPSIDE_EMAIL")
            password = os.getenv("FLIPSIDE_PASSWORD")
            
            if not email or not password:
                self.logger.log_error("❌ Missing credentials in environment variables")
                return False
            
            # Enter email
            self.logger.log_info("📧 Entering email")
            email_field = self.driver.find_element(By.NAME, "email")
            email_field.clear()
            email_field.send_keys(email)
            
            time.sleep(2)
            
            # Enter password
            self.logger.log_info("🔑 Entering password")
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            time.sleep(2)
            
            # Click login button
            self.logger.log_info("🖱️ Clicking login button")
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for redirect
            self.logger.log_info("⏳ Waiting for login to complete")
            WebDriverWait(self.driver, 30).until(
                lambda driver: "chat" in driver.current_url
            )
            
            self.logger.log_success(f"✅ Redirected to: {self.driver.current_url}")
            self.logger.log_success("✅ Login successful")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Login failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up the driver."""
        try:
            if self.driver:
                self.driver.quit()
                self.logger.log_info("🧹 Stealth driver cleanup complete")
        except Exception as e:
            self.logger.log_error(f"Cleanup error: {e}")
