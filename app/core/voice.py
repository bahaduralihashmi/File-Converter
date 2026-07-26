"""
Voice Controller - Complete with Advanced Features
Supports: Speech recognition, TTS, wake word, multiple languages, custom commands
"""

import threading
import queue
import tempfile
import os
import wave
import time
import re
from typing import Optional, Callable, Dict, List, Any

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    import sounddevice as sd
    SD_AVAILABLE = True
except ImportError:
    SD_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

from app.utils.logger import get_logger

logger = get_logger(__name__)


class VoiceController:
    """
    Advanced voice controller with:
    - Speech recognition
    - Text-to-speech
    - Command parsing
    - Wake word detection
    - Multiple languages
    - Custom commands
    """
    
    def __init__(self):
        # State
        self.is_listening = False
        self.is_recording = False
        self.command_callback = None
        self.wake_word_callback = None
        self.status_callback = None
        
        # Audio
        self.audio_queue = queue.Queue()
        self.sample_rate = 16000
        self.recording_duration = 4.0
        
        # Speech recognition
        self.recognizer = None
        self.microphone = None
        self.language = 'en-US'
        
        # Text-to-speech
        self.tts = None
        self.tts_voice = None
        self.tts_rate = 150
        self.tts_volume = 0.9
        
        # Commands
        self.commands = {
            # Conversion commands
            'convert_to_pdf': ['convert to pdf', 'make pdf', 'to pdf', 'pdf file'],
            'convert_to_docx': ['convert to docx', 'make docx', 'to word', 'word file'],
            'convert_to_jpg': ['convert to jpg', 'make jpg', 'to jpg', 'image file'],
            'convert_to_png': ['convert to png', 'make png', 'to png'],
            'convert_to_mp3': ['convert to mp3', 'make mp3', 'to mp3', 'audio file'],
            'convert_to_mp4': ['convert to mp4', 'make mp4', 'to mp4', 'video file'],
            'convert_to_zip': ['convert to zip', 'make zip', 'to zip', 'archive', 'compress'],
            
            # File operations
            'add_files': ['add files', 'add file', 'select files', 'browse files'],
            'add_folder': ['add folder', 'select folder', 'browse folder'],
            'clear_files': ['clear files', 'remove all', 'delete all', 'clear list'],
            'remove_file': ['remove file', 'delete file', 'remove selected'],
            
            # Actions
            'scan': ['scan', 'document scan', 'scan document', 'camera'],
            'ocr': ['ocr', 'extract text', 'read text', 'text extraction'],
            'convert': ['convert', 'convert now', 'start conversion'],
            'stop': ['stop', 'cancel', 'stop conversion', 'abort'],
            
            # Navigation
            'dashboard': ['dashboard', 'home', 'main'],
            'history': ['history', 'recent', 'past conversions'],
            'settings': ['settings', 'preferences', 'options'],
            'ai_chat': ['ai chat', 'assistant', 'ai assistant', 'help chat'],
            
            # System
            'status': ['status', 'what is the status', 'how many files', 'progress'],
            'help': ['help', 'commands', 'what can I do', 'what can you do'],
            'clear_history': ['clear history', 'delete history', 'remove history'],
            
            # Theme
            'dark_theme': ['dark theme', 'dark mode', 'night mode'],
            'light_theme': ['light theme', 'light mode', 'day mode'],
            
            # Quality
            'high_quality': ['high quality', 'best quality', 'maximum quality'],
            'medium_quality': ['medium quality', 'normal quality'],
            'low_quality': ['low quality', 'fast', 'small file'],
            
            # Wake word
            'wake': ['hey assistant', 'ok assistant', 'hello assistant', 'wake up', 'assistant'],
        }
        
        # Reverse mapping for faster lookup
        self._command_map = {}
        for cmd, phrases in self.commands.items():
            for phrase in phrases:
                self._command_map[phrase] = cmd
        
        # Wake word
        self.wake_word_enabled = True
        self.wake_word = 'assistant'
        self.wake_word_callback = None
        
        # Initialize components
        self._init_components()
        
        logger.info("Voice Controller initialized")
    
    # ============================================================
    # INITIALIZATION
    # ============================================================
    
    def _init_components(self):
        """Initialize speech recognition and TTS components"""
        # Speech recognition
        if SR_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                
                # Adjust for ambient noise
                with self.microphone as source:
                    logger.info("Adjusting for ambient noise...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                logger.info("Speech recognition initialized")
            except Exception as e:
                logger.warning(f"Speech recognition initialization failed: {e}")
                self.recognizer = None
        else:
            logger.warning("Speech recognition not available")
        
        # Text-to-speech
        if TTS_AVAILABLE:
            try:
                self.tts = pyttsx3.init()
                self._configure_tts()
                logger.info("TTS initialized")
            except Exception as e:
                logger.warning(f"TTS initialization failed: {e}")
                self.tts = None
        else:
            logger.warning("TTS not available")
    
    def _configure_tts(self):
        """Configure TTS settings"""
        if not self.tts:
            return
        
        try:
            # Get available voices
            voices = self.tts.getProperty('voices')
            if voices:
                # Try to find a good voice
                preferred_voices = ['zira', 'david', 'female', 'male']
                for pref in preferred_voices:
                    for voice in voices:
                        if pref.lower() in voice.name.lower():
                            self.tts_voice = voice.id
                            self.tts.setProperty('voice', voice.id)
                            break
                    if self.tts_voice:
                        break
            
            # Set properties
            self.tts.setProperty('rate', self.tts_rate)
            self.tts.setProperty('volume', self.tts_volume)
            
            logger.info(f"TTS configured with voice: {self.tts_voice}")
            
        except Exception as e:
            logger.warning(f"TTS configuration failed: {e}")
    
    # ============================================================
    # VOICE COMMANDS
    # ============================================================
    
    def set_command_callback(self, callback: Callable):
        """Set callback for voice commands"""
        self.command_callback = callback
    
    def set_wake_word_callback(self, callback: Callable):
        """Set callback for wake word detection"""
        self.wake_word_callback = callback
    
    def set_status_callback(self, callback: Callable):
        """Set callback for status updates"""
        self.status_callback = callback
    
    # ============================================================
    # LISTENING CONTROL
    # ============================================================
    
    def start_listening(self, use_wake_word: bool = True):
        """Start listening for voice commands"""
        if not SD_AVAILABLE or not self.recognizer:
            logger.warning("Voice control not available")
            return False
        
        if self.is_listening:
            logger.warning("Already listening")
            return True
        
        self.is_listening = True
        self.wake_word_enabled = use_wake_word
        
        # Start threads
        threading.Thread(target=self._record_loop, daemon=True).start()
        threading.Thread(target=self._process_loop, daemon=True).start()
        
        logger.info("Voice control activated")
        self._speak("Voice control activated")
        return True
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        self.is_recording = False
        logger.info("Voice control deactivated")
        self._speak("Voice control deactivated")
    
    def toggle_listening(self) -> bool:
        """Toggle listening state"""
        if self.is_listening:
            self.stop_listening()
            return False
        else:
            self.start_listening()
            return True
    
    def is_active(self) -> bool:
        """Check if voice control is active"""
        return self.is_listening
    
    # ============================================================
    # RECORDING
    # ============================================================
    
    def _record_loop(self):
        """Record audio from microphone"""
        while self.is_listening:
            try:
                self.is_recording = True
                
                # Record audio
                audio_data = sd.rec(
                    int(self.recording_duration * self.sample_rate),
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='int16'
                )
                sd.wait()
                self.is_recording = False
                
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
                    temp_file = f.name
                
                with wave.open(temp_file, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(audio_data.tobytes())
                
                self.audio_queue.put(temp_file)
                
            except Exception as e:
                logger.error(f"Recording error: {e}")
                self.is_recording = False
                time.sleep(0.5)
    
    def _process_loop(self):
        """Process audio from queue"""
        while self.is_listening:
            try:
                audio_file = self.audio_queue.get(timeout=1)
                
                if self.recognizer and os.path.exists(audio_file):
                    try:
                        with sr.AudioFile(audio_file) as source:
                            audio = self.recognizer.record(source)
                        
                        # Recognize speech
                        try:
                            text = self.recognizer.recognize_google(audio, language=self.language)
                            logger.info(f"Recognized: {text}")
                            self._handle_recognized_text(text.lower())
                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError as e:
                            logger.warning(f"Recognition service error: {e}")
                        except Exception as e:
                            logger.error(f"Recognition error: {e}")
                            
                    except Exception as e:
                        logger.error(f"Audio processing error: {e}")
                
                # Clean up temp file
                try:
                    os.remove(audio_file)
                except:
                    pass
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Processing error: {e}")
    
    # ============================================================
    # COMMAND PARSING
    # ============================================================
    
    def _handle_recognized_text(self, text: str):
        """Handle recognized text"""
        # Check for wake word
        if self.wake_word_enabled and self.wake_word in text:
            logger.info(f"Wake word detected: {text}")
            if self.wake_word_callback:
                self.wake_word_callback()
            # Remove wake word from text
            text = text.replace(self.wake_word, '').strip()
            
            if not text:
                self._speak("Yes? How can I help you?")
                return
        
        # Parse command
        self._parse_command(text)
    
    def _parse_command(self, text: str):
        """Parse and execute voice command"""
        logger.info(f"Parsing command: {text}")
        
        # Check for exact matches first
        for cmd, phrases in self.commands.items():
            for phrase in phrases:
                if phrase in text:
                    self._execute_command(cmd, text)
                    return
        
        # Check for format mentions
        formats = ['pdf', 'docx', 'doc', 'txt', 'jpg', 'jpeg', 'png', 'gif', 
                   'mp3', 'wav', 'mp4', 'avi', 'mov', 'zip', 'rar', '7z']
        
        for fmt in formats:
            if fmt in text and ('convert' in text or 'to' in text):
                self._execute_command(f'convert_to_{fmt}', text)
                return
        
        # Check for other common patterns
        if 'open' in text:
            for folder in ['documents', 'downloads', 'desktop', 'pictures', 'videos']:
                if folder in text:
                    self._execute_command('open_folder', text)
                    return
        
        # Unknown command
        self._speak("I didn't understand that. Try saying 'Help' for available commands.")
    
    def _execute_command(self, command: str, text: str):
        """Execute a voice command"""
        logger.info(f"Executing command: {command}")
        
        # Add to recent commands
        self._update_recent_commands(command)
        
        # Execute based on command
        if command.startswith('convert_to_'):
            if self.command_callback:
                self.command_callback(command)
                self._speak(f"Converting to {command.replace('convert_to_', '').upper()}")
            return
        
        # Map commands to actions
        command_map = {
            'add_files': ('add_files', "Opening file browser"),
            'add_folder': ('add_folder', "Opening folder browser"),
            'clear_files': ('clear_files', "Clearing all files"),
            'remove_file': ('remove_file', "Removing selected file"),
            'scan': ('scan', "Opening camera scanner"),
            'ocr': ('ocr', "Opening OCR extractor"),
            'convert': ('convert', "Starting conversion"),
            'stop': ('stop', "Stopping conversion"),
            'dashboard': ('dashboard', "Going to dashboard"),
            'history': ('history', "Showing history"),
            'settings': ('settings', "Opening settings"),
            'ai_chat': ('ai_chat', "Opening AI assistant"),
            'status': ('status', "Getting status"),
            'help': ('help', "Showing help"),
            'clear_history': ('clear_history', "Clearing history"),
            'dark_theme': ('dark_theme', "Switching to dark theme"),
            'light_theme': ('light_theme', "Switching to light theme"),
            'high_quality': ('high_quality', "Setting quality to high"),
            'medium_quality': ('medium_quality', "Setting quality to medium"),
            'low_quality': ('low_quality', "Setting quality to low"),
        }
        
        if command in command_map:
            cmd, message = command_map[command]
            if self.command_callback:
                self.command_callback(cmd)
                self._speak(message)
            return
        
        # Open folder
        if command == 'open_folder':
            # Extract folder name
            for folder in ['documents', 'downloads', 'desktop', 'pictures', 'videos']:
                if folder in text:
                    if self.command_callback:
                        self.command_callback(f'open_{folder}')
                        self._speak(f"Opening {folder}")
                    return
        
        # Default
        self._speak(f"Command {command} executed")
    
    # ============================================================
    # TEXT-TO-SPEECH
    # ============================================================
    
    def speak(self, text: str, async_mode: bool = True):
        """Speak text"""
        if async_mode:
            threading.Thread(target=self._speak, args=(text,), daemon=True).start()
        else:
            self._speak(text)
    
    def _speak(self, text: str):
        """Internal speak method"""
        if self.tts:
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except Exception as e:
                logger.error(f"TTS error: {e}")
        else:
            logger.info(f"🔊 {text}")
    
    def set_tts_voice(self, voice_name: str):
        """Set TTS voice"""
        if not self.tts:
            return
        
        try:
            voices = self.tts.getProperty('voices')
            for voice in voices:
                if voice_name.lower() in voice.name.lower():
                    self.tts.setProperty('voice', voice.id)
                    self.tts_voice = voice.id
                    logger.info(f"TTS voice set to: {voice.name}")
                    return
            logger.warning(f"Voice not found: {voice_name}")
        except Exception as e:
            logger.error(f"Voice change error: {e}")
    
    def set_tts_rate(self, rate: int):
        """Set TTS speaking rate"""
        if not self.tts:
            return
        
        try:
            self.tts_rate = rate
            self.tts.setProperty('rate', rate)
            logger.info(f"TTS rate set to: {rate}")
        except Exception as e:
            logger.error(f"Rate change error: {e}")
    
    def set_tts_volume(self, volume: float):
        """Set TTS volume (0.0 to 1.0)"""
        if not self.tts:
            return
        
        try:
            self.tts_volume = max(0.0, min(1.0, volume))
            self.tts.setProperty('volume', self.tts_volume)
            logger.info(f"TTS volume set to: {self.tts_volume}")
        except Exception as e:
            logger.error(f"Volume change error: {e}")
    
    # ============================================================
    # LANGUAGE
    # ============================================================
    
    def set_language(self, language: str):
        """Set recognition language"""
        self.language = language
        logger.info(f"Language set to: {language}")
    
    def get_languages(self) -> List[str]:
        """Get available languages"""
        return ['en-US', 'en-GB', 'ur-PK', 'ar-SA', 'fr-FR', 'de-DE', 'es-ES', 'zh-CN']
    
    # ============================================================
    # RECENT COMMANDS
    # ============================================================
    
    def _update_recent_commands(self, command: str):
        """Update recent commands list"""
        if not hasattr(self, '_recent_commands'):
            self._recent_commands = []
        
        self._recent_commands.append(command)
        if len(self._recent_commands) > 20:
            self._recent_commands = self._recent_commands[-20:]
    
    def get_recent_commands(self) -> List[str]:
        """Get recent commands"""
        return getattr(self, '_recent_commands', [])
    
    def clear_recent_commands(self):
        """Clear recent commands"""
        self._recent_commands = []
    
    # ============================================================
    # STATUS
    # ============================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get voice controller status"""
        return {
            'is_listening': self.is_listening,
            'is_recording': self.is_recording,
            'wake_word_enabled': self.wake_word_enabled,
            'wake_word': self.wake_word,
            'language': self.language,
            'tts_available': TTS_AVAILABLE and self.tts is not None,
            'sr_available': SR_AVAILABLE and self.recognizer is not None,
            'sd_available': SD_AVAILABLE,
            'sample_rate': self.sample_rate,
            'recording_duration': self.recording_duration,
            'tts_rate': self.tts_rate,
            'tts_volume': self.tts_volume,
            'commands_count': len(self.commands),
            'recent_commands': len(self.get_recent_commands())
        }
    
    def get_commands(self) -> Dict[str, List[str]]:
        """Get all available commands"""
        return self.commands.copy()
    
    def get_available_commands(self) -> List[str]:
        """Get list of available commands"""
        return list(self.commands.keys())
    
    # ============================================================
    # COMMAND REGISTRATION
    # ============================================================
    
    def register_command(self, command_id: str, phrases: List[str]):
        """Register a custom command"""
        self.commands[command_id] = phrases
        for phrase in phrases:
            self._command_map[phrase] = command_id
        logger.info(f"Registered custom command: {command_id}")
    
    def unregister_command(self, command_id: str):
        """Unregister a custom command"""
        if command_id in self.commands:
            phrases = self.commands[command_id]
            for phrase in phrases:
                if phrase in self._command_map:
                    del self._command_map[phrase]
            del self.commands[command_id]
            logger.info(f"Unregistered command: {command_id}")
    
    # ============================================================
    # SOUND TEST
    # ============================================================
    
    def test_microphone(self) -> bool:
        """Test microphone"""
        if not SD_AVAILABLE:
            logger.warning("Sounddevice not available")
            return False
        
        try:
            logger.info("Testing microphone... (speak for 2 seconds)")
            
            # Record test audio
            duration = 2.0
            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16'
            )
            sd.wait()
            
            # Check if audio has any sound
            max_amplitude = max(abs(audio))
            logger.info(f"Max amplitude: {max_amplitude}")
            
            if max_amplitude > 100:
                logger.info("✅ Microphone test passed")
                self._speak("Microphone test passed")
                return True
            else:
                logger.warning("⚠️ Microphone test failed - low volume detected")
                self._speak("Microphone test failed. Please check your microphone.")
                return False
                
        except Exception as e:
            logger.error(f"Microphone test error: {e}")
            return False
    
    def test_speaker(self):
        """Test speaker"""
        self._speak("Testing speaker. Can you hear me?")
    
    # ============================================================
    # CLEANUP
    # ============================================================
    
    def close(self):
        """Close voice controller and release resources"""
        self.stop_listening()
        
        # Clear audio queue
        while not self.audio_queue.empty():
            try:
                file_path = self.audio_queue.get_nowait()
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
        
        # Clean up TTS
        if self.tts:
            try:
                self.tts.stop()
            except:
                pass
        
        logger.info("Voice Controller closed")


# Singleton instance
voice_controller = VoiceController()