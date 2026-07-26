"""
File Manager - Complete
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from app.utils.logger import get_logger
from app.utils.helpers import format_file_size

logger = get_logger(__name__)

class FileManager:
    """Handles file operations"""
    
    def __init__(self):
        self.current_files = []
        self.history = []
        
    def add_files(self, file_paths: List[str]) -> int:
        """Add files to the list"""
        added = 0
        for file_path in file_paths:
            if file_path not in self.current_files and os.path.exists(file_path):
                self.current_files.append(file_path)
                added += 1
        return added
        
    def remove_file(self, file_path: str) -> bool:
        """Remove a file from the list"""
        if file_path in self.current_files:
            self.current_files.remove(file_path)
            return True
        return False
        
    def clear_files(self):
        """Clear all files"""
        self.current_files.clear()
        
    def get_files(self) -> List[str]:
        """Get all files"""
        return self.current_files.copy()
        
    def get_file_info(self, file_path: str) -> Dict:
        """Get file information"""
        path = Path(file_path)
        if not path.exists():
            return {}
            
        return {
            'name': path.name,
            'size': path.stat().st_size,
            'size_formatted': format_file_size(path.stat().st_size),
            'extension': path.suffix[1:].lower(),
            'modified': datetime.fromtimestamp(path.stat().st_mtime),
            'created': datetime.fromtimestamp(path.stat().st_ctime),
            'is_file': path.is_file(),
            'is_dir': path.is_dir()
        }
        
    def create_output_path(self, input_path: str, output_format: str, output_folder: Optional[str] = None) -> str:
        """Generate output path for conversion"""
        input_path = Path(input_path)
        if output_folder:
            output_path = Path(output_folder) / f"{input_path.stem}_converted.{output_format}"
        else:
            output_path = input_path.parent / f"{input_path.stem}_converted.{output_format}"
        return str(output_path)
        
    def ensure_directory(self, directory: str):
        """Ensure directory exists"""
        Path(directory).mkdir(parents=True, exist_ok=True)
        
    def get_supported_files(self, folder: str) -> List[str]:
        """Get all supported files in a folder"""
        from config import Config
        files = []
        for ext in Config.ALL_EXTENSIONS:
            for file_path in Path(folder).rglob(f"*.{ext}"):
                files.append(str(file_path))
        return files