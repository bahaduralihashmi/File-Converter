# app/utils/logger.py
"""
Logging Configuration - Fixed for Program Files permission
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime


def setup_logging():
    """Setup logging configuration with permission handling"""
    
    # ===== FIX: Use AppData for logs =====
    try:
        # Get AppData path
        appdata = Path(os.environ.get('APPDATA', str(Path.home() / 'AppData' / 'Roaming')))
        log_dir = appdata / 'All Files Converter AI' / 'logs'
    except:
        # Fallback to temp directory
        import tempfile
        log_dir = Path(tempfile.gettempdir()) / 'All_Files_Converter_AI' / 'logs'
    
    # Create log directory with error handling
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # Fallback to temp directory
        import tempfile
        log_dir = Path(tempfile.gettempdir()) / 'All_Files_Converter_AI' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Log file
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Remove existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("PySide6").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    logging.info(f"Logging initialized: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)