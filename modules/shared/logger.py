"""
Automation Logger

Centralized logging for the automation system.
"""

import logging
import os
from datetime import datetime
from typing import Optional


class AutomationLogger:
    """Centralized logging for automation workflows."""
    
    def __init__(self, name: str = "flipside_automation"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        # Setup file handler
        log_file = f"logs/automation_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Setup formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def log_success(self, message: str):
        """Log success message."""
        self.logger.info(f"✅ {message}")
    
    def log_warning(self, message: str):
        """Log warning message."""
        self.logger.warning(f"⚠️ {message}")
    
    def log_error(self, message: str):
        """Log error message."""
        self.logger.error(f"❌ {message}")
    
    def log_debug(self, message: str):
        """Log debug message."""
        self.logger.debug(f"🐛 {message}")
