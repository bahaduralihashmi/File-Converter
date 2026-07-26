"""
FFmpeg Patcher - Completely fixes FFmpeg/FFprobe for pydub and moviepy
Supports: Standalone, bundled, and system FFmpeg
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple

# Try to import imageio_ffmpeg
try:
    import imageio_ffmpeg
    IMAGEIO_AVAILABLE = True
except ImportError:
    IMAGEIO_AVAILABLE = False


class FFmpegPatcher:
    """
    Complete FFmpeg patcher for pydub and moviepy
    Supports multiple detection methods and fallbacks
    """
    
    def __init__(self):
        self.ffmpeg_path = None
        self.ffprobe_path = None
        self.patched = False
        
        # Common installation paths
        self.common_paths = [
            # System paths
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe",
            # User paths
            os.path.expanduser("~\\ffmpeg\\bin\\ffmpeg.exe"),
            os.path.expanduser("~\\Desktop\\ffmpeg\\bin\\ffmpeg.exe"),
            os.path.expanduser("~\\Downloads\\ffmpeg\\bin\\ffmpeg.exe"),
            # Portable
            os.path.join(os.path.dirname(sys.executable), "ffmpeg", "ffmpeg.exe"),
            # Bundled with app
            os.path.join(os.path.dirname(sys.executable), "ffmpeg\\ffmpeg.exe"),
        ]
        
        # Common ffprobe paths
        self.common_ffprobe_paths = [
            "C:\\ffmpeg\\bin\\ffprobe.exe",
            "C:\\Program Files\\ffmpeg\\bin\\ffprobe.exe",
            os.path.expanduser("~\\ffmpeg\\bin\\ffprobe.exe"),
            os.path.join(os.path.dirname(sys.executable), "ffmpeg", "ffprobe.exe"),
        ]
        
        # Alternative names
        self.ffprobe_alternatives = [
            "ffprobe.exe",
            "ffprobe-win-x86_64-v7.1.exe",
            "ffprobe-win-x86_64-v6.1.exe",
            "ffprobe-vaapi.exe"
        ]
    
    # ============================================================
    # FFMPEG DETECTION
    # ============================================================
    
    def find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg using multiple methods"""
        
        # Method 1: Check if already found
        if self.ffmpeg_path and Path(self.ffmpeg_path).exists():
            return self.ffmpeg_path
        
        # Method 2: Check environment variables
        env_paths = [
            os.environ.get('FFMPEG'),
            os.environ.get('FFMPEG_BINARY'),
            os.environ.get('IMAGEIO_FFMPEG_EXE'),
        ]
        for path in env_paths:
            if path and Path(path).exists():
                self.ffmpeg_path = path
                return path
        
        # Method 3: Try imageio_ffmpeg
        if IMAGEIO_AVAILABLE:
            try:
                path = imageio_ffmpeg.get_ffmpeg_exe()
                if path and Path(path).exists():
                    self.ffmpeg_path = path
                    return path
            except Exception as e:
                print(f"⚠️ imageio_ffmpeg error: {e}")
        
        # Method 4: Check common paths
        for path in self.common_paths:
            if Path(path).exists():
                self.ffmpeg_path = path
                return path
        
        # Method 5: Check system PATH
        try:
            result = subprocess.run(
                ['where', 'ffmpeg'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                path = result.stdout.strip().split('\n')[0]
                if Path(path).exists():
                    self.ffmpeg_path = path
                    return path
        except:
            pass
        
        return None
    
    def find_ffprobe(self, ffmpeg_dir: Optional[Path] = None) -> Optional[str]:
        """Find FFprobe using multiple methods"""
        
        # Method 1: Check if already found
        if self.ffprobe_path and Path(self.ffprobe_path).exists():
            return self.ffprobe_path
        
        # Method 2: Check environment variables
        env_paths = [
            os.environ.get('FFPROBE'),
            os.environ.get('FFPROBE_BINARY'),
        ]
        for path in env_paths:
            if path and Path(path).exists():
                self.ffprobe_path = path
                return path
        
        # Method 3: Look next to ffmpeg
        if ffmpeg_dir and ffmpeg_dir.exists():
            for alt_name in self.ffprobe_alternatives:
                probe_path = ffmpeg_dir / alt_name
                if probe_path.exists():
                    self.ffprobe_path = str(probe_path)
                    return self.ffprobe_path
        
        # Method 4: Check common paths
        for path in self.common_ffprobe_paths:
            if Path(path).exists():
                self.ffprobe_path = path
                return path
        
        # Method 5: Check system PATH
        try:
            result = subprocess.run(
                ['where', 'ffprobe'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                path = result.stdout.strip().split('\n')[0]
                if Path(path).exists():
                    self.ffprobe_path = path
                    return path
        except:
            pass
        
        return None
    
    # ============================================================
    # PATCHING METHODS
    # ============================================================
    
    def patch_pydub(self) -> bool:
        """Patch pydub to use correct FFmpeg/FFprobe paths"""
        try:
            from pydub import utils
            import pydub
            
            ffmpeg_path = self.ffmpeg_path or self.find_ffmpeg()
            if not ffmpeg_path:
                print("❌ FFmpeg not found for pydub patch")
                return False
            
            ffmpeg_dir = Path(ffmpeg_path).parent
            ffprobe_path = self.ffprobe_path or self.find_ffprobe(ffmpeg_dir)
            
            # ===== PATCH THE WHICH FUNCTION =====
            original_which = utils.which
            
            def patched_which(program):
                if program == 'ffmpeg':
                    return ffmpeg_path
                if program == 'ffprobe':
                    return ffprobe_path or ffmpeg_path
                return original_which(program)
            
            utils.which = patched_which
            
            # ===== DIRECT PATCHING =====
            # Set module-level variables
            if hasattr(pydub, 'ffmpeg'):
                pydub.ffmpeg = ffmpeg_path
            if hasattr(pydub, 'ffprobe'):
                pydub.ffprobe = ffprobe_path or ffmpeg_path
            if hasattr(utils, 'ffmpeg'):
                utils.ffmpeg = ffmpeg_path
            if hasattr(utils, 'ffprobe'):
                utils.ffprobe = ffprobe_path or ffmpeg_path
            
            # ===== PATCH GET_FFMPEG FUNCTION =====
            if hasattr(utils, 'get_ffmpeg'):
                def patched_get_ffmpeg():
                    return ffmpeg_path
                utils.get_ffmpeg = patched_get_ffmpeg
            
            # ===== SET ENVIRONMENT VARIABLES =====
            os.environ['FFMPEG'] = ffmpeg_path
            os.environ['FFMPEG_BINARY'] = ffmpeg_path
            if ffprobe_path:
                os.environ['FFPROBE'] = ffprobe_path
                os.environ['FFPROBE_BINARY'] = ffprobe_path
            
            print(f"✅ Pydub patched with FFmpeg: {ffmpeg_path}")
            if ffprobe_path:
                print(f"✅ Pydub patched with FFprobe: {ffprobe_path}")
            
            return True
            
        except ImportError as e:
            print(f"⚠️ Pydub not installed: {e}")
            return False
        except Exception as e:
            print(f"❌ Failed to patch pydub: {e}")
            return False
    
    def patch_moviepy(self) -> bool:
        """Patch moviepy to use correct FFmpeg paths"""
        try:
            from moviepy import config
            import moviepy
            
            ffmpeg_path = self.ffmpeg_path or self.find_ffmpeg()
            if not ffmpeg_path:
                print("❌ FFmpeg not found for moviepy patch")
                return False
            
            ffmpeg_dir = Path(ffmpeg_path).parent
            ffprobe_path = self.ffprobe_path or self.find_ffprobe(ffmpeg_dir)
            
            # ===== METHOD 1: Direct config patching =====
            if hasattr(config, 'FFMPEG_BINARY'):
                config.FFMPEG_BINARY = ffmpeg_path
            if hasattr(config, 'FFPROBE_BINARY'):
                config.FFPROBE_BINARY = ffprobe_path or ffmpeg_path
            
            # ===== METHOD 2: Using change_settings =====
            try:
                if hasattr(config, 'change_settings'):
                    config.change_settings({
                        "FFMPEG_BINARY": ffmpeg_path,
                        "FFPROBE_BINARY": ffprobe_path or ffmpeg_path
                    })
            except:
                pass
            
            # ===== METHOD 3: Direct module-level =====
            if hasattr(moviepy, 'FFMPEG_BINARY'):
                moviepy.FFMPEG_BINARY = ffmpeg_path
            if hasattr(moviepy, 'FFPROBE_BINARY'):
                moviepy.FFPROBE_BINARY = ffprobe_path or ffmpeg_path
            
            # ===== METHOD 4: Settings dict =====
            if hasattr(config, '_settings'):
                config._settings['FFMPEG_BINARY'] = ffmpeg_path
                config._settings['FFPROBE_BINARY'] = ffprobe_path or ffmpeg_path
            
            print(f"✅ MoviePy patched with FFmpeg: {ffmpeg_path}")
            if ffprobe_path:
                print(f"✅ MoviePy patched with FFprobe: {ffprobe_path}")
            
            return True
            
        except ImportError as e:
            print(f"⚠️ MoviePy not installed: {e}")
            return False
        except Exception as e:
            print(f"❌ Failed to patch moviepy: {e}")
            return False
    
    def patch_imageio(self) -> bool:
        """Patch imageio_ffmpeg to use correct paths"""
        try:
            if not IMAGEIO_AVAILABLE:
                print("⚠️ imageio_ffmpeg not available")
                return False
            
            ffmpeg_path = self.ffmpeg_path or self.find_ffmpeg()
            if ffmpeg_path:
                os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg_path
            
            print(f"✅ imageio_ffmpeg patched: {ffmpeg_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to patch imageio: {e}")
            return False
    
    def patch_ffmpeg_python(self) -> bool:
        """Patch ffmpeg-python to use correct paths"""
        try:
            import ffmpeg
            ffmpeg_path = self.ffmpeg_path or self.find_ffmpeg()
            if ffmpeg_path:
                # ffmpeg-python uses environment variables
                os.environ['FFMPEG_BINARY'] = ffmpeg_path
            print(f"✅ ffmpeg-python patched: {ffmpeg_path}")
            return True
        except ImportError:
            print("⚠️ ffmpeg-python not installed")
            return False
        except Exception as e:
            print(f"❌ Failed to patch ffmpeg-python: {e}")
            return False
    
    # ============================================================
    # MAIN PATCH METHOD
    # ============================================================
    
    def patch_all(self, verbose: bool = True) -> bool:
        """Apply all patches"""
        if verbose:
            print("=" * 60)
            print("🔧 Applying FFmpeg patches...")
            print("=" * 60)
        
        # Find FFmpeg first
        ffmpeg_path = self.find_ffmpeg()
        if not ffmpeg_path:
            print("❌ FFmpeg not found on the system!")
            print("   Please install FFmpeg from: https://ffmpeg.org/download.html")
            print("   Or run: fix_ffmpeg.py to download automatically")
            return False
        
        if verbose:
            print(f"📁 FFmpeg found at: {ffmpeg_path}")
        
        # Find FFprobe
        ffmpeg_dir = Path(ffmpeg_path).parent
        ffprobe_path = self.find_ffprobe(ffmpeg_dir)
        if ffprobe_path and verbose:
            print(f"📁 FFprobe found at: {ffprobe_path}")
        elif verbose:
            print("⚠️ FFprobe not found (fallback: using ffmpeg)")
        
        # Apply patches
        success = True
        
        # Patch pydub
        if not self.patch_pydub():
            success = False
        
        # Patch moviepy
        if not self.patch_moviepy():
            success = False
        
        # Patch imageio
        if not self.patch_imageio():
            success = False
        
        # Patch ffmpeg-python
        if not self.patch_ffmpeg_python():
            # Not critical
            pass
        
        # Set final environment variables
        os.environ['FFMPEG'] = ffmpeg_path
        os.environ['FFMPEG_BINARY'] = ffmpeg_path
        if ffprobe_path:
            os.environ['FFPROBE'] = ffprobe_path
            os.environ['FFPROBE_BINARY'] = ffprobe_path
        
        self.patched = success
        
        if verbose:
            print("=" * 60)
            if success:
                print("✅ All patches applied successfully!")
                print(f"   FFmpeg: {ffmpeg_path}")
                print(f"   FFprobe: {ffprobe_path or 'Not found (using ffmpeg as fallback)'}")
            else:
                print("⚠️ Some patches failed. Please check manually.")
            print("=" * 60)
        
        return success
    
    # ============================================================
    # VERIFICATION
    # ============================================================
    
    def verify_patches(self) -> bool:
        """Verify that patches are applied correctly"""
        try:
            # Test pydub
            try:
                from pydub import utils
                ffmpeg = utils.which('ffmpeg')
                if not ffmpeg:
                    print("❌ Pydub patch verification failed")
                    return False
                print(f"✅ Pydub sees FFmpeg at: {ffmpeg}")
            except:
                pass
            
            # Test moviepy
            try:
                from moviepy.config import FFMPEG_BINARY
                if not FFMPEG_BINARY:
                    print("❌ MoviePy patch verification failed")
                    return False
                print(f"✅ MoviePy sees FFmpeg at: {FFMPEG_BINARY}")
            except:
                pass
            
            return True
            
        except Exception as e:
            print(f"⚠️ Verification error: {e}")
            return False
    
    # ============================================================
    # STATUS
    # ============================================================
    
    def get_status(self) -> dict:
        """Get current patch status"""
        return {
            'ffmpeg_path': self.ffmpeg_path or self.find_ffmpeg(),
            'ffprobe_path': self.ffprobe_path or self.find_ffprobe(),
            'patched': self.patched,
            'imageio_available': IMAGEIO_AVAILABLE
        }


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

def patch_pydub():
    """Convenience function to patch pydub only"""
    patcher = FFmpegPatcher()
    return patcher.patch_pydub()


def patch_moviepy():
    """Convenience function to patch moviepy only"""
    patcher = FFmpegPatcher()
    return patcher.patch_moviepy()


def patch_all(verbose: bool = True) -> bool:
    """Convenience function to apply all patches"""
    patcher = FFmpegPatcher()
    return patcher.patch_all(verbose)


def get_ffmpeg_path() -> Optional[str]:
    """Get FFmpeg path"""
    patcher = FFmpegPatcher()
    return patcher.find_ffmpeg()


def get_ffprobe_path() -> Optional[str]:
    """Get FFprobe path"""
    patcher = FFmpegPatcher()
    return patcher.find_ffprobe()


def verify_patches() -> bool:
    """Verify all patches"""
    patcher = FFmpegPatcher()
    return patcher.verify_patches()


def get_status() -> dict:
    """Get patch status"""
    patcher = FFmpegPatcher()
    return patcher.get_status()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='FFmpeg Patcher')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--verify', action='store_true', help='Verify patches')
    parser.add_argument('--status', action='store_true', help='Show status')
    
    args = parser.parse_args()
    
    if args.verify:
        print("Verifying patches...")
        success = verify_patches()
        print(f"Verification {'✅ PASSED' if success else '❌ FAILED'}")
    elif args.status:
        print("Patch Status:")
        for key, value in get_status().items():
            print(f"  {key}: {value}")
    else:
        patch_all(verbose=True)