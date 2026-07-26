"""
Archive Converter - Complete with proper ZIP creation
Supports: ZIP, RAR, 7Z, TAR, GZ, BZ2, XZ
"""

import os
import shutil
import zipfile
import tarfile
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Dict, List

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Try to import optional libraries
try:
    import py7zr
    PYZ7R_AVAILABLE = True
except ImportError:
    PYZ7R_AVAILABLE = False

try:
    import rarfile
    RARFILE_AVAILABLE = True
except ImportError:
    RARFILE_AVAILABLE = False


class ArchiveConverter:
    """Complete archive converter with proper ZIP support"""
    
    def __init__(self):
        self.supported_formats = [
            'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz',
            'tgz', 'tbz2', 'txz'
        ]
        
        # Formats that can be created
        self.compress_formats = ['zip', '7z', 'tar', 'gz', 'bz2', 'xz', 'tgz']
        
        logger.info("Archive Converter initialized")
        if PYZ7R_AVAILABLE:
            logger.info("7z support: True")
        if RARFILE_AVAILABLE:
            logger.info("RAR support: True")
    
    def convert(self, input_path: str, output_path: str, options: dict = None) -> Tuple[bool, str]:
        """Convert/compress file to archive format"""
        try:
            # Check if input file exists
            if not os.path.exists(input_path):
                return False, f"Input file not found: {input_path}"
            
            input_ext = Path(input_path).suffix[1:].lower()
            output_ext = Path(output_path).suffix[1:].lower()
            
            logger.info(f"Converting: {Path(input_path).name} ({input_ext}) -> {output_ext}")
            
            # ===== CREATE ZIP =====
            if output_ext == 'zip':
                return self._create_zip(input_path, output_path, options)
            
            # ===== CREATE 7Z =====
            elif output_ext == '7z':
                return self._create_7z(input_path, output_path, options)
            
            # ===== CREATE TAR =====
            elif output_ext in ['tar', 'gz', 'bz2', 'xz', 'tgz']:
                return self._create_tar(input_path, output_path, options)
            
            # ===== EXTRACT ARCHIVE =====
            elif input_ext in ['zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'tgz']:
                return self._extract_archive(input_path, output_path, options)
            
            # ===== COPY (fallback) =====
            else:
                shutil.copy2(input_path, output_path)
                return True, f"File copied to {Path(output_path).name}"
            
        except Exception as e:
            logger.error(f"Archive conversion error: {e}")
            return False, f"Archive conversion error: {str(e)}"
    
    # ============================================================
    # CREATE ZIP - FIXED
    # ============================================================
    
    def _create_zip(self, input_path: str, output_path: str, options: dict = None) -> Tuple[bool, str]:
        """Create a valid ZIP archive"""
        try:
            input_path_obj = Path(input_path)
            output_path_obj = Path(output_path)
            
            # Ensure output directory exists
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Get compression level
            compression_level = options.get('compression', 6) if options else 6
            
            # ===== CREATE ZIP =====
            with zipfile.ZipFile(output_path_obj, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # If input is a directory, add all files
                if input_path_obj.is_dir():
                    for file_path in input_path_obj.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(input_path_obj.parent)
                            zipf.write(file_path, arcname, compresslevel=compression_level)
                            logger.info(f"Added: {file_path.name}")
                else:
                    # Single file
                    zipf.write(input_path_obj, input_path_obj.name, compresslevel=compression_level)
                    logger.info(f"Added: {input_path_obj.name}")
            
            # ===== VERIFY ZIP =====
            if output_path_obj.exists() and output_path_obj.stat().st_size > 22:  # Minimum ZIP size
                size_mb = output_path_obj.stat().st_size / (1024 * 1024)
                logger.info(f"✅ ZIP created: {output_path_obj.name} ({size_mb:.2f} MB)")
                
                # Verify ZIP integrity
                try:
                    with zipfile.ZipFile(output_path_obj, 'r') as test_zip:
                        # Test ZIP integrity
                        badfile = test_zip.testzip()
                        if badfile:
                            return False, f"ZIP verification failed: {badfile} is corrupted"
                        file_count = len(test_zip.namelist())
                        logger.info(f"ZIP verified: {file_count} files")
                except Exception as e:
                    logger.warning(f"ZIP verification warning: {e}")
                
                return True, f"ZIP archive created: {output_path_obj.name} ({size_mb:.2f} MB)"
            else:
                return False, "ZIP creation failed - file too small or corrupted"
            
        except Exception as e:
            logger.error(f"ZIP creation error: {e}")
            return False, f"ZIP creation error: {str(e)}"
    
    # ============================================================
    # CREATE 7Z
    # ============================================================
    
    def _create_7z(self, input_path: str, output_path: str, options: dict = None) -> Tuple[bool, str]:
        """Create 7Z archive"""
        try:
            if not PYZ7R_AVAILABLE:
                return False, "py7zr not installed. Install: pip install py7zr"
            
            input_path_obj = Path(input_path)
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with py7zr.SevenZipFile(output_path_obj, mode='w') as archive:
                if input_path_obj.is_dir():
                    for file_path in input_path_obj.rglob('*'):
                        if file_path.is_file():
                            arcname = str(file_path.relative_to(input_path_obj.parent))
                            archive.write(file_path, arcname)
                else:
                    archive.write(input_path_obj, input_path_obj.name)
            
            if output_path_obj.exists() and output_path_obj.stat().st_size > 0:
                size_mb = output_path_obj.stat().st_size / (1024 * 1024)
                return True, f"7Z archive created: {output_path_obj.name} ({size_mb:.2f} MB)"
            else:
                return False, "7Z creation failed"
            
        except Exception as e:
            logger.error(f"7Z creation error: {e}")
            return False, f"7Z creation error: {str(e)}"
    
    # ============================================================
    # CREATE TAR
    # ============================================================
    
    def _create_tar(self, input_path: str, output_path: str, options: dict = None) -> Tuple[bool, str]:
        """Create TAR/GZ/BZ2/XZ archive"""
        try:
            input_path_obj = Path(input_path)
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Determine mode
            output_ext = output_path_obj.suffix[1:].lower()
            if output_ext == 'gz' or output_ext == 'tgz':
                mode = 'w:gz'
            elif output_ext == 'bz2':
                mode = 'w:bz2'
            elif output_ext == 'xz':
                mode = 'w:xz'
            else:
                mode = 'w'
            
            with tarfile.open(output_path_obj, mode) as tar:
                if input_path_obj.is_dir():
                    for file_path in input_path_obj.rglob('*'):
                        if file_path.is_file():
                            arcname = str(file_path.relative_to(input_path_obj.parent))
                            tar.add(file_path, arcname)
                else:
                    tar.add(input_path_obj, input_path_obj.name)
            
            if output_path_obj.exists() and output_path_obj.stat().st_size > 0:
                size_mb = output_path_obj.stat().st_size / (1024 * 1024)
                return True, f"TAR archive created: {output_path_obj.name} ({size_mb:.2f} MB)"
            else:
                return False, "TAR creation failed"
            
        except Exception as e:
            logger.error(f"TAR creation error: {e}")
            return False, f"TAR creation error: {str(e)}"
    
    # ============================================================
    # EXTRACT ARCHIVE
    # ============================================================
    
    def _extract_archive(self, input_path: str, output_path: str, options: dict = None) -> Tuple[bool, str]:
        """Extract archive to folder"""
        try:
            input_ext = Path(input_path).suffix[1:].lower()
            
            # Create output directory
            output_dir = Path(output_path)
            if not output_dir.suffix:
                output_dir.mkdir(parents=True, exist_ok=True)
            else:
                output_dir = output_dir.parent / output_dir.stem
                output_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract based on format
            if input_ext == 'zip':
                with zipfile.ZipFile(input_path, 'r') as zip_ref:
                    zip_ref.extractall(str(output_dir))
                    file_count = len(zip_ref.namelist())
                    return True, f"ZIP extracted: {file_count} files to {output_dir.name}"
            
            elif input_ext == '7z':
                if not PYZ7R_AVAILABLE:
                    return False, "py7zr not installed"
                with py7zr.SevenZipFile(input_path, mode='r') as archive:
                    archive.extractall(path=str(output_dir))
                    return True, f"7Z extracted to {output_dir.name}"
            
            elif input_ext in ['tar', 'gz', 'bz2', 'xz', 'tgz']:
                mode = self._get_tar_mode(input_path)
                with tarfile.open(input_path, mode) as tar:
                    tar.extractall(str(output_dir))
                    file_count = len(tar.getmembers())
                    return True, f"TAR extracted: {file_count} files to {output_dir.name}"
            
            else:
                return False, f"Extraction not supported for {input_ext}"
            
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            return False, f"Extraction error: {str(e)}"
    
    def _get_tar_mode(self, file_path: str) -> str:
        """Get tar mode"""
        file_name = Path(file_path).name
        if file_name.endswith('.tar.gz') or file_name.endswith('.tgz'):
            return 'r:gz'
        elif file_name.endswith('.tar.bz2') or file_name.endswith('.tbz2'):
            return 'r:bz2'
        elif file_name.endswith('.tar.xz') or file_name.endswith('.txz'):
            return 'r:xz'
        else:
            return 'r'
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def get_supported_formats(self) -> list:
        return self.supported_formats
    
    def get_compress_formats(self) -> list:
        return self.compress_formats