# app/ocr/camera.py
"""
Camera Scanner - Optimized for speed
"""

import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import threading
import time
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CameraScanner:
    """Camera scanner with optimized settings"""
    
    def __init__(self):
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.lock = threading.Lock()
        self.scan_folder = Path("scanned_documents")
        self.scan_folder.mkdir(exist_ok=True)
        self.camera_index = 0
        self.preview_active = False
        
    def is_camera_available(self) -> bool:
        try:
            cap = cv2.VideoCapture(self.camera_index)
            if cap.isOpened():
                cap.release()
                return True
            return False
        except:
            return False
    
    def open_camera(self) -> bool:
        try:
            with self.lock:
                if self.cap is not None:
                    self.close_camera()
                
                self.cap = cv2.VideoCapture(self.camera_index)
                if not self.cap.isOpened():
                    logger.error("Failed to open camera")
                    return False
                
                # Optimized settings for speed
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                
                self.is_running = True
                self.preview_active = True
                logger.info("Camera opened")
                return True
                
        except Exception as e:
            logger.error(f"Error opening camera: {e}")
            return False
    
    def get_preview_frame(self):
        if not self.is_running or self.cap is None or not self.preview_active:
            return None
        
        try:
            with self.lock:
                if self.cap is None or not self.cap.isOpened():
                    return None
                
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.current_frame = frame.copy()
                    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return None
                
        except Exception as e:
            logger.error(f"Error getting frame: {e}")
            return None
    
    def scan_document(self) -> tuple:
        try:
            with self.lock:
                if self.current_frame is None:
                    return False, None, None
                
                frame = self.current_frame.copy()
                
                if frame is None:
                    return False, None, None
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"scanned_document_{timestamp}.jpg"
                file_path = self.scan_folder / filename
                
                cv2.imwrite(str(file_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                
                # Quick enhancement
                processed = self._quick_enhance(frame)
                
                logger.info(f"Document scanned: {filename}")
                return True, str(file_path), processed
                
        except Exception as e:
            logger.error(f"Error capturing document: {e}")
            return False, None, None
    
    def _quick_enhance(self, image):
        """Quick enhancement for OCR"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Simple contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            return enhanced
        except:
            return image
    
    def close_camera(self):
        try:
            with self.lock:
                self.preview_active = False
                if self.cap is not None:
                    self.cap.release()
                    self.cap = None
                self.is_running = False
                self.current_frame = None
                logger.info("Camera closed")
        except Exception as e:
            logger.error(f"Error closing camera: {e}")
    
    def stop_preview(self):
        self.close_camera()
    
    def __del__(self):
        self.close_camera()