"""
Direct Pydub Patch - Forces pydub to use correct FFmpeg path
This must be imported BEFORE any pydub imports
"""

import os
import sys
from pathlib import Path

def patch_pydub_ffmpeg():
    """Directly patch pydub's ffmpeg handling"""
    
    # Find FFmpeg
    ffmpeg_path = None
    ffprobe_path = None
    
    # 1. Try imageio_ffmpeg
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        if ffmpeg_path:
            ffmpeg_path = str(ffmpeg_path)
            ffmpeg_dir = Path(ffmpeg_path).parent
            # Find ffprobe
            for name in ["ffprobe.exe", "ffprobe-win-x86_64-v7.1.exe"]:
                probe_path = ffmpeg_dir / name
                if probe_path.exists():
                    ffprobe_path = str(probe_path)
                    break
    except:
        pass
    
    # 2. Try common paths
    if not ffmpeg_path or not Path(ffmpeg_path).exists():
        common_paths = [
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            os.path.expanduser("~\\ffmpeg\\bin\\ffmpeg.exe"),
        ]
        for path in common_paths:
            if Path(path).exists():
                ffmpeg_path = path
                ffprobe_path = str(Path(path).parent / "ffprobe.exe")
                if not Path(ffprobe_path).exists():
                    ffprobe_path = None
                break
    
    if not ffmpeg_path:
        print("❌ FFmpeg not found! Please install FFmpeg.")
        return False
    
    # ===== SET ENVIRONMENT VARIABLES =====
    os.environ['FFMPEG'] = ffmpeg_path
    os.environ['FFMPEG_BINARY'] = ffmpeg_path
    os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg_path
    
    if ffprobe_path:
        os.environ['FFPROBE'] = ffprobe_path
        os.environ['FFPROBE_BINARY'] = ffprobe_path
    
    # ===== DIRECTLY PATCH PYDUB =====
    try:
        # Import pydub and directly modify its internal variables
        import pydub
        from pydub import utils
        
        # Method 1: Direct assignment
        if hasattr(pydub, 'ffmpeg'):
            pydub.ffmpeg = ffmpeg_path
        if hasattr(pydub, 'ffprobe'):
            pydub.ffprobe = ffprobe_path or ffmpeg_path
        
        # Method 2: Patch the which function
        original_which = utils.which
        
        def new_which(program):
            if program == 'ffmpeg':
                return ffmpeg_path
            if program == 'ffprobe' and ffprobe_path:
                return ffprobe_path
            return original_which(program)
        
        utils.which = new_which
        
        # Method 3: Directly set in the module
        if hasattr(utils, 'ffmpeg'):
            utils.ffmpeg = ffmpeg_path
        if hasattr(utils, 'ffprobe'):
            utils.ffprobe = ffprobe_path or ffmpeg_path
        
        # Method 4: Monkey patch the get_ffmpeg function if it exists
        if hasattr(utils, 'get_ffmpeg'):
            def new_get_ffmpeg():
                return ffmpeg_path
            utils.get_ffmpeg = new_get_ffmpeg
        
        print(f"✅ Pydub patched successfully!")
        print(f"   FFmpeg: {ffmpeg_path}")
        if ffprobe_path:
            print(f"   FFprobe: {ffprobe_path}")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Error patching pydub: {e}")
        return False

def patch_moviepy():
    """Directly patch moviepy"""
    try:
        from moviepy import config
        
        ffmpeg_path = os.environ.get('FFMPEG_BINARY')
        ffprobe_path = os.environ.get('FFPROBE_BINARY')
        
        if ffmpeg_path:
            if hasattr(config, 'FFMPEG_BINARY'):
                config.FFMPEG_BINARY = ffmpeg_path
            if hasattr(config, 'FFPROBE_BINARY') and ffprobe_path:
                config.FFPROBE_BINARY = ffprobe_path
            
            # Try change_settings
            try:
                if hasattr(config, 'change_settings'):
                    config.change_settings({
                        "FFMPEG_BINARY": ffmpeg_path,
                        "FFPROBE_BINARY": ffprobe_path or ffmpeg_path
                    })
            except:
                pass
            
            print(f"✅ MoviePy patched successfully!")
            return True
    except Exception as e:
        print(f"⚠️ Error patching moviepy: {e}")
        return False

# Run the patch immediately when imported
if __name__ != "__main__":
    patch_pydub_ffmpeg()
    patch_moviepy()