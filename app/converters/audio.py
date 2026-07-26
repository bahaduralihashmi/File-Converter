"""
Audio Converter - Complete with FFmpeg support
Supports: MP3, WAV, AAC, FLAC, OGG, M4A, WMA, AIFF, OPUS
"""

from pathlib import Path
import os
import subprocess
import tempfile

from app.utils.logger import get_logger

logger = get_logger(__name__)


class AudioConverter:
    """Handles audio conversions using pydub and FFmpeg"""
    
    def __init__(self):
        self.supported_formats = ['mp3', 'wav', 'aac', 'flac', 'ogg', 'm4a', 'wma', 'aiff', 'opus']
        self.bitrates = ['64k', '128k', '192k', '256k', '320k']
        self.sample_rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 96000]
        
    def convert(self, input_path: str, output_path: str, options: dict = None):
        """Convert audio to any supported format"""
        try:
            # Check if input file exists
            if not os.path.exists(input_path):
                return False, f"Input file not found: {input_path}"
            
            # Get FFmpeg path
            ffmpeg_path = self._get_ffmpeg_path()
            if not ffmpeg_path:
                return False, "FFmpeg not found. Please install FFmpeg."
            
            logger.info(f"Using FFmpeg: {ffmpeg_path}")
            
            # Get output extension
            output_ext = Path(output_path).suffix[1:].lower()
            
            # ===== TRY PYDUB FIRST =====
            try:
                return self._convert_with_pydub(input_path, output_path, options, ffmpeg_path)
            except Exception as e:
                logger.warning(f"Pydub conversion failed: {e}")
                # Fallback to direct FFmpeg
                return self._convert_with_ffmpeg(input_path, output_path, ffmpeg_path, options)
                
        except Exception as e:
            return False, f"Audio conversion error: {str(e)}"
    
    def _get_ffmpeg_path(self):
        """Get FFmpeg path from multiple sources"""
        # 1. Check environment variable
        ffmpeg_path = os.environ.get('FFMPEG_BINARY')
        if ffmpeg_path and Path(ffmpeg_path).exists():
            return ffmpeg_path
        
        # 2. Try imageio_ffmpeg
        try:
            import imageio_ffmpeg
            ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
            if ffmpeg_path and Path(ffmpeg_path).exists():
                return ffmpeg_path
        except:
            pass
        
        # 3. Common installation paths
        common_paths = [
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            os.path.expanduser("~\\ffmpeg\\bin\\ffmpeg.exe"),
            os.path.expanduser("~\\Desktop\\ffmpeg\\bin\\ffmpeg.exe"),
        ]
        
        for path in common_paths:
            if Path(path).exists():
                return path
        
        # 4. Check PATH
        try:
            result = subprocess.run(['where', 'ffmpeg'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        return None
    
    def _convert_with_pydub(self, input_path: str, output_path: str, options: dict, ffmpeg_path: str):
        """Convert using pydub (better quality)"""
        from pydub import AudioSegment
        from pydub import utils
        
        # Force pydub to use our ffmpeg
        original_which = utils.which
        
        def forced_which(program):
            if program == 'ffmpeg':
                return ffmpeg_path
            if program == 'ffprobe':
                ffprobe_path = Path(ffmpeg_path).parent / "ffprobe.exe"
                if ffprobe_path.exists():
                    return str(ffprobe_path)
                return ffmpeg_path
            return original_which(program)
        
        utils.which = forced_which
        
        # Set environment variables
        os.environ['FFMPEG'] = ffmpeg_path
        os.environ['FFMPEG_BINARY'] = ffmpeg_path
        
        # Load audio
        audio = AudioSegment.from_file(input_path)
        
        # Apply options
        if options:
            # Sample rate
            if 'sample_rate' in options:
                audio = audio.set_frame_rate(int(options['sample_rate']))
            
            # Volume adjustment
            if 'volume' in options:
                audio = audio + int(options['volume'])  # dB adjustment
            
            # Normalize
            if options.get('normalize', False):
                audio = audio - audio.max_dBFS  # Normalize to 0dB
        
        output_ext = Path(output_path).suffix[1:].lower()
        
        # Export with format-specific options
        export_params = {'format': output_ext}
        
        if output_ext == 'mp3':
            bitrate = options.get('bitrate', '192k') if options else '192k'
            export_params['bitrate'] = bitrate
        elif output_ext == 'wav':
            export_params['parameters'] = ['-acodec', 'pcm_s16le']
        elif output_ext == 'flac':
            export_params['parameters'] = ['-compression_level', '8']
        elif output_ext == 'aac':
            bitrate = options.get('bitrate', '128k') if options else '128k'
            export_params['bitrate'] = bitrate
        elif output_ext == 'ogg':
            export_params['parameters'] = ['-acodec', 'libvorbis', '-q', '6']
        
        # Export
        audio.export(output_path, **export_params)
        
        return True, f"Audio conversion to {output_ext.upper()} successful"
    
    def _convert_with_ffmpeg(self, input_path: str, output_path: str, ffmpeg_path: str, options: dict = None):
        """Direct FFmpeg conversion (fallback)"""
        try:
            cmd = [ffmpeg_path, '-i', input_path, '-y']
            
            # Get output extension
            output_ext = Path(output_path).suffix[1:].lower()
            
            # Add codec options
            if output_ext == 'mp3':
                cmd.extend(['-acodec', 'libmp3lame'])
                bitrate = options.get('bitrate', '192k') if options else '192k'
                cmd.extend(['-b:a', bitrate])
            elif output_ext == 'wav':
                cmd.extend(['-acodec', 'pcm_s16le'])
            elif output_ext == 'flac':
                cmd.extend(['-acodec', 'flac', '-compression_level', '8'])
            elif output_ext == 'aac':
                cmd.extend(['-acodec', 'aac'])
                bitrate = options.get('bitrate', '128k') if options else '128k'
                cmd.extend(['-b:a', bitrate])
            elif output_ext == 'ogg':
                cmd.extend(['-acodec', 'libvorbis', '-q', '6'])
            elif output_ext == 'm4a':
                cmd.extend(['-acodec', 'aac', '-b:a', '128k'])
            else:
                cmd.extend(['-acodec', 'copy'])  # Copy codec for same format
            
            # Sample rate
            if options and 'sample_rate' in options:
                cmd.extend(['-ar', str(options['sample_rate'])])
            
            # Channels
            if options and 'channels' in options:
                cmd.extend(['-ac', str(options['channels'])])
            
            # Volume
            if options and 'volume' in options:
                cmd.extend(['-af', f'volume={options["volume"]}dB'])
            
            cmd.append(output_path)
            
            logger.info(f"Running FFmpeg: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, f"Audio conversion to {output_ext.upper()} successful (FFmpeg)"
            else:
                return False, f"FFmpeg error: {result.stderr[:200]}"
                
        except Exception as e:
            return False, f"FFmpeg conversion error: {str(e)}"
    
    def get_supported_formats(self) -> list:
        """Get all supported input formats"""
        return self.supported_formats
    
    def get_output_formats(self) -> list:
        """Get all supported output formats"""
        return self.supported_formats
    
    def get_format_info(self, format_name: str) -> dict:
        """Get information about a format"""
        info = {
            'mp3': {'name': 'MP3', 'extension': 'mp3', 'mime': 'audio/mpeg', 'lossy': True},
            'wav': {'name': 'WAV', 'extension': 'wav', 'mime': 'audio/wav', 'lossy': False},
            'aac': {'name': 'AAC', 'extension': 'aac', 'mime': 'audio/aac', 'lossy': True},
            'flac': {'name': 'FLAC', 'extension': 'flac', 'mime': 'audio/flac', 'lossy': False},
            'ogg': {'name': 'OGG', 'extension': 'ogg', 'mime': 'audio/ogg', 'lossy': True},
            'm4a': {'name': 'M4A', 'extension': 'm4a', 'mime': 'audio/mp4', 'lossy': True},
            'wma': {'name': 'WMA', 'extension': 'wma', 'mime': 'audio/x-ms-wma', 'lossy': True},
            'aiff': {'name': 'AIFF', 'extension': 'aiff', 'mime': 'audio/aiff', 'lossy': False},
            'opus': {'name': 'OPUS', 'extension': 'opus', 'mime': 'audio/opus', 'lossy': True}
        }
        return info.get(format_name.lower(), {})