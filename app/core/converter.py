# app/core/converter.py
"""
Converter Engine - Complete with All Format Support
"""

import os
import threading
from pathlib import Path
from typing import Optional, Dict, Tuple, Callable, List, Any
from datetime import datetime

from app.utils.logger import get_logger
from app.converters.document import DocumentConverter
from app.converters.image import ImageConverter
from app.converters.audio import AudioConverter
from app.converters.video import VideoConverter
from app.converters.archive import ArchiveConverter
from app.converters.ebook import EBookConverter
from app.converters.spreadsheet import SpreadsheetConverter
from app.converters.batch import BatchConverter

logger = get_logger(__name__)


class ConverterEngine:
    """
    Converter engine using specialized converters
    Supports: Documents, Images, Audio, Video, Archives, E-books, Spreadsheets
    """
    
    def __init__(self):
        # Initialize all specialized converters
        self.document = DocumentConverter()
        self.image = ImageConverter()
        self.audio = AudioConverter()
        self.video = VideoConverter()
        self.archive = ArchiveConverter()
        self.ebook = EBookConverter()
        self.spreadsheet = SpreadsheetConverter()
        self.batch = BatchConverter()
        
        # Callbacks
        self.progress_callback = None
        self.complete_callback = None
        self.file_callback = None
        self.error_callback = None
        
        # State
        self.is_converting = False
        self.current_file = None
        self.total_files = 0
        self.processed_files = 0
        
        # Cache for format detection
        self._format_cache = {}
        
        logger.info("Converter Engine initialized")
        self._log_supported_formats()
    
    # ============================================================
    # CONVERSION METHODS
    # ============================================================
    
    def convert_file(
        self,
        input_path: str,
        output_format: str,
        output_path: str,
        options: Optional[Dict] = None
    ) -> bool:
        """Convert a file using the appropriate specialized converter"""
        try:
            input_file = Path(input_path)
            if not input_file.exists():
                logger.error(f"Input file not found: {input_path}")
                return False
            
            # Check if file is empty
            if input_file.stat().st_size == 0:
                logger.error(f"Input file is empty: {input_path}")
                return False
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            input_ext = input_file.suffix[1:].lower()
            output_ext = output_format.lower()
            
            logger.info(f"Converting: {input_file.name} ({input_ext}) -> {output_ext}")
            
            # Update state
            self.current_file = str(input_file)
            self.is_converting = True
            
            # Get the appropriate converter
            converter, category = self._get_converter(input_ext, output_ext)
            
            if not converter:
                logger.error(f"No converter found for {input_ext} -> {output_ext}")
                self.is_converting = False
                return False
            
            # Convert using the specialized converter with options
            success, message = converter.convert(str(input_path), str(output_path), options)
            
            self.is_converting = False
            
            if success:
                logger.info(f"✅ Conversion successful: {output_file.name}")
                return True
            else:
                logger.error(f"❌ Conversion failed: {message}")
                return False
                
        except Exception as e:
            self.is_converting = False
            logger.error(f"Conversion error: {e}")
            return False
    
    def convert_files(
        self,
        files: List[str],
        output_format: str,
        output_folder: Optional[str] = None,
        options: Optional[Dict] = None,
        ask_each: bool = False
    ) -> List[Dict[str, Any]]:
        """Convert multiple files"""
        results = []
        self.total_files = len(files)
        self.processed_files = 0
        
        for i, file_path in enumerate(files):
            self.processed_files = i + 1
            self.current_file = file_path
            
            # Generate output path
            input_file = Path(file_path)
            
            if ask_each:
                # Will be handled by caller
                output_path = None
            elif output_folder:
                output_path = Path(output_folder) / f"{input_file.stem}_converted.{output_format}"
            else:
                output_path = input_file.parent / f"{input_file.stem}_converted.{output_format}"
            
            # Ensure unique filename
            if not ask_each:
                counter = 1
                while output_path.exists():
                    output_path = Path(output_path.parent) / f"{input_file.stem}_converted_{counter}.{output_format}"
                    counter += 1
            
            # Convert
            success = False
            error = None
            
            try:
                if ask_each:
                    # Will be handled by caller with custom path
                    success = self.convert_file(file_path, output_format, str(output_path), options)
                else:
                    success = self.convert_file(file_path, output_format, str(output_path), options)
            except Exception as e:
                success = False
                error = str(e)
            
            result = {
                'input': file_path,
                'output': str(output_path) if success else None,
                'format': output_format,
                'success': success,
                'error': error,
                'size': output_path.stat().st_size if success and output_path.exists() else 0
            }
            results.append(result)
            
            # Callbacks
            if self.file_callback:
                self.file_callback(file_path, success, result)
            
            if self.progress_callback:
                progress = int((self.processed_files / self.total_files) * 100)
                self.progress_callback(progress, f"Converting {Path(file_path).name}...")
        
        return results
    
    def convert_with_options(
        self,
        input_path: str,
        output_format: str,
        output_path: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """Convert file with options"""
        try:
            input_file = Path(input_path)
            if not input_file.exists():
                return False, f"Input file not found: {input_path}"
            
            # Generate output path if not provided
            if output_path is None:
                output_path = str(input_file.parent / f"{input_file.stem}_converted.{output_format}")
            
            return self.convert_file(input_path, output_format, output_path, options)
            
        except Exception as e:
            return False, f"Conversion error: {str(e)}"
    
    # ============================================================
    # CONVERTER DETECTION
    # ============================================================
    
    def _get_converter(self, input_ext: str, output_ext: str):
        """
        Get the appropriate converter for the file types
        Uses priority-based detection
        """
        # Create cache key
        cache_key = f"{input_ext}->{output_ext}"
        if cache_key in self._format_cache:
            return self._format_cache[cache_key]
        
        # ===== CHECK E-BOOK FORMATS =====
        ebook_formats = ['epub', 'mobi', 'azw3', 'fb2', 'lit', 'lrf', 'azw', 'kfx']
        if input_ext in ebook_formats or output_ext in ebook_formats:
            result = (self.ebook, 'ebook')
            self._format_cache[cache_key] = result
            return result
        
        # ===== CHECK SPREADSHEET FORMATS =====
        spreadsheet_formats = ['xlsx', 'xls', 'csv', 'ods', 'tsv', 'numbers']
        if input_ext in spreadsheet_formats or output_ext in spreadsheet_formats:
            result = (self.spreadsheet, 'spreadsheet')
            self._format_cache[cache_key] = result
            return result
        
        # ===== CHECK DOCUMENT FORMATS =====
        document_formats = self.document.supported_formats
        if input_ext in document_formats or output_ext in document_formats:
            result = (self.document, 'document')
            self._format_cache[cache_key] = result
            return result
        
        # ===== CHECK IMAGE FORMATS =====
        image_formats = self.image.supported_formats
        if input_ext in image_formats or output_ext in image_formats:
            result = (self.image, 'image')
            self._format_cache[cache_key] = result
            return result
        
        # ===== CHECK AUDIO FORMATS =====
        audio_formats = self.audio.supported_formats
        if input_ext in audio_formats or output_ext in audio_formats:
            result = (self.audio, 'audio')
            self._format_cache[cache_key] = result
            return result
        
        # ===== CHECK VIDEO FORMATS =====
        video_formats = self.video.video_formats
        if input_ext in video_formats or output_ext in video_formats:
            result = (self.video, 'video')
            self._format_cache[cache_key] = result
            return result
        
        # ===== CHECK ARCHIVE FORMATS =====
        archive_formats = self.archive.supported_formats
        if input_ext in archive_formats or output_ext in archive_formats:
            result = (self.archive, 'archive')
            self._format_cache[cache_key] = result
            return result
        
        # ===== DEFAULT =====
        result = (self.document, 'document')
        self._format_cache[cache_key] = result
        return result
    
    # ============================================================
    # FORMAT INFORMATION
    # ============================================================
    
    def get_supported_formats(self) -> Dict[str, list]:
        """Get all supported formats by category"""
        return {
            'Documents': self.document.supported_formats,
            'Images': self.image.supported_formats,
            'Audio': self.audio.supported_formats,
            'Video': self.video.video_formats,
            'Archives': self.archive.supported_formats,
            'E-books': self.ebook.supported_formats,
            'Spreadsheets': self.spreadsheet.supported_formats
        }
    
    def get_all_formats(self) -> List[str]:
        """Get all supported formats as a list"""
        formats = []
        for category, format_list in self.get_supported_formats().items():
            formats.extend(format_list)
        return sorted(set(formats))
    
    def get_format_category(self, format_name: str) -> Optional[str]:
        """Get category for a format"""
        format_name = format_name.lower()
        for category, format_list in self.get_supported_formats().items():
            if format_name in format_list:
                return category
        return None
    
    def get_conversion_info(self, input_format: str, output_format: str) -> Dict[str, Any]:
        """Get information about a conversion"""
        input_ext = input_format.lower()
        output_ext = output_format.lower()
        
        converter, category = self._get_converter(input_ext, output_ext)
        
        return {
            'input_format': input_ext,
            'output_format': output_ext,
            'category': category,
            'converter': converter.__class__.__name__,
            'is_supported': converter is not None,
            'converter_available': converter is not None
        }
    
    def is_format_supported(self, format_name: str) -> bool:
        """Check if a format is supported"""
        return format_name.lower() in self.get_all_formats()
    
    def is_conversion_supported(self, input_format: str, output_format: str) -> bool:
        """Check if a conversion is supported"""
        converter, _ = self._get_converter(input_format.lower(), output_format.lower())
        return converter is not None
    
    # ============================================================
    # CALLBACKS
    # ============================================================
    
    def set_callbacks(
        self,
        progress_callback: Optional[Callable] = None,
        complete_callback: Optional[Callable] = None,
        file_callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None
    ):
        """Set callbacks for conversion"""
        self.progress_callback = progress_callback
        self.complete_callback = complete_callback
        self.file_callback = file_callback
        self.error_callback = error_callback
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get conversion statistics"""
        return {
            'is_converting': self.is_converting,
            'current_file': self.current_file,
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'progress_percent': int((self.processed_files / self.total_files) * 100) if self.total_files > 0 else 0,
            'total_formats': len(self.get_all_formats()),
            'categories': len(self.get_supported_formats())
        }
    
    def _log_supported_formats(self):
        """Log supported formats"""
        formats = self.get_supported_formats()
        total = sum(len(f) for f in formats.values())
        logger.info(f"📊 Supported formats: {total} formats across {len(formats)} categories")
        for category, format_list in formats.items():
            logger.info(f"  📁 {category}: {len(format_list)} formats")
    
    def reset(self):
        """Reset converter state"""
        self.is_converting = False
        self.current_file = None
        self.total_files = 0
        self.processed_files = 0
        self._format_cache = {}
        logger.info("Converter Engine reset")


class ConversionWorker:
    """
    Worker class for background conversion
    Supports threading and cancellation
    """
    
    def __init__(self):
        self.engine = ConverterEngine()
        self.is_running = False
        self.progress = 0
        self.status = ""
        self._thread = None
        self._should_stop = False
    
    def convert(
        self,
        input_path: str,
        output_format: str,
        output_path: str,
        options: Optional[Dict] = None,
        progress_callback: Optional[Callable] = None,
        complete_callback: Optional[Callable] = None
    ) -> bool:
        """Run conversion with callbacks"""
        self.is_running = True
        self._should_stop = False
        
        self.engine.progress_callback = progress_callback
        self.engine.complete_callback = complete_callback
        
        try:
            result = self.engine.convert_file(input_path, output_format, output_path, options)
            self.is_running = False
            
            if complete_callback:
                complete_callback(result, output_path)
            
            return result
            
        except Exception as e:
            self.is_running = False
            logger.error(f"Conversion worker error: {e}")
            
            if complete_callback:
                complete_callback(False, output_path)
            
            return False
    
    def convert_async(
        self,
        input_path: str,
        output_format: str,
        output_path: str,
        options: Optional[Dict] = None,
        progress_callback: Optional[Callable] = None,
        complete_callback: Optional[Callable] = None
    ):
        """Run conversion asynchronously in a thread"""
        if self.is_running:
            logger.warning("Conversion already in progress")
            return False
        
        self.is_running = True
        self._should_stop = False
        
        self._thread = threading.Thread(
            target=self.convert,
            args=(input_path, output_format, output_path, options, progress_callback, complete_callback),
            daemon=True
        )
        self._thread.start()
        return True
    
    def stop(self):
        """Stop conversion"""
        self._should_stop = True
        self.is_running = False
        logger.info("Conversion worker stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get worker status"""
        return {
            'is_running': self.is_running,
            'progress': self.progress,
            'status': self.status,
            'engine_stats': self.engine.get_stats()
        }
    
    def convert_batch_with_location(
        self,
        files: List[str],
        output_format: str,
        output_folder: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Convert multiple files with location handling"""
        return self.engine.convert_files(files, output_format, output_folder, options)
    
    def convert_file_with_location(
        self,
        input_path: str,
        output_format: str,
        output_path: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """Convert file with optional custom save location"""
        return self.engine.convert_with_options(input_path, output_format, output_path, options)