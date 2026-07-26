"""
FFmpeg Manager - Fixed for PyInstaller/EXE packaging
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple, Dict  # <-- ADD Dict HERE

from app.utils.logger import get_logger

logger = get_logger(__name__)


class FFmpegManager:
    """Manages FFmpeg and FFprobe paths - Fixed for EXE"""
    
    _instance = None
    _ffmpeg_path: Optional[str] = None
    _ffprobe_path: Optional[str] = None
    _patched: bool = False
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._find_ffmpeg()
            self._find_ffprobe()
            self._patch_libraries()
            self.setup_environment()
            self._initialized = True
    
    def _get_resource_path(self, relative_path: str) -> str:
        """Get path to resource (works for both development and EXE)"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        return os.path.join(base_path, relative_path)
    
    def _find_ffmpeg(self):
        """Find FFmpeg executable - Works in EXE too"""
        # List of possible paths (in priority order)
        possible_paths = []
        
        # 1. Bundled with PyInstaller (when packaged)
        try:
            bundled = self._get_resource_path("ffmpeg/ffmpeg.exe")
            if os.path.exists(bundled):
                possible_paths.append(bundled)
        except:
            pass
        
        # 2. imageio_ffmpeg (virtual environment)
        try:
            import imageio_ffmpeg
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            if ffmpeg_path and os.path.exists(ffmpeg_path):
                possible_paths.append(ffmpeg_path)
        except:
            pass
        
        # 3. Common installation paths
        common_paths = [
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            os.path.join(os.environ.get('USERPROFILE', ''), "ffmpeg\\bin\\ffmpeg.exe"),
            os.path.join(os.environ.get('USERPROFILE', ''), "Desktop\\ffmpeg\\bin\\ffmpeg.exe"),
            os.path.join(os.environ.get('USERPROFILE', ''), "Downloads\\ffmpeg\\bin\\ffmpeg.exe"),
        ]
        possible_paths.extend(common_paths)
        
        # 4. System PATH
        possible_paths.append('ffmpeg')
        
        # Check each path
        for path in possible_paths:
            if path and self._check_ffmpeg_exists(path):
                self._ffmpeg_path = path
                logger.info(f"✅ FFmpeg found: {path}")
                return
        
        # If not found, try to extract from imageio_ffmpeg to local folder
        self._extract_ffmpeg_from_imageio()
        
        logger.warning("⚠️ FFmpeg not found! Some conversions may not work.")
    
    def _check_ffmpeg_exists(self, path: str) -> bool:
        """Check if ffmpeg exists and works"""
        if path == 'ffmpeg':
            try:
                result = subprocess.run(['ffmpeg', '-version'], 
                                      capture_output=True, timeout=2)
                return result.returncode == 0
            except:
                return False
        
        if not os.path.exists(path):
            return False
        
        try:
            result = subprocess.run([path, '-version'], 
                                  capture_output=True, timeout=2)
            return result.returncode == 0
        except:
            return False
    
    def _extract_ffmpeg_from_imageio(self):
        """Extract ffmpeg from imageio_ffmpeg to local folder"""
        try:
            import imageio_ffmpeg
            import shutil
            
            # Get ffmpeg from imageio_ffmpeg
            source = imageio_ffmpeg.get_ffmpeg_exe()
            if not source or not os.path.exists(source):
                return
            
            # Create ffmpeg folder in app directory
            app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            ffmpeg_dir = os.path.join(app_dir, "ffmpeg")
            os.makedirs(ffmpeg_dir, exist_ok=True)
            
            # Copy ffmpeg.exe
            target = os.path.join(ffmpeg_dir, "ffmpeg.exe")
            shutil.copy2(source, target)
            
            # Also copy ffprobe if available
            source_probe = os.path.join(os.path.dirname(source), "ffprobe.exe")
            if os.path.exists(source_probe):
                target_probe = os.path.join(ffmpeg_dir, "ffprobe.exe")
                shutil.copy2(source_probe, target_probe)
                self._ffprobe_path = target_probe
            
            self._ffmpeg_path = target
            logger.info(f"✅ FFmpeg extracted to: {target}")
            
        except Exception as e:
            logger.warning(f"Failed to extract ffmpeg: {e}")
    
    def _find_ffprobe(self):
        """Find FFprobe executable"""
        if self._ffmpeg_path and self._ffmpeg_path != 'ffmpeg':
            # Look next to ffmpeg
            ffmpeg_dir = os.path.dirname(self._ffmpeg_path)
            for name in ["ffprobe.exe", "ffprobe-win-x86_64-v7.1.exe"]:
                ffprobe_path = os.path.join(ffmpeg_dir, name)
                if os.path.exists(ffprobe_path):
                    self._ffprobe_path = ffprobe_path
                    logger.info(f"✅ FFprobe found: {ffprobe_path}")
                    return
        
        # Try common paths
        common_paths = [
            "C:\\ffmpeg\\bin\\ffprobe.exe",
            os.path.join(os.environ.get('USERPROFILE', ''), "ffmpeg\\bin\\ffprobe.exe"),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                self._ffprobe_path = path
                logger.info(f"✅ FFprobe found: {path}")
                return
        
        # Try PATH
        try:
            result = subprocess.run(['ffprobe', '-version'], 
                                  capture_output=True, timeout=2)
            if result.returncode == 0:
                self._ffprobe_path = 'ffprobe'
                logger.info("✅ FFprobe found in PATH")
                return
        except:
            pass
        
        # Use ffmpeg as fallback
        if self._ffmpeg_path:
            self._ffprobe_path = self._ffmpeg_path
            logger.info("Using FFmpeg as FFprobe fallback")
    
    def _patch_libraries(self):
        """Patch pydub and moviepy to use correct paths"""
        if self._patched:
            return
            
        # Patch pydub
        try:
            from pydub import utils
            import pydub
            
            ffmpeg_path = self._ffmpeg_path
            ffprobe_path = self._ffprobe_path
            
            original_which = utils.which
            
            def patched_which(program):
                if program == 'ffmpeg' and ffmpeg_path:
                    return ffmpeg_path
                if program == 'ffprobe' and ffprobe_path:
                    return ffprobe_path
                return original_which(program)
            
            utils.which = patched_which
            
            # Directly set paths
            if hasattr(pydub, 'ffmpeg'):
                pydub.ffmpeg = ffmpeg_path
            if hasattr(pydub, 'ffprobe'):
                pydub.ffprobe = ffprobe_path
            if hasattr(utils, 'ffmpeg'):
                utils.ffmpeg = ffmpeg_path
            if hasattr(utils, 'ffprobe'):
                utils.ffprobe = ffprobe_path
            
            logger.info("✅ Pydub patched successfully")
            
        except Exception as e:
            logger.warning(f"Failed to patch pydub: {e}")
        
        # Patch moviepy
        try:
            from moviepy import config
            
            ffmpeg_path = self._ffmpeg_path
            
            # Set environment variables for moviepy
            os.environ['FFMPEG_BINARY'] = ffmpeg_path or ''
            os.environ['FFPROBE_BINARY'] = self._ffprobe_path or ffmpeg_path or ''
            os.environ['MOVIEPY_FFMPEG'] = ffmpeg_path or ''
            os.environ['MOVIEPY_FFPROBE'] = self._ffprobe_path or ffmpeg_path or ''
            
            # Try direct config
            try:
                if hasattr(config, 'FFMPEG_BINARY'):
                    config.FFMPEG_BINARY = ffmpeg_path
                if hasattr(config, 'FFPROBE_BINARY'):
                    config.FFPROBE_BINARY = self._ffprobe_path or ffmpeg_path
            except:
                pass
            
            logger.info("✅ MoviePy patched successfully")
            
        except Exception as e:
            logger.warning(f"Failed to patch moviepy: {e}")
        
        self._patched = True
    
    def setup_environment(self):
        """Set environment variables"""
        if self._ffmpeg_path:
            os.environ['FFMPEG'] = self._ffmpeg_path
            os.environ['FFMPEG_BINARY'] = self._ffmpeg_path
            os.environ['IMAGEIO_FFMPEG_EXE'] = self._ffmpeg_path
            
        if self._ffprobe_path:
            os.environ['FFPROBE'] = self._ffprobe_path
            os.environ['FFPROBE_BINARY'] = self._ffprobe_path
        
        logger.info(f"✅ FFmpeg environment set: {self._ffmpeg_path}")
        if self._ffprobe_path:
            logger.info(f"✅ FFprobe environment set: {self._ffprobe_path}")
    
    def get_ffmpeg_path(self) -> Optional[str]:
        return self._ffmpeg_path
    
    def get_ffprobe_path(self) -> Optional[str]:
        return self._ffprobe_path
    
    def is_available(self) -> bool:
        return self._ffmpeg_path is not None and os.path.exists(self._ffmpeg_path)
    
    def get_ffmpeg_info(self) -> Dict:  # <-- Now Dict is imported
        """Get FFmpeg version info"""
        try:
            if self._ffmpeg_path:
                result = subprocess.run(
                    [self._ffmpeg_path, '-version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                lines = result.stdout.split('\n')
                return {
                    "available": True,
                    "version": lines[0] if lines else "Unknown",
                    "path": self._ffmpeg_path
                }
        except:
            pass
        
        return {
            "available": False,
            "version": "Not found",
            "path": self._ffmpeg_path or "Not found"
        }


# Global instance
ffmpeg_manager = FFmpegManager()