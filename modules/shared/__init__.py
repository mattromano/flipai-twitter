"""
Shared Modules

Common utilities and components used across different modules.
"""

from modules.shared.logger import AutomationLogger
from modules.shared.authentication import StealthAuthenticator
from modules.shared.prompt_selector import PromptSelector

__all__ = ['AutomationLogger', 'StealthAuthenticator', 'PromptSelector']
