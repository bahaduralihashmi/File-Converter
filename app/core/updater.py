"""
Updater - Complete
"""

import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
import requests

from app.utils.logger import get_logger
from config import Config

logger = get_logger(__name__)

class Updater:
    """Application updater"""
    
    def __init__(self):
        self.current_version = Config.APP_VERSION
        self.update_url = "https://api.aiconverterpro.com/updates"
        self.update_info = None
        
    def check_for_updates(self) -> Tuple[bool, Optional[Dict]]:
        """Check if updates are available"""
        try:
            response = requests.get(
                self.update_url,
                params={
                    "version": self.current_version,
                    "platform": platform.system(),
                    "arch": platform.machine()
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("update_available", False):
                    self.update_info = data
                    return True, data
                    
            return False, None
            
        except Exception as e:
            logger.error(f"Update check error: {e}")
            return False, None
            
    def download_update(self, download_path: Path) -> bool:
        """Download update"""
        if not self.update_info:
            return False
            
        try:
            download_url = self.update_info.get("download_url")
            if not download_url:
                return False
                
            response = requests.get(download_url, stream=True, timeout=30)
            if response.status_code == 200:
                with open(download_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                return True
                
        except Exception as e:
            logger.error(f"Download update error: {e}")
            return False
            
    def install_update(self, download_path: Path) -> bool:
        """Install the update"""
        try:
            if platform.system() == "Windows":
                # Run installer silently
                subprocess.Popen(
                    [str(download_path), "/VERYSILENT", "/SUPPRESSMSGBOXES"],
                    shell=True
                )
                # Exit current application
                sys.exit(0)
                return True
            else:
                # For other platforms
                subprocess.Popen([str(download_path)], shell=True)
                sys.exit(0)
                return True
                
        except Exception as e:
            logger.error(f"Install update error: {e}")
            return False
            
    def get_update_info(self) -> Dict:
        """Get update information"""
        return self.update_info or {
            "version": self.current_version,
            "available": False,
            "release_notes": "No updates available"
        }