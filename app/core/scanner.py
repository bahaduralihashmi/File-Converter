"""
Scanner Engine - Complete with Advanced Image Processing
Supports: Document scanning, edge detection, perspective correction, multiple formats
"""

import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
import threading
import time

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ScannerEngine:
    """
    Advanced document scanning engine using camera
    Features: Edge detection, perspective correction, image enhancement
    """
    
    def __init__(self):
        self.camera = None
        self.is_scanning = False
        self.is_previewing = False
        self.capture_callback = None
        self.preview_thread = None
        self.camera_id = 0
        self.resolution = (1280, 720)  # HD resolution
        self.scan_folder = Path("scanned_documents")
        self.scan_folder.mkdir(exist_ok=True)
        
        # Processing settings
        self.settings = {
            'auto_crop': True,
            'perspective_correction': True,
            'enhance_contrast': True,
            'denoise': True,
            'output_quality': 95,
            'threshold': 200,
            'min_area': 5000
        }
        
        logger.info("Scanner Engine initialized")
    
    # ============================================================
    # CAMERA CONTROL
    # ============================================================
    
    def open_camera(self, camera_id: int = 0, resolution: Tuple[int, int] = (1280, 720)) -> bool:
        """Open camera with specified resolution"""
        try:
            if self.camera is not None:
                self.close_camera()
            
            self.camera_id = camera_id
            self.resolution = resolution
            
            self.camera = cv2.VideoCapture(camera_id)
            if not self.camera.isOpened():
                logger.error(f"Failed to open camera {camera_id}")
                return False
            
            # Set resolution
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
            
            # Set other properties for better performance
            self.camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            self.camera.set(cv2.CAP_PROP_BRIGHTNESS, 0.5)
            self.camera.set(cv2.CAP_PROP_CONTRAST, 0.5)
            self.camera.set(cv2.CAP_PROP_SATURATION, 0.5)
            
            logger.info(f"Camera {camera_id} opened with resolution {resolution}")
            return True
            
        except Exception as e:
            logger.error(f"Camera error: {e}")
            return False
    
    def close_camera(self):
        """Close camera and release resources"""
        self.is_previewing = False
        self.is_scanning = False
        
        if self.camera:
            try:
                self.camera.release()
            except:
                pass
            self.camera = None
        
        # Clean up any OpenCV windows
        try:
            cv2.destroyAllWindows()
        except:
            pass
        
        logger.info("Camera closed")
    
    def is_camera_open(self) -> bool:
        """Check if camera is open"""
        return self.camera is not None and self.camera.isOpened()
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Get camera information"""
        if not self.is_camera_open():
            return {'available': False}
        
        return {
            'available': True,
            'camera_id': self.camera_id,
            'resolution': self.resolution,
            'is_scanning': self.is_scanning,
            'is_previewing': self.is_previewing
        }
    
    # ============================================================
    # FRAME CAPTURE
    # ============================================================
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a single frame"""
        if not self.is_camera_open():
            return None
        
        try:
            ret, frame = self.camera.read()
            if ret and frame is not None:
                return frame
            return None
        except Exception as e:
            logger.error(f"Capture error: {e}")
            return None
    
    def capture_frame_with_processing(self, process: bool = True) -> Optional[np.ndarray]:
        """Capture and process a frame"""
        frame = self.capture_frame()
        if frame is None:
            return None
        
        if process:
            return self._process_document(frame)
        return frame
    
    # ============================================================
    # DOCUMENT SCANNING
    # ============================================================
    
    def scan_document(
        self,
        process: bool = True,
        filename: Optional[str] = None,
        output_format: str = 'jpg'
    ) -> Tuple[bool, Optional[str], Optional[np.ndarray]]:
        """
        Scan a document and save it
        
        Args:
            process: Whether to process the image
            filename: Custom filename (optional)
            output_format: Output format (jpg, png, pdf, tiff)
        
        Returns:
            Tuple of (success, filename, processed_image)
        """
        try:
            frame = self.capture_frame()
            if frame is None:
                logger.error("No frame captured")
                return False, None, None
            
            # Process the document
            processed = self._process_document(frame) if process else frame
            
            # Generate filename
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"scanned_document_{timestamp}.{output_format}"
            
            # Ensure output folder exists
            self.scan_folder.mkdir(parents=True, exist_ok=True)
            file_path = self.scan_folder / filename
            
            # Save the image
            success = self._save_image(processed, str(file_path), output_format)
            
            if success:
                logger.info(f"Document scanned: {filename}")
                return True, str(file_path), processed
            else:
                return False, None, None
            
        except Exception as e:
            logger.error(f"Scan error: {e}")
            return False, None, None
    
    def _save_image(self, image: np.ndarray, file_path: str, format: str) -> bool:
        """Save image in specified format"""
        try:
            format = format.lower()
            
            if format == 'jpg' or format == 'jpeg':
                params = [cv2.IMWRITE_JPEG_QUALITY, self.settings['output_quality']]
                return cv2.imwrite(file_path, image, params)
            elif format == 'png':
                params = [cv2.IMWRITE_PNG_COMPRESSION, 6]
                return cv2.imwrite(file_path, image, params)
            elif format == 'tiff' or format == 'tif':
                params = [cv2.IMWRITE_TIFF_COMPRESSION, 1]  # LZW compression
                return cv2.imwrite(file_path, image, params)
            elif format == 'bmp':
                return cv2.imwrite(file_path, image)
            else:
                # Default to JPG
                params = [cv2.IMWRITE_JPEG_QUALITY, self.settings['output_quality']]
                return cv2.imwrite(file_path, image, params)
                
        except Exception as e:
            logger.error(f"Save error: {e}")
            return False
    
    # ============================================================
    # IMAGE PROCESSING
    # ============================================================
    
    def _process_document(self, frame: np.ndarray) -> np.ndarray:
        """Process document image with advanced techniques"""
        try:
            # 1. Detect document corners
            corners = self._detect_document_corners(frame)
            
            # 2. If corners found and perspective correction enabled
            if corners is not None and self.settings['perspective_correction']:
                processed = self._apply_perspective_correction(frame, corners)
            else:
                processed = frame.copy()
            
            # 3. Enhance image quality
            processed = self._enhance_image(processed)
            
            # 4. Auto-crop if enabled
            if self.settings['auto_crop']:
                processed = self._auto_crop(processed)
            
            return processed
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return frame
    
    def _detect_document_corners(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Detect document corners using edge detection"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Edge detection
            edges = cv2.Canny(blurred, 50, 150)
            
            # Dilate edges to close gaps
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None
            
            # Find largest contour
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)
            
            # Check if area is significant
            if area < self.settings['min_area']:
                return None
            
            # Approximate polygon
            epsilon = 0.02 * cv2.arcLength(largest, True)
            approx = cv2.approxPolyDP(largest, epsilon, True)
            
            # If we have 4 corners, return them
            if len(approx) == 4:
                # Reorder corners: top-left, top-right, bottom-right, bottom-left
                corners = self._order_corners(approx.reshape(4, 2))
                return corners
            
            # If more than 4 corners, try to find the 4 most extreme
            if len(approx) > 4:
                # Get bounding rectangle
                rect = cv2.minAreaRect(largest)
                corners = cv2.boxPoints(rect)
                corners = self._order_corners(corners.astype(np.float32))
                return corners
            
            return None
            
        except Exception as e:
            logger.error(f"Corner detection error: {e}")
            return None
    
    def _order_corners(self, corners: np.ndarray) -> np.ndarray:
        """Order corners: top-left, top-right, bottom-right, bottom-left"""
        try:
            # Calculate the center
            center = np.mean(corners, axis=0)
            
            # Calculate angles from center
            angles = np.arctan2(corners[:, 1] - center[1], corners[:, 0] - center[0])
            
            # Sort by angle (clockwise starting from top-left)
            sorted_indices = np.argsort(angles)
            
            # Reorder: TL, TR, BR, BL
            ordered_corners = corners[sorted_indices]
            
            # Ensure correct order
            # TL: smallest x, smallest y
            # TR: largest x, smallest y
            # BR: largest x, largest y
            # BL: smallest x, largest y
            if ordered_corners[0][0] > ordered_corners[1][0]:
                ordered_corners = np.roll(ordered_corners, -1, axis=0)
            
            return ordered_corners
            
        except Exception as e:
            logger.error(f"Corner ordering error: {e}")
            return corners
    
    def _apply_perspective_correction(self, image: np.ndarray, corners: np.ndarray) -> np.ndarray:
        """Apply perspective correction to straighten document"""
        try:
            # Get dimensions
            width, height = self._calculate_dimensions(corners)
            
            # Destination points (top-left, top-right, bottom-right, bottom-left)
            dst = np.array([
                [0, 0],
                [width - 1, 0],
                [width - 1, height - 1],
                [0, height - 1]
            ], dtype=np.float32)
            
            # Calculate perspective transform matrix
            src = corners.astype(np.float32)
            matrix = cv2.getPerspectiveTransform(src, dst)
            
            # Apply transform
            warped = cv2.warpPerspective(image, matrix, (width, height))
            
            return warped
            
        except Exception as e:
            logger.error(f"Perspective correction error: {e}")
            return image
    
    def _calculate_dimensions(self, corners: np.ndarray) -> Tuple[int, int]:
        """Calculate width and height from corners"""
        try:
            # Calculate distances
            width1 = np.linalg.norm(corners[1] - corners[0])
            width2 = np.linalg.norm(corners[2] - corners[3])
            width = int(max(width1, width2))
            
            height1 = np.linalg.norm(corners[3] - corners[0])
            height2 = np.linalg.norm(corners[2] - corners[1])
            height = int(max(height1, height2))
            
            return width, height
            
        except Exception as e:
            logger.error(f"Dimension calculation error: {e}")
            return 1000, 1000
    
    def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Enhance image quality"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Denoise if enabled
            if self.settings['denoise']:
                gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # Enhance contrast if enabled
            if self.settings['enhance_contrast']:
                # CLAHE (Contrast Limited Adaptive Histogram Equalization)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                gray = clahe.apply(gray)
            
            # Apply threshold
            # Convert back to BGR
            enhanced = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Image enhancement error: {e}")
            return image
    
    def _auto_crop(self, image: np.ndarray) -> np.ndarray:
        """Auto-crop white borders from image"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Threshold the image
            _, thresh = cv2.threshold(gray, self.settings['threshold'], 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return image
            
            # Find largest contour
            largest = max(contours, key=cv2.contourArea)
            
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(largest)
            
            # Add small padding
            padding = 10
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2 * padding)
            h = min(image.shape[0] - y, h + 2 * padding)
            
            # Crop
            cropped = image[y:y+h, x:x+w]
            
            return cropped
            
        except Exception as e:
            logger.error(f"Auto crop error: {e}")
            return image
    
    # ============================================================
    # PREVIEW
    # ============================================================
    
    def start_preview(self, callback, show_preview: bool = True) -> bool:
        """Start camera preview with callback"""
        if not self.is_camera_open():
            if not self.open_camera():
                return False
        
        self.is_previewing = True
        self.is_scanning = True
        self.capture_callback = callback
        
        if show_preview:
            # Start preview thread
            self.preview_thread = threading.Thread(target=self._preview_loop, daemon=True)
            self.preview_thread.start()
        
        logger.info("Camera preview started")
        return True
    
    def _preview_loop(self):
        """Camera preview loop with processing"""
        while self.is_previewing and self.is_camera_open():
            try:
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    # Process frame if callback expects processed
                    if self.capture_callback:
                        self.capture_callback(frame)
                time.sleep(0.03)  # ~30 FPS
            except Exception as e:
                logger.error(f"Preview loop error: {e}")
                break
    
    def stop_preview(self):
        """Stop camera preview"""
        self.is_previewing = False
        self.is_scanning = False
        
        # Wait for thread to finish
        if self.preview_thread and self.preview_thread.is_alive():
            self.preview_thread.join(timeout=1)
        
        self.close_camera()
        logger.info("Camera preview stopped")
    
    # ============================================================
    # BATCH SCANNING
    # ============================================================
    
    def batch_scan(
        self,
        count: int = 5,
        process: bool = True,
        output_format: str = 'jpg',
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Scan multiple documents in batch
        
        Args:
            count: Number of scans
            process: Whether to process images
            output_format: Output format
            progress_callback: Progress callback
        
        Returns:
            List of scan results
        """
        results = []
        
        for i in range(count):
            if not self.is_camera_open():
                break
            
            success, file_path, image = self.scan_document(process, None, output_format)
            
            results.append({
                'index': i + 1,
                'success': success,
                'file_path': file_path,
                'image': image
            })
            
            if progress_callback:
                progress_callback(i + 1, count)
            
            # Small delay between scans
            time.sleep(0.5)
        
        return results
    
    # ============================================================
    # SETTINGS
    # ============================================================
    
    def update_settings(self, **kwargs):
        """Update scanner settings"""
        for key, value in kwargs.items():
            if key in self.settings:
                self.settings[key] = value
                logger.info(f"Setting updated: {key} = {value}")
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        return self.settings.copy()
    
    def reset_settings(self):
        """Reset settings to defaults"""
        self.settings = {
            'auto_crop': True,
            'perspective_correction': True,
            'enhance_contrast': True,
            'denoise': True,
            'output_quality': 95,
            'threshold': 200,
            'min_area': 5000
        }
        logger.info("Settings reset to defaults")
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def get_available_cameras(self) -> List[int]:
        """Get list of available camera IDs"""
        available = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        return available
    
    def get_scanned_files(self) -> List[Dict[str, Any]]:
        """Get list of scanned files"""
        files = []
        for file_path in self.scan_folder.glob('*'):
            if file_path.is_file():
                files.append({
                    'name': file_path.name,
                    'path': str(file_path),
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                    'extension': file_path.suffix[1:].lower()
                })
        return sorted(files, key=lambda x: x['modified'], reverse=True)
    
    def delete_scanned_file(self, filename: str) -> bool:
        """Delete a scanned file"""
        try:
            file_path = self.scan_folder / filename
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted scanned file: {filename}")
                return True
            return False
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return False
    
    def clear_scanned_files(self) -> bool:
        """Clear all scanned files"""
        try:
            for file_path in self.scan_folder.glob('*'):
                if file_path.is_file():
                    file_path.unlink()
            logger.info("Cleared all scanned files")
            return True
        except Exception as e:
            logger.error(f"Clear error: {e}")
            return False
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close_camera()