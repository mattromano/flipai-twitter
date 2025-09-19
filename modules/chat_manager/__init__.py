"""
Chat Manager Module

Handles all Flipside AI chat automation including:
- Authentication and login
- Prompt submission
- Response waiting and monitoring
- Data extraction and artifact capture
"""

from modules.chat_manager.flipside_automation import FlipsideChatManager
from modules.chat_manager.data_extractor import DataExtractor
from modules.chat_manager.artifact_capture import ArtifactCapture

__all__ = ['FlipsideChatManager', 'DataExtractor', 'ArtifactCapture']
