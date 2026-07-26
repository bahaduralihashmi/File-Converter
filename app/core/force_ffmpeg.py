"""
Force FFmpeg - Complete fix for pydub and moviepy (NO pydub.convert)
"""

import os
import sys
from pathlib import Path
import subprocess

def force_ffmpeg_paths():
    """Force all libraries to use the correct FFmpeg paths"""
    
    # Get FFmpeg path from imageio_ffmpeg
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_dir = Path(ffmpeg_path).parent
    except:
        ffmpeg_path = "C:\\ffmpeg\\bin\\ffmpeg.exe"
        ffmpeg_dir = Path("C:\\ffmpeg\\bin")
    
    # Find ffprobe
    ffprobe_path = None
    possible_ffprobe = [
        ffmpeg_dir / "ffprobe.exe",
        ffmpeg_dir / "ffprobe-win-x86_64-v7.1.exe",
        Path("C:\\ffmpeg\\bin\\ffprobe.exe"),
        Path("C:\\ffmpeg\\ffprobe.exe"),
    ]
    
    for p in possible_ffprobe:
        if p.exists():
            ffprobe_path = str(p)
            break
    
    if not ffprobe_path:
        # Try to find ffprobe in PATH
        try:
            result = subprocess.run(['where', 'ffprobe'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                ffprobe_path = result.stdout.strip().split('\n')[0]
        except:
            pass
    
    # ===== SET ENVIRONMENT VARIABLES =====
    os.environ['FFMPEG'] = ffmpeg_path
    os.environ['FFMPEG_BINARY'] = ffmpeg_path
    os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg_path
    
    if ffprobe_path:
        os.environ['FFPROBE'] = ffprobe_path
        os.environ['FFPROBE_BINARY'] = ffprobe_path
    else:
        os.environ['FFPROBE_BINARY'] = ffmpeg_path
    
    # ===== PATCH PYDUB (NO pydub.convert) =====
    try:
        from pydub import utils
        import pydub
        
        # Override the which function
        def pydub_which(program):
            if program == 'ffmpeg':
                return ffmpeg_path
            if program == 'ffprobe' and ffprobe_path:
                return ffprobe_path
            return None
        
        utils.which = pydub_which
        
        # Directly set the ffmpeg variable in pydub (not pydub.convert)
        if hasattr(pydub, 'ffmpeg'):
            pydub.ffmpeg = ffmpeg_path
        if hasattr(pydub, 'ffprobe'):
            pydub.ffprobe = ffprobe_path or ffmpeg_path
            
        # Also set in the utils module
        if hasattr(utils, 'ffmpeg'):
            utils.ffmpeg = ffmpeg_path
        if hasattr(utils, 'ffprobe'):
            utils.ffprobe = ffprobe_path or ffmpeg_path
            
        print(f"✅ Pydub patched with: {ffmpeg_path}")
        if ffprobe_path:
            print(f"✅ Pydub ffprobe patched with: {ffprobe_path}")
            
    except Exception as e:
        print(f"⚠️ Pydub patch error: {e}")
    
    # ===== PATCH MOVIEPY =====
    try:
        from moviepy import config
        
        if hasattr(config, 'FFMPEG_BINARY'):
            config.FFMPEG_BINARY = ffmpeg_path
        if hasattr(config, 'FFPROBE_BINARY'):
            config.FFPROBE_BINARY = ffprobe_path or ffmpeg_path
            
        # Also set in the config dict if exists
        if hasattr(config, '_settings'):
            config._settings['FFMPEG_BINARY'] = ffmpeg_path
            config._settings['FFPROBE_BINARY'] = ffprobe_path or ffmpeg_path
            
        print(f"✅ MoviePy patched with: {ffmpeg_path}")
        
    except Exception as e:
        print(f"⚠️ MoviePy patch error: {e}")
    
    # ===== VERIFY =====
    print("\n" + "=" * 60)
    print("FFmpeg Configuration:")
    print(f"FFmpeg path: {ffmpeg_path}")
    print(f"FFprobe path: {ffprobe_path or 'Using FFmpeg as fallback'}")
    print("=" * 60)
    
    return ffmpeg_path, ffprobe_path

def test_ffmpeg():
    """Test if FFmpeg is working"""
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        print(f"✅ imageio_ffmpeg path: {ffmpeg_path}")
        
        # Test pydub
        from pydub import AudioSegment
        print("✅ Pydub imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    force_ffmpeg_paths()
    test_ffmpeg()