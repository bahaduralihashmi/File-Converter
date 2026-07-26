"""
Batch Processor - Complete with Advanced Features
app/core/batch.py
"""

import threading
import time
from typing import List, Dict, Optional, Callable, Any
from pathlib import Path
from datetime import datetime

from app.converters.batch import BatchConverter
from app.core.file_manager import FileManager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BatchProcessor:
    """
    Batch processing manager with:
    - Progress tracking
    - Pause/Resume support
    - Cancellation
    - Statistics
    - Error handling
    - Callback system
    """
    
    def __init__(self):
        self.batch_converter = BatchConverter()
        self.file_manager = FileManager()
        
        # State
        self.is_processing = False
        self.is_paused = False
        self.should_cancel = False
        self.current_file_index = 0
        self.total_files = 0
        
        # Statistics
        self.stats = {
            'total': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'start_time': None,
            'end_time': None,
            'current_file': None
        }
        
        # Callbacks
        self._progress_callback = None
        self._complete_callback = None
        self._file_callback = None
        self._error_callback = None
        self._pause_callback = None
        self._resume_callback = None
        self._cancel_callback = None
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        logger.info("Batch Processor initialized")
    
    # ============================================================
    # CONFIGURATION
    # ============================================================
    
    def set_callbacks(
        self,
        progress_callback: Optional[Callable] = None,
        complete_callback: Optional[Callable] = None,
        file_callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
        pause_callback: Optional[Callable] = None,
        resume_callback: Optional[Callable] = None,
        cancel_callback: Optional[Callable] = None
    ):
        """
        Set callbacks for batch operations
        
        Args:
            progress_callback: Called with (progress_percent, message, stats)
            complete_callback: Called with (results, stats)
            file_callback: Called with (file_path, index, total, success, message)
            error_callback: Called with (file_path, error_message)
            pause_callback: Called when batch is paused
            resume_callback: Called when batch is resumed
            cancel_callback: Called when batch is cancelled
        """
        self._progress_callback = progress_callback
        self._complete_callback = complete_callback
        self._file_callback = file_callback
        self._error_callback = error_callback
        self._pause_callback = pause_callback
        self._resume_callback = resume_callback
        self._cancel_callback = cancel_callback
        
        # Pass callbacks to batch converter
        self.batch_converter.set_callbacks(
            progress_callback=self._on_converter_progress,
            complete_callback=self._on_converter_complete,
            file_callback=self._on_converter_file,
            error_callback=self._on_converter_error
        )
    
    # ============================================================
    # PROCESSING
    # ============================================================
    
    def process_batch(
        self,
        files: List[str],
        output_format: str,
        output_folder: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> bool:
        """
        Process a batch of files
        
        Args:
            files: List of file paths
            output_format: Target format
            output_folder: Output directory (optional)
            options: Conversion options
            
        Returns:
            bool: True if started successfully
        """
        with self._lock:
            if self.is_processing:
                logger.warning("Batch already in progress")
                return False
            
            if not files:
                logger.warning("No files to process")
                return False
            
            # Reset state
            self.is_processing = True
            self.is_paused = False
            self.should_cancel = False
            self.current_file_index = 0
            self.total_files = len(files)
            
            # Reset stats
            self.stats = {
                'total': len(files),
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'skipped': 0,
                'start_time': datetime.now(),
                'end_time': None,
                'current_file': None
            }
        
        logger.info(f"Starting batch: {len(files)} files -> {output_format}")
        
        # Start in thread
        thread = threading.Thread(
            target=self._process_batch_thread,
            args=(files, output_format, output_folder, options),
            daemon=True
        )
        thread.start()
        
        return True
    
    def _process_batch_thread(
        self,
        files: List[str],
        output_format: str,
        output_folder: Optional[str] = None,
        options: Optional[Dict] = None
    ):
        """Thread worker for batch processing"""
        try:
            # Start conversion
            self.batch_converter.convert_batch(
                files,
                output_format,
                output_folder,
                options
            )
            
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            self._on_converter_error(None, str(e))
        finally:
            with self._lock:
                self.is_processing = False
                self.stats['end_time'] = datetime.now()
    
    # ============================================================
    # CONTROL METHODS
    # ============================================================
    
    def pause(self) -> bool:
        """Pause current batch"""
        with self._lock:
            if not self.is_processing or self.is_paused:
                return False
            
            self.is_paused = True
            self.batch_converter.pause()
        
        logger.info("Batch paused")
        if self._pause_callback:
            self._pause_callback()
        return True
    
    def resume(self) -> bool:
        """Resume current batch"""
        with self._lock:
            if not self.is_processing or not self.is_paused:
                return False
            
            self.is_paused = False
            self.batch_converter.resume()
        
        logger.info("Batch resumed")
        if self._resume_callback:
            self._resume_callback()
        return True
    
    def cancel(self) -> bool:
        """Cancel current batch"""
        with self._lock:
            if not self.is_processing:
                return False
            
            self.should_cancel = True
            self.batch_converter.cancel()
        
        logger.info("Batch cancellation requested")
        if self._cancel_callback:
            self._cancel_callback()
        return True
    
    # ============================================================
    # STATUS METHODS
    # ============================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        with self._lock:
            return {
                'is_processing': self.is_processing,
                'is_paused': self.is_paused,
                'current_file_index': self.current_file_index,
                'total_files': self.total_files,
                'stats': self.stats.copy(),
                'progress_percent': self._calculate_progress()
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        with self._lock:
            return self.stats.copy()
    
    def _calculate_progress(self) -> int:
        """Calculate progress percentage"""
        if self.stats['total'] == 0:
            return 0
        return int((self.stats['processed'] / self.stats['total']) * 100)
    
    def _format_duration(self, start_time, end_time) -> str:
        """Format duration"""
        if not start_time or not end_time:
            return "N/A"
        delta = end_time - start_time
        seconds = delta.total_seconds()
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"
    
    # ============================================================
    # CONVERTER CALLBACKS
    # ============================================================
    
    def _on_converter_progress(self, progress: int, message: str):
        """Handle converter progress"""
        with self._lock:
            self.stats['processed'] = int((progress / 100) * self.total_files)
            self.stats['current_file'] = message
        
        if self._progress_callback:
            self._progress_callback(progress, message, self.stats.copy())
    
    def _on_converter_complete(self, results: List[Dict]):
        """Handle converter completion"""
        with self._lock:
            self.is_processing = False
            self.stats['end_time'] = datetime.now()
            
            # Update stats
            for result in results:
                if result.get('success', False):
                    self.stats['successful'] += 1
                else:
                    self.stats['failed'] += 1
        
        duration = self._format_duration(
            self.stats['start_time'],
            self.stats['end_time']
        )
        
        logger.info(
            f"Batch complete: {self.stats['successful']}/{self.stats['total']} "
            f"successful in {duration}"
        )
        
        if self._complete_callback:
            self._complete_callback(results, self.stats.copy(), duration)
    
    def _on_converter_file(self, file_path: str, success: bool, message: str):
        """Handle individual file completion"""
        with self._lock:
            self.current_file_index += 1
            if success:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1
        
        if self._file_callback:
            self._file_callback(
                file_path,
                self.current_file_index,
                self.total_files,
                success,
                message
            )
    
    def _on_converter_error(self, file_path: str, error_message: str):
        """Handle converter error"""
        if self._error_callback:
            self._error_callback(file_path, error_message)
        else:
            logger.error(f"Batch error: {file_path} - {error_message}")
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def get_summary(self) -> str:
        """Get a summary of current status"""
        status = self.get_status()
        stats = status['stats']
        
        summary = f"""📊 **Batch Processing Summary**

📁 **Total Files:** {stats['total']}
🔄 **Processed:** {stats['processed']}
✅ **Successful:** {stats['successful']}
❌ **Failed:** {stats['failed']}
📈 **Progress:** {status['progress_percent']}%

⏱️ **Started:** {stats['start_time'].strftime('%H:%M:%S') if stats['start_time'] else 'N/A'}
{'⏸️ **Paused:** Yes' if status['is_paused'] else ''}
{'⏹️ **Processing:** Yes' if status['is_processing'] else ''}

📄 **Current File:** {stats.get('current_file', 'N/A')}
"""
        return summary
    
    def estimate_remaining_time(self) -> Optional[int]:
        """Estimate remaining time in seconds"""
        with self._lock:
            if not self.is_processing or self.stats['processed'] == 0:
                return None
            
            if not self.stats['start_time']:
                return None
            
            elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
            processed = self.stats['processed']
            remaining = self.total_files - processed
            
            if processed == 0:
                return None
            
            avg_time = elapsed / processed
            return int(avg_time * remaining)
    
    def reset(self):
        """Reset the processor"""
        with self._lock:
            self.is_processing = False
            self.is_paused = False
            self.should_cancel = False
            self.current_file_index = 0
            self.total_files = 0
            self.stats = {
                'total': 0,
                'processed': 0,
                'successful': 0,
                'failed': 0,
                'skipped': 0,
                'start_time': None,
                'end_time': None,
                'current_file': None
            }
            self.batch_converter.reset()
        
        logger.info("Batch Processor reset")