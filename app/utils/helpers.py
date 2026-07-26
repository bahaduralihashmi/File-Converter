"""
Helper Functions - Complete
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from config import Config

def resource_path(relative_path: str) -> Optional[str]:
    """Get absolute path to resource (works for both development and PyInstaller builds)"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = str(Config.BASE_DIR)
    
    full_path = Path(base_path) / relative_path
    return str(full_path) if full_path.exists() else None

def format_file_size(size_bytes: int) -> str:
    """Format file size"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def check_ffmpeg() -> bool:
    """Check if ffmpeg is available"""
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        return ffmpeg_path is not None
    except:
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=2)
            return result.returncode == 0
        except:
            return False

def get_file_icon(file_path: str) -> str:
    """Get icon for file type"""
    ext = Path(file_path).suffix[1:].lower()
    for category, info in Config.SUPPORTED_FORMATS.items():
        if ext in info["extensions"]:
            return info["icon"]
    return "📄"

def get_file_category(file_path: str) -> str:
    """Get category for file"""
    ext = Path(file_path).suffix[1:].lower()
    for category, info in Config.SUPPORTED_FORMATS.items():
        if ext in info["extensions"]:
            return category
    return "Others"

def get_output_folder() -> Path:
    """Get output folder from settings"""
    from app.core.settings import SettingsManager
    settings = SettingsManager.load()
    folder = settings.get("output_folder")
    if folder:
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        return path
    return Path.home() / "Documents" / "Converted"

def safe_filename(filename: str) -> str:
    """Create a safe filename"""
    import re
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip(' .')
    return filename or "untitled"

def get_unique_filename(path: Path) -> Path:
    """Get a unique filename if file exists"""
    if not path.exists():
        return path
    
    counter = 1
    stem = path.stem
    suffix = path.suffix
    
    while True:
        new_path = path.parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1

def ensure_directory(path: Path) -> Path:
    """Ensure directory exists"""
    path.mkdir(parents=True, exist_ok=True)
    return path