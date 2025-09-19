#!/usr/bin/env python3
"""
Enhanced logging system for Flipside Chat Automation.
Provides step-by-step progress tracking and readable summaries.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum


class AutomationStep(Enum):
    """Enumeration of automation steps for tracking progress."""
    INITIALIZATION = "🚀 Initialization"
    WEBDRIVER_SETUP = "🌐 WebDriver Setup"
    SESSION_LOADING = "🍪 Session Loading"
    NAVIGATION = "🧭 Navigation"
    AUTHENTICATION = "🔐 Authentication"
    CHAT_ACCESS = "💬 Chat Access"
    PROMPT_SUBMISSION = "📝 Prompt Submission"
    RESPONSE_WAITING = "⏳ Response Waiting"
    RESULT_CAPTURE = "📸 Result Capture"
    CLEANUP = "🧹 Cleanup"


class AutomationLogger:
    """Enhanced logger for automation with step tracking and progress indicators."""
    
    def __init__(self, name: str = "flipside_automation"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create console handler with custom formatting
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Step tracking
        self.current_step: Optional[AutomationStep] = None
        self.step_start_time: Optional[float] = None
        self.step_history: List[Dict[str, Any]] = []
        self.start_time = time.time()
        
        # Progress tracking
        self.total_steps = len(AutomationStep)
        self.current_step_number = 0
        
        self.logger.info("🤖 Flipside Chat Automation Logger Initialized")
    
    def start_step(self, step: AutomationStep, details: str = ""):
        """Start tracking a new automation step."""
        # End previous step if exists
        if self.current_step:
            self.end_step()
        
        self.current_step = step
        self.step_start_time = time.time()
        self.current_step_number += 1
        
        progress = f"[{self.current_step_number}/{self.total_steps}]"
        message = f"{progress} {step.value}"
        if details:
            message += f" - {details}"
        
        self.logger.info(f"▶️  {message}")
        
        # Add to history
        self.step_history.append({
            "step": step,
            "start_time": self.step_start_time,
            "details": details,
            "status": "in_progress"
        })
    
    def end_step(self, success: bool = True, details: str = ""):
        """End the current step and log results."""
        if not self.current_step or not self.step_start_time:
            return
        
        duration = time.time() - self.step_start_time
        status_emoji = "✅" if success else "❌"
        status_text = "COMPLETED" if success else "FAILED"
        
        message = f"{status_emoji} {self.current_step.value} - {status_text}"
        if details:
            message += f" ({details})"
        message += f" [{duration:.1f}s]"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
        
        # Update history
        if self.step_history:
            self.step_history[-1].update({
                "end_time": time.time(),
                "duration": duration,
                "success": success,
                "status": status_text.lower(),
                "end_details": details
            })
        
        self.current_step = None
        self.step_start_time = None
    
    def log_info(self, message: str, emoji: str = "ℹ️"):
        """Log an info message with optional emoji."""
        self.logger.info(f"{emoji} {message}")
    
    def log_success(self, message: str):
        """Log a success message."""
        self.logger.info(f"✅ {message}")
    
    def log_warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(f"⚠️  {message}")
    
    def log_error(self, message: str):
        """Log an error message."""
        self.logger.error(f"❌ {message}")
    
    def log_debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(f"🔍 {message}")
    
    def log_element_found(self, element_type: str, selector: str, count: int = 1):
        """Log when an element is found."""
        if count == 1:
            self.log_info(f"Found {element_type}: {selector}")
        else:
            self.log_info(f"Found {count} {element_type}s: {selector}")
    
    def log_element_not_found(self, element_type: str, selector: str):
        """Log when an element is not found."""
        self.log_warning(f"Element not found: {element_type} ({selector})")
    
    def log_retry_attempt(self, attempt: int, max_attempts: int, reason: str = ""):
        """Log a retry attempt."""
        message = f"Retry attempt {attempt}/{max_attempts}"
        if reason:
            message += f" - {reason}"
        self.log_warning(message)
    
    def log_waiting(self, duration: float, reason: str = ""):
        """Log waiting periods."""
        message = f"Waiting {duration}s"
        if reason:
            message += f" for {reason}"
        self.log_info(message, "⏳")
    
    def log_selenium_action(self, action: str, target: str = "", success: bool = True):
        """Log Selenium actions in a readable format."""
        status = "✅" if success else "❌"
        message = f"{status} {action}"
        if target:
            message += f" on {target}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def log_network_request(self, method: str, url: str, status_code: int = None):
        """Log network requests in a readable format."""
        status_emoji = "✅" if status_code and 200 <= status_code < 300 else "⚠️"
        message = f"{status_emoji} {method} {url}"
        if status_code:
            message += f" [{status_code}]"
        self.logger.info(message)
    
    def log_cookie_operation(self, operation: str, count: int = 0):
        """Log cookie operations."""
        if operation == "loaded":
            self.log_success(f"Loaded {count} cookies from session")
        elif operation == "applied":
            self.log_success(f"Applied {count} cookies to browser")
        elif operation == "failed":
            self.log_error("Failed to load cookies")
        else:
            self.log_info(f"Cookie operation: {operation}")
    
    def log_screenshot(self, filename: str, description: str = ""):
        """Log screenshot capture."""
        message = f"Screenshot saved: {filename}"
        if description:
            message += f" ({description})"
        self.log_success(message)
    
    def log_analysis_result(self, response_length: int, artifacts_count: int, screenshots_count: int):
        """Log analysis results summary."""
        self.log_success(f"Analysis completed: {response_length} chars, {artifacts_count} artifacts, {screenshots_count} screenshots")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the automation run."""
        total_duration = time.time() - self.start_time
        successful_steps = sum(1 for step in self.step_history if step.get("success", False))
        failed_steps = len(self.step_history) - successful_steps
        
        return {
            "total_duration": total_duration,
            "total_steps": len(self.step_history),
            "successful_steps": successful_steps,
            "failed_steps": failed_steps,
            "success_rate": (successful_steps / len(self.step_history) * 100) if self.step_history else 0,
            "step_history": self.step_history
        }
    
    def print_summary(self):
        """Print a formatted summary of the automation run."""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("📊 AUTOMATION SUMMARY")
        print("="*60)
        print(f"⏱️  Total Duration: {summary['total_duration']:.1f}s")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print(f"✅ Successful Steps: {summary['successful_steps']}")
        print(f"❌ Failed Steps: {summary['failed_steps']}")
        
        print("\n📋 Step Details:")
        print("-" * 40)
        for i, step in enumerate(summary['step_history'], 1):
            status_emoji = "✅" if step.get("success", False) else "❌"
            duration = step.get("duration", 0)
            step_name = step['step'].value
            print(f"{i:2d}. {status_emoji} {step_name} [{duration:.1f}s]")
            if step.get("end_details"):
                print(f"    └─ {step['end_details']}")
        
        print("="*60)
    
    def log_progress_bar(self, current: int, total: int, description: str = ""):
        """Log a simple progress bar."""
        percentage = (current / total) * 100
        bar_length = 20
        filled_length = int(bar_length * current // total)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        message = f"Progress: [{bar}] {percentage:.1f}% ({current}/{total})"
        if description:
            message += f" - {description}"
        
        self.logger.info(message)


# Global logger instance
automation_logger = AutomationLogger()


def get_automation_logger() -> AutomationLogger:
    """Get the global automation logger instance."""
    return automation_logger


def setup_automation_logging(debug_mode: bool = False):
    """Setup automation logging with appropriate level."""
    if debug_mode:
        automation_logger.logger.setLevel(logging.DEBUG)
        automation_logger.log_info("Debug mode enabled - verbose logging active")
    else:
        automation_logger.logger.setLevel(logging.INFO)
        automation_logger.log_info("Standard logging mode - essential steps only")
    
    return automation_logger
