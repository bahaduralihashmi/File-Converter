# app/core/__init__.py
"""
Core Package
"""

from .converter import ConverterEngine, ConversionWorker
from .file_manager import FileManager
from .history import HistoryManager
from .settings import SettingsManager
from .ai_engine import ai_engine
from .image_ai import image_ai
from .ffmpeg import ffmpeg_manager

# No new classes added to core

__all__ = [
    'ConverterEngine',
    'ConversionWorker',
    'FileManager',
    'HistoryManager',
    'SettingsManager',
    'ai_engine',
    'image_ai',
    'ffmpeg_manager'
]