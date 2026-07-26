"""
Video Converter - Complete with All Formats Support
Supports: MP4, AVI, MOV, MKV, WEBM, FLV, WMV, M4V, 3GP, MPG, M2TS
Audio: MP3, WAV, AAC, FLAC, OGG, M4A, WMA, AIFF, OPUS
"""

from pathlib import Path
from moviepy import VideoFileClip, AudioFileClip, ImageClip, concatenate_videoclips
import os
import subprocess
import tempfile
import shutil
import time
import re

from app.core.ffmpeg import ffmpeg_manager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VideoConverter:
    """Complete video converter with all format support"""
    
    def __init__(self):
        # All video formats
        self.video_formats = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv', 'm4v', '3gp', 'mpg', 'mpeg', 'm2ts']
        self.audio_formats = ['mp3', 'wav', 'aac', 'flac', 'ogg', 'm4a', 'wma', 'aiff', 'opus']
        self.audio_to_video_formats = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv']
        
        # Supported output formats
        self.output_formats = self.video_formats + self.audio_formats
        
    def convert(self, input_path: str, output_path: str, options: dict = None):
        """Convert video/audio to any supported format"""
        try:
            ffmpeg_manager.setup_environment()
            
            input_ext = Path(input_path).suffix[1:].lower()
            output_ext = Path(output_path).suffix[1:].lower()
            
            # Check if input file exists
            if not Path(input_path).exists():
                return False, f"Input file not found: {input_path}"
            
            # Check if input file is empty
            if Path(input_path).stat().st_size == 0:
                return False, f"Input file is empty: {input_path}"
            
            logger.info(f"Converting: {input_path} -> {output_path}")
            logger.info(f"Input: {input_ext}, Output: {output_ext}")
            
            # ===== CONVERSION CASES =====
            
            # Case 1: Audio to Video (MP3 → MP4)
            if input_ext in self.audio_formats and output_ext in self.audio_to_video_formats:
                return self._audio_to_video(input_path, output_path, options)
            
            # Case 2: Video to Audio (MP4 → MP3)
            if input_ext in self.video_formats and output_ext in self.audio_formats:
                return self._video_to_audio(input_path, output_path, options)
            
            # Case 3: Video to Video (MP4 → AVI)
            if input_ext in self.video_formats and output_ext in self.video_formats:
                return self._video_to_video(input_path, output_path, options)
            
            # Case 4: Audio to Audio (MP3 → WAV)
            if input_ext in self.audio_formats and output_ext in self.audio_formats:
                return self._audio_to_audio(input_path, output_path, options)
            
            return False, f"Unsupported conversion: {input_ext} → {output_ext}"
            
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return False, f"Conversion error: {str(e)}"
    
    # ============================================================
    # AUDIO TO VIDEO (MP3 → MP4)
    # ============================================================
    
    def _audio_to_video(self, input_path: str, output_path: str, options: dict = None):
        """Convert audio to video with visual elements"""
        try:
            # Try MoviePy first
            success, message = self._audio_to_video_moviepy(input_path, output_path, options)
            if success:
                return True, message
            
            # Fallback to FFmpeg
            success, message = self._audio_to_video_ffmpeg(input_path, output_path, options)
            if success:
                return True, message
            
            return False, "All audio to video conversion methods failed"
            
        except Exception as e:
            logger.error(f"Audio to video error: {e}")
            return False, f"Audio to video conversion error: {str(e)}"
    
    def _audio_to_video_moviepy(self, input_path: str, output_path: str, options: dict = None):
        """Convert audio to video using MoviePy - WITH VISIBLE CONTENT"""
        try:
            from moviepy import AudioFileClip, ImageClip, TextClip, CompositeVideoClip
            from PIL import Image, ImageDraw, ImageFont
            import tempfile
            import numpy as np
            
            logger.info("🎬 Creating video from audio...")
            
            # Load audio
            audio = AudioFileClip(input_path)
            duration = audio.duration
            
            logger.info(f"⏱️ Audio duration: {duration:.2f} seconds")
            
            # Get options
            width = options.get('width', 1280) if options else 1280
            height = options.get('height', 720) if options else 720
            
            # ===== CREATE VISUAL IMAGE WITH BRIGHT COLORS =====
            img = Image.new('RGB', (width, height), color=(25, 30, 50))  # Dark blue background
            
            # Create gradient effect (lighter at top, darker at bottom)
            draw = ImageDraw.Draw(img)
            for y in range(height):
                ratio = y / height
                r = int(25 + ratio * 60)
                g = int(30 + ratio * 50)
                b = int(50 + ratio * 80)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            
            # ===== ADD WAVEFORM =====
            try:
                import numpy as np
                # Generate a waveform
                wave_points = 300
                for i in range(wave_points):
                    x = int(80 + i * ((width - 160) / wave_points))
                    # Create a sine wave pattern
                    wave_value = abs(np.sin(i / 20 + 0.5)) * 0.5 + 0.5
                    height_val = int(wave_value * 150 + 30)
                    
                    # Color gradient for waveform
                    color_intensity = int(100 + wave_value * 155)
                    color = (color_intensity, int(100 + wave_value * 100), 255)
                    
                    draw.line([(x, height//2 - height_val), (x, height//2 + height_val)], 
                            fill=color, width=3)
            except:
                pass
            
            # ===== ADD TITLE TEXT =====
            try:
                font_large = ImageFont.truetype("arialbd.ttf", 52)
                font_medium = ImageFont.truetype("arial.ttf", 28)
                font_small = ImageFont.truetype("arial.ttf", 18)
            except:
                font_large = ImageFont.load_default()
                font_medium = font_large
                font_small = font_large
            
            # Title (file name)
            title = Path(input_path).stem
            # Truncate if too long
            if len(title) > 40:
                title = title[:37] + "..."
            
            # Draw title with shadow
            bbox = draw.textbbox((0, 0), title, font=font_large)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Shadow
            draw.text(((width - text_width) // 2 + 2, height//2 - 80 + 2), 
                    title, fill=(0, 0, 0), font=font_large)
            # Main text
            draw.text(((width - text_width) // 2, height//2 - 80), 
                    title, fill=(255, 255, 255), font=font_large)
            
            # ===== ADD DURATION =====
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            duration_text = f"⏱️ Duration: {minutes:02d}:{seconds:02d}"
            
            bbox = draw.textbbox((0, 0), duration_text, font=font_medium)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, height//2 + 30), 
                    duration_text, fill=(108, 99, 255), font=font_medium)
            
            # ===== ADD FOOTER =====
            footer = "🎵 Converted by All Files Converter AI"
            bbox = draw.textbbox((0, 0), footer, font=font_small)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, height - 60), 
                    footer, fill=(180, 180, 180), font=font_small)
            
            # ===== ADD DECORATIVE LINE =====
            draw.line([(width//4, height - 90), (3*width//4, height - 90)], 
                    fill=(108, 99, 255), width=2)
            
            # ===== SAVE IMAGE TO TEMP =====
            temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            img.save(temp_image.name)
            temp_image.close()
            
            logger.info(f"🖼️ Created visual image: {temp_image.name}")
            
            # ===== CREATE VIDEO =====
            image_clip = ImageClip(temp_image.name, duration=duration)
            video = image_clip.set_audio(audio)
            
            # ===== WRITE VIDEO FILE =====
            logger.info(f"📝 Writing video: {output_path}")
            
            video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=24,
                verbose=False,
                logger=None,
                bitrate='2000k',
                preset='medium'
            )
            
            # ===== CLEANUP =====
            audio.close()
            video.close()
            image_clip.close()
            
            try:
                os.unlink(temp_image.name)
            except:
                pass
            
            # ===== VERIFY OUTPUT =====
            if Path(output_path).exists() and Path(output_path).stat().st_size > 0:
                size_mb = Path(output_path).stat().st_size / (1024 * 1024)
                logger.info(f"✅ Audio to video successful! Size: {size_mb:.2f} MB")
                return True, f"Audio converted to video: {Path(output_path).name} ({size_mb:.1f} MB)"
            else:
                return False, "Output file is empty"
            
        except Exception as e:
            logger.error(f"MoviePy audio to video error: {e}")
            return False, f"MoviePy error: {str(e)}"
    
    def _audio_to_video_ffmpeg(self, input_path: str, output_path: str, options: dict = None):
        """Convert audio to video using FFmpeg"""
        try:
            ffmpeg_path = ffmpeg_manager.get_ffmpeg_path()
            if not ffmpeg_path:
                return False, "FFmpeg not found"
            
            logger.info("Using FFmpeg for audio to video conversion")
            
            # Get audio duration
            result = subprocess.run(
                [ffmpeg_path, '-i', input_path],
                capture_output=True, text=True, stderr=subprocess.PIPE
            )
            
            duration = 30  # Default
            duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d+)', result.stderr)
            if duration_match:
                h, m, s = duration_match.groups()
                duration = int(h) * 3600 + int(m) * 60 + float(s)
            
            # Get width/height from options
            width = options.get('width', 1280) if options else 1280
            height = options.get('height', 720) if options else 720
            
            # Create video with color background and audio
            ffmpeg_cmd = [
                ffmpeg_path,
                '-f', 'lavfi',
                '-i', f'color=c=0x141428:s={width}x{height}:r=24:d={duration}',
                '-i', input_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',
                '-pix_fmt', 'yuv420p',
                '-y',
                output_path
            ]
            
            logger.info(f"Running FFmpeg: {' '.join(ffmpeg_cmd)}")
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and Path(output_path).exists() and Path(output_path).stat().st_size > 0:
                logger.info(f"✅ FFmpeg audio to video successful")
                return True, f"Audio converted to video: {Path(output_path).name}"
            else:
                return False, f"FFmpeg error: {result.stderr[:200] if result.stderr else 'Unknown error'}"
            
        except Exception as e:
            logger.error(f"FFmpeg audio to video error: {e}")
            return False, f"FFmpeg error: {str(e)}"
    
    # ============================================================
    # VIDEO TO AUDIO (MP4 → MP3)
    # ============================================================
    
    def _video_to_audio(self, input_path: str, output_path: str, options: dict = None):
        """Extract audio from video"""
        try:
            # Try MoviePy first
            success, message = self._video_to_audio_moviepy(input_path, output_path, options)
            if success:
                return True, message
            
            # Try FFmpeg
            success, message = self._video_to_audio_ffmpeg(input_path, output_path, options)
            if success:
                return True, message
            
            return False, "All video to audio extraction methods failed"
            
        except Exception as e:
            logger.error(f"Video to audio error: {e}")
            return False, f"Video to audio conversion error: {str(e)}"
    
    def _video_to_audio_moviepy(self, input_path: str, output_path: str, options: dict = None):
        """Extract audio using MoviePy"""
        try:
            logger.info("Using MoviePy for video to audio extraction")
            
            clip = VideoFileClip(input_path)
            audio = clip.audio
            
            if audio is None:
                clip.close()
                return False, "No audio track found in video"
            
            output_ext = Path(output_path).suffix[1:].lower()
            
            # Get bitrate from options
            bitrate = options.get('bitrate', '192k') if options else '192k'
            
            # Write audio file
            audio.write_audiofile(
                output_path,
                codec='libmp3lame' if output_ext == 'mp3' else 'pcm_s16le',
                fps=44100,
                nbytes=2,
                bitrate=bitrate,
                verbose=False,
                logger=None
            )
            
            audio.close()
            clip.close()
            
            if Path(output_path).exists() and Path(output_path).stat().st_size > 0:
                logger.info(f"✅ Audio extraction successful")
                return True, f"Audio extracted: {Path(output_path).name}"
            else:
                return False, "MoviePy extraction produced empty file"
            
        except Exception as e:
            logger.error(f"MoviePy video to audio error: {e}")
            return False, f"MoviePy error: {str(e)}"
    
    def _video_to_audio_ffmpeg(self, input_path: str, output_path: str, options: dict = None):
        """Extract audio using FFmpeg"""
        try:
            ffmpeg_path = ffmpeg_manager.get_ffmpeg_path()
            if not ffmpeg_path:
                return False, "FFmpeg not found"
            
            logger.info("Using FFmpeg for video to audio extraction")
            
            output_ext = Path(output_path).suffix[1:].lower()
            
            ffmpeg_cmd = [
                ffmpeg_path,
                '-i', input_path,
                '-vn',  # No video
            ]
            
            if output_ext == 'mp3':
                ffmpeg_cmd.extend(['-acodec', 'libmp3lame'])
                bitrate = options.get('bitrate', '192k') if options else '192k'
                ffmpeg_cmd.extend(['-b:a', bitrate])
            elif output_ext == 'wav':
                ffmpeg_cmd.extend(['-acodec', 'pcm_s16le'])
            elif output_ext == 'aac':
                ffmpeg_cmd.extend(['-acodec', 'aac'])
                bitrate = options.get('bitrate', '128k') if options else '128k'
                ffmpeg_cmd.extend(['-b:a', bitrate])
            elif output_ext == 'flac':
                ffmpeg_cmd.extend(['-acodec', 'flac'])
            elif output_ext == 'ogg':
                ffmpeg_cmd.extend(['-acodec', 'libvorbis'])
            else:
                ffmpeg_cmd.extend(['-acodec', 'copy'])
            
            ffmpeg_cmd.extend(['-y', output_path])
            
            logger.info(f"Running FFmpeg: {' '.join(ffmpeg_cmd)}")
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and Path(output_path).exists() and Path(output_path).stat().st_size > 0:
                logger.info(f"✅ FFmpeg audio extraction successful")
                return True, f"Audio extracted: {Path(output_path).name}"
            
            return False, f"FFmpeg error: {result.stderr[:200] if result.stderr else 'Unknown error'}"
            
        except Exception as e:
            logger.error(f"FFmpeg video to audio error: {e}")
            return False, f"FFmpeg error: {str(e)}"
    
    # ============================================================
    # VIDEO TO VIDEO (MP4 → AVI)
    # ============================================================
    
    def _video_to_video(self, input_path: str, output_path: str, options: dict = None):
        """Convert video to another video format"""
        try:
            clip = VideoFileClip(input_path)
            
            # Apply options
            if options:
                # Resolution
                if 'width' in options and 'height' in options:
                    clip = clip.resize((options['width'], options['height']))
                elif 'size' in options:
                    clip = clip.resize(options['size'])
                
                # FPS
                if 'fps' in options:
                    clip = clip.set_fps(options['fps'])
                
                # Trim
                if 'start' in options and 'end' in options:
                    clip = clip.subclip(options['start'], options['end'])
                elif 'start' in options:
                    clip = clip.subclip(options['start'])
                elif 'end' in options:
                    clip = clip.subclip(0, options['end'])
                
                # Speed
                if 'speed' in options:
                    speed = options['speed']
                    clip = clip.speedx(speed)
                
                # Volume
                if 'volume' in options:
                    clip = clip.volumex(options['volume'])
            
            output_ext = Path(output_path).suffix[1:].lower()
            codec = self._get_video_codec(output_ext)
            
            # Write video
            clip.write_videofile(
                output_path,
                codec=codec,
                fps=clip.fps,
                verbose=False,
                logger=None
            )
            clip.close()
            
            if Path(output_path).exists() and Path(output_path).stat().st_size > 0:
                return True, f"Video converted to {output_ext.upper()}"
            else:
                return False, "Video conversion produced empty file"
            
        except Exception as e:
            return False, f"Video conversion error: {str(e)}"
    
    # ============================================================
    # AUDIO TO AUDIO (MP3 → WAV)
    # ============================================================
    
    def _audio_to_audio(self, input_path: str, output_path: str, options: dict = None):
        """Convert audio to another audio format"""
        try:
            from pydub import AudioSegment
            
            logger.info(f"Converting audio: {Path(input_path).name}")
            
            audio = AudioSegment.from_file(input_path)
            
            # Apply options
            if options:
                if 'sample_rate' in options:
                    audio = audio.set_frame_rate(int(options['sample_rate']))
                if 'channels' in options:
                    if options['channels'] == 1:
                        audio = audio.set_channels(1)
                    elif options['channels'] == 2:
                        audio = audio.set_channels(2)
            
            output_ext = Path(output_path).suffix[1:].lower()
            export_params = {'format': output_ext}
            
            if output_ext == 'mp3':
                bitrate = options.get('bitrate', '192k') if options else '192k'
                export_params['bitrate'] = bitrate
            elif output_ext == 'wav':
                export_params['parameters'] = ['-acodec', 'pcm_s16le']
            elif output_ext == 'flac':
                export_params['parameters'] = ['-compression_level', '8']
            
            audio.export(output_path, **export_params)
            
            if Path(output_path).exists() and Path(output_path).stat().st_size > 0:
                return True, f"Audio converted to {output_ext.upper()}"
            else:
                return False, "Audio conversion produced empty file"
            
        except Exception as e:
            return False, f"Audio conversion error: {str(e)}"
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def _get_video_codec(self, format: str) -> str:
        """Get video codec for format"""
        codecs = {
            'mp4': 'libx264',
            'avi': 'mpeg4',
            'mov': 'libx264',
            'mkv': 'libx264',
            'webm': 'libvpx',
            'flv': 'flv',
            'wmv': 'wmv2',
            'm4v': 'libx264',
            '3gp': 'libx264',
            'mpg': 'mpeg1video',
            'mpeg': 'mpeg1video',
            'm2ts': 'libx264'
        }
        return codecs.get(format, 'libx264')
    
    def _get_audio_codec(self, format: str) -> str:
        """Get audio codec for format"""
        codecs = {
            'mp3': 'libmp3lame',
            'wav': 'pcm_s16le',
            'aac': 'aac',
            'flac': 'flac',
            'ogg': 'libvorbis',
            'm4a': 'aac',
            'wma': 'wmav2'
        }
        return codecs.get(format, 'libmp3lame')
    
    def get_supported_formats(self) -> list:
        """Get all supported input formats"""
        return self.video_formats + self.audio_formats
    
    def get_output_formats(self) -> list:
        """Get all supported output formats"""
        return self.output_formats
    
    def get_format_info(self, format_name: str) -> dict:
        """Get information about a format"""
        info = {
            'mp4': {'name': 'MP4', 'extension': 'mp4', 'mime': 'video/mp4'},
            'avi': {'name': 'AVI', 'extension': 'avi', 'mime': 'video/x-msvideo'},
            'mov': {'name': 'MOV', 'extension': 'mov', 'mime': 'video/quicktime'},
            'mkv': {'name': 'MKV', 'extension': 'mkv', 'mime': 'video/x-matroska'},
            'webm': {'name': 'WEBM', 'extension': 'webm', 'mime': 'video/webm'},
            'flv': {'name': 'FLV', 'extension': 'flv', 'mime': 'video/x-flv'},
            'wmv': {'name': 'WMV', 'extension': 'wmv', 'mime': 'video/x-ms-wmv'},
            'm4v': {'name': 'M4V', 'extension': 'm4v', 'mime': 'video/mp4'},
            '3gp': {'name': '3GP', 'extension': '3gp', 'mime': 'video/3gpp'},
            'mpg': {'name': 'MPG', 'extension': 'mpg', 'mime': 'video/mpeg'},
            'mpeg': {'name': 'MPEG', 'extension': 'mpeg', 'mime': 'video/mpeg'},
            'm2ts': {'name': 'M2TS', 'extension': 'm2ts', 'mime': 'video/m2ts'}
        }
        return info.get(format_name.lower(), {})