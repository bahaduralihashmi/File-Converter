"""
Batch Converter - Complete with Enhanced Features
Handles batch conversion of multiple files with progress tracking
"""

import os
import threading
from pathlib import Path
from typing import List, Dict, Optional, Callable, Any
from datetime import datetime
import time

from app.utils.logger import get_logger
from app.converters.document import DocumentConverter
from app.converters.image import ImageConverter
from app.converters.audio import AudioConverter
from app.converters.video import VideoConverter
from app.converters.archive import ArchiveConverter
from app.converters.ebook import EBookConverter
from app.converters.spreadsheet import SpreadsheetConverter

logger = get_logger(__name__)


class BatchConverter:
    """Handles batch conversion operations with progress tracking"""
    
    def __init__(self):
        # Initialize all converters
        self.converters = {
            'document': DocumentConverter(),
            'image': ImageConverter(),
            'audio': AudioConverter(),
            'video': VideoConverter(),
            'archive': ArchiveConverter(),
            'ebook': EBookConverter(),
            'spreadsheet': SpreadsheetConverter()
        }
        
        # State
        self.is_running = False
        self.is_paused = False
        self.should_cancel = False
        self.progress_callback = None
        self.complete_callback = None
        self.file_callback = None
        self.error_callback = None
        
        # Statistics
        self.stats = {
            'total': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None
        }
        
    def set_callbacks(self, 
                      progress_callback: Optional[Callable] = None,
                      complete_callback: Optional[Callable] = None,
                      file_callback: Optional[Callable] = None,
                      error_callback: Optional[Callable] = None):
        """
        Set callbacks for batch operations
        
        Args:
            progress_callback: Called with (progress_percent, message)
            complete_callback: Called with (results_list)
            file_callback: Called with (file_path, success, message)
            error_callback: Called with (file_path, error_message)
        """
        self.progress_callback = progress_callback
        self.complete_callback = complete_callback
        self.file_callback = file_callback
        self.error_callback = error_callback
        
    def convert_batch(self, 
                      files: List[str], 
                      output_format: str, 
                      output_folder: Optional[str] = None, 
                      options: Optional[Dict] = None) -> bool:
        """
        Convert multiple files in batch
        
        Args:
            files: List of file paths to convert
            output_format: Target format (e.g., 'pdf', 'mp3')
            output_folder: Output directory (optional)
            options: Conversion options
            
        Returns:
            bool: True if batch started successfully
        """
        if self.is_running:
            logger.warning("Batch conversion already running")
            return False
        
        if not files:
            logger.warning("No files to convert")
            return False
        
        # Reset stats
        self.stats = {
            'total': len(files),
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': datetime.now(),
            'end_time': None
        }
        
        self.is_running = True
        self.should_cancel = False
        self.is_paused = False
        self.options = options or {}
        
        logger.info(f"Starting batch conversion: {len(files)} files -> {output_format}")
        
        # Start conversion in thread
        thread = threading.Thread(
            target=self._process_batch,
            args=(files, output_format, output_folder),
            daemon=True
        )
        thread.start()
        return True
        
    def _process_batch(self, files: List[str], output_format: str, output_folder: Optional[str] = None):
        """Process batch conversion in background"""
        total = len(files)
        results = []
        
        for i, file_path in enumerate(files):
            # Check if cancelled
            if self.should_cancel:
                logger.info("Batch conversion cancelled by user")
                break
            
            # Check if paused
            while self.is_paused and not self.should_cancel:
                time.sleep(0.5)
            
            # Update progress
            progress = int((i + 1) / total * 100)
            file_name = Path(file_path).name
            
            if self.progress_callback:
                self.progress_callback(progress, f"Converting {file_name} ({i+1}/{total})...")
            
            # Convert single file
            result = self._convert_single(file_path, output_format, output_folder)
            results.append(result)
            
            # Update stats
            self.stats['processed'] += 1
            if result.get('success', False):
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1
            
            # Call file callback
            if self.file_callback:
                self.file_callback(
                    file_path,
                    result.get('success', False),
                    result.get('message', '')
                )
            
            # Call error callback if failed
            if not result.get('success', False) and self.error_callback:
                self.error_callback(
                    file_path,
                    result.get('error', result.get('message', 'Unknown error'))
                )
            
            logger.info(f"Progress: {i+1}/{total} - {file_name} - {'✅' if result['success'] else '❌'}")
        
        # Finalize
        self.is_running = False
        self.stats['end_time'] = datetime.now()
        
        # Calculate duration
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        logger.info(f"Batch complete: {self.stats['successful']}/{self.stats['total']} successful in {duration:.1f}s")
        
        if self.complete_callback:
            self.complete_callback({
                'results': results,
                'stats': self.stats,
                'duration': duration
            })
        
        return results
    
    def _convert_single(self, file_path: str, output_format: str, output_folder: Optional[str] = None) -> Dict[str, Any]:
        """Convert a single file"""
        try:
            input_path = Path(file_path)
            
            # Check if file exists
            if not input_path.exists():
                return {
                    'input': file_path,
                    'success': False,
                    'error': f"File not found: {file_path}",
                    'output': None,
                    'format': output_format,
                    'message': 'File not found'
                }
            
            # Check if file is empty
            if input_path.stat().st_size == 0:
                return {
                    'input': file_path,
                    'success': False,
                    'error': f"File is empty: {file_path}",
                    'output': None,
                    'format': output_format,
                    'message': 'Empty file'
                }
            
            # Determine file type/category
            input_ext = input_path.suffix[1:].lower()
            category = self._get_category(input_ext)
            
            # Get appropriate converter
            converter_key = self._get_converter_key(category, input_ext, output_format)
            converter = self.converters.get(converter_key)
            
            if not converter:
                return {
                    'input': file_path,
                    'success': False,
                    'error': f'No converter for {category} ({input_ext})',
                    'output': None,
                    'format': output_format,
                    'message': f'Unsupported format: {input_ext}'
                }
            
            # Generate output path
            if output_folder:
                output_path = Path(output_folder) / f"{input_path.stem}_converted.{output_format}"
            else:
                output_path = input_path.parent / f"{input_path.stem}_converted.{output_format}"
            
            # Ensure unique filename
            counter = 1
            while output_path.exists():
                output_path = Path(output_path.parent) / f"{input_path.stem}_converted_{counter}.{output_format}"
                counter += 1
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert with options
            success, message = converter.convert(
                str(file_path),
                str(output_path),
                self.options
            )
            
            # Get file size
            size = 0
            if success and output_path.exists():
                size = output_path.stat().st_size
            
            return {
                'input': file_path,
                'output': str(output_path) if success else None,
                'format': output_format,
                'success': success,
                'message': message,
                'size': size,
                'size_formatted': self._format_size(size) if size else '0 B',
                'input_size': input_path.stat().st_size,
                'input_size_formatted': self._format_size(input_path.stat().st_size),
                'category': category,
                'input_ext': input_ext
            }
            
        except Exception as e:
            logger.error(f"Batch conversion error for {file_path}: {e}")
            return {
                'input': file_path,
                'success': False,
                'error': str(e),
                'output': None,
                'format': output_format,
                'message': f"Error: {str(e)}"
            }
    
    def _get_category(self, extension: str) -> str:
        """Get category for extension"""
        from config import Config
        for category, info in Config.SUPPORTED_FORMATS.items():
            if extension in info["extensions"]:
                return category
        return "Others"
    
    def _get_converter_key(self, category: str, input_ext: str, output_format: str) -> str:
        """Get converter key based on category and formats"""
        # Map categories to converter keys
        category_map = {
            'Documents': 'document',
            'Images': 'image',
            'Audio': 'audio',
            'Video': 'video',
            'Archives': 'archive',
            'E-books': 'ebook',
            'Spreadsheets': 'spreadsheet'
        }
        
        # Check if it's an e-book (based on extension)
        ebook_formats = ['epub', 'mobi', 'azw3', 'fb2', 'lit', 'lrf', 'azw', 'kfx']
        if input_ext in ebook_formats or output_format in ebook_formats:
            return 'ebook'
        
        # Check if it's a spreadsheet
        spreadsheet_formats = ['xlsx', 'xls', 'csv', 'ods', 'tsv']
        if input_ext in spreadsheet_formats or output_format in spreadsheet_formats:
            return 'spreadsheet'
        
        return category_map.get(category, 'document')
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def cancel(self):
        """Cancel current batch operation"""
        self.should_cancel = True
        logger.info("Batch cancellation requested")
    
    def pause(self):
        """Pause current batch operation"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            logger.info("Batch paused")
            return True
        return False
    
    def resume(self):
        """Resume paused batch operation"""
        if self.is_running and self.is_paused:
            self.is_paused = False
            logger.info("Batch resumed")
            return True
        return False
    
    def get_stats(self) -> Dict:
        """Get current statistics"""
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'total': self.stats['total'],
            'processed': self.stats['processed'],
            'successful': self.stats['successful'],
            'failed': self.stats['failed'],
            'skipped': self.stats['skipped'],
            'progress_percent': int((self.stats['processed'] / self.stats['total']) * 100) if self.stats['total'] > 0 else 0,
            'start_time': self.stats['start_time'],
            'end_time': self.stats['end_time']
        }
    
    def get_converter_for_file(self, file_path: str) -> Optional[str]:
        """Get the appropriate converter for a file"""
        ext = Path(file_path).suffix[1:].lower()
        category = self._get_category(ext)
        return self._get_converter_key(category, ext, '')