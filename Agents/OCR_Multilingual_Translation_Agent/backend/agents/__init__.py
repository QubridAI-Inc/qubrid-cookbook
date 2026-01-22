"""Agent definitions for language detection and translation."""
from .language_detector import create_language_detection_agent
from .translator import create_translation_agent

__all__ = ["create_language_detection_agent", "create_translation_agent"]
