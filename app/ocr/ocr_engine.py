# app/ocr/ocr_engine.py
"""
OCR Engine - High Accuracy Text Extraction
Fixed for EasyOCR paragraph mode and Tesseract fallback
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import logging
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)

# Try to import OCR libraries
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class OCREngine:
    """OCR Engine with multiple backends for best accuracy"""
    
    def __init__(self):
        self.reader = None
        self.initialized = False
        self.backend = None
        
        # Initialize OCR
        self._init_ocr()
        
    def _init_ocr(self):
        """Initialize OCR engine with best available backend"""
        
        # Try EasyOCR first (best accuracy)
        if EASYOCR_AVAILABLE:
            try:
                logger.info("Loading EasyOCR...")
                self.reader = easyocr.Reader(
                    ['en'], 
                    gpu=False, 
                    verbose=False,
                    model_storage_directory='models/easyocr',
                    download_enabled=True
                )
                self.initialized = True
                self.backend = 'EasyOCR'
                logger.info("✅ EasyOCR initialized successfully")
                return
            except Exception as e:
                logger.warning(f"EasyOCR initialization failed: {e}")
        
        # Try Tesseract as fallback
        if TESSERACT_AVAILABLE:
            try:
                version = pytesseract.get_tesseract_version()
                self.initialized = True
                self.backend = 'Tesseract'
                logger.info(f"✅ Tesseract initialized (v{version})")
                return
            except Exception as e:
                logger.warning(f"Tesseract not available: {e}")
        
        if not self.initialized:
            logger.warning("⚠️ No OCR engine available. Install: pip install easyocr")
    
    def is_available(self) -> bool:
        """Check if OCR is available"""
        return self.initialized
    
    def get_backend(self) -> str:
        """Get active OCR backend"""
        return self.backend or "None"
    
    # ============================================================
    # IMAGE PREPROCESSING
    # ============================================================
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Resize if too small
            h, w = gray.shape
            if min(h, w) < 400:
                scale = 800 / min(h, w)
                new_w = int(w * scale)
                new_h = int(h * scale)
                gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # Sharpen
            kernel = np.array([[-1,-1,-1], [-1, 9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel)
            
            # Otsu threshold
            _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Clean noise
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Preprocessing error: {e}")
            img = cv2.imread(image_path)
            if img is not None:
                return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return None
    
    # ============================================================
    # TEXT EXTRACTION - MAIN
    # ============================================================
    
    def extract_text(self, image_path: str, language: str = 'en', 
                     preprocess: bool = True) -> Tuple[bool, str, Dict]:
        """Extract text from image"""
        try:
            if not Path(image_path).exists():
                return False, f"File not found: {image_path}", {}
            
            if not self.initialized:
                return False, "OCR engine not initialized. Install: pip install easyocr", {}
            
            ext = Path(image_path).suffix[1:].lower()
            if ext == 'pdf':
                return self.extract_text_from_pdf(image_path)
            
            # Preprocess
            processed_img = None
            if preprocess:
                try:
                    processed_img = self.preprocess_image(image_path)
                except:
                    pass
            
            if processed_img is None:
                processed_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            
            if processed_img is None:
                return False, "Could not read image", {}
            
            # ===== TRY EASYOCR =====
            if self.backend == 'EasyOCR' and self.reader:
                try:
                    result = self._extract_with_easyocr(processed_img, language)
                    if result[0] and result[1].strip():
                        return result
                except Exception as e:
                    logger.warning(f"EasyOCR failed: {e}")
            
            # ===== TRY TESSERACT =====
            if TESSERACT_AVAILABLE:
                try:
                    result = self._extract_with_tesseract(processed_img)
                    if result[0] and result[1].strip():
                        return result
                except Exception as e:
                    logger.warning(f"Tesseract failed: {e}")
            
            # ===== TRY EASYOCR WITHOUT PREPROCESSING =====
            if self.backend == 'EasyOCR' and self.reader:
                try:
                    # Use original image
                    original = cv2.imread(image_path)
                    if original is not None:
                        result = self._extract_with_easyocr(original, language)
                        if result[0] and result[1].strip():
                            return result
                except Exception as e:
                    logger.warning(f"EasyOCR on original failed: {e}")
            
            return False, "No text detected", {}
            
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return False, str(e), {}
    
    # ============================================================
    # EASYOCR EXTRACTION - FIXED
    # ============================================================
    
    def _extract_with_easyocr(self, image: np.ndarray, language: str = 'en') -> Tuple[bool, str, Dict]:
        """Extract text using EasyOCR - FIXED for both modes"""
        try:
            if not self.reader:
                return False, "EasyOCR reader not initialized", {}
            
            logger.info("Using EasyOCR for text extraction")
            
            # Convert grayscale to color if needed
            if len(image.shape) == 2:
                img = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            else:
                img = image
            
            # FIX: Use paragraph=False to get consistent output format
            # Each result: (bbox, text, confidence)
            results = self.reader.readtext(img, paragraph=False)
            
            if not results:
                return False, "No text detected", {}
            
            # Extract text and confidence
            text_parts = []
            confidences = []
            
            for result in results:
                # FIX: Handle different output formats
                if len(result) == 3:
                    bbox, text, confidence = result
                elif len(result) == 2:
                    # Some versions return (bbox, text) without confidence
                    bbox, text = result
                    confidence = 0.5  # Default confidence
                else:
                    continue
                
                if confidence > 0.2 and len(text.strip()) > 0:
                    text_parts.append(text)
                    confidences.append(confidence)
            
            if not text_parts:
                return False, "No text with sufficient confidence", {}
            
            full_text = '\n'.join(text_parts)
            full_text = self._clean_text(full_text)
            
            metadata = {
                'confidence': sum(confidences) / len(confidences) if confidences else 0,
                'word_count': len(full_text.split()),
                'char_count': len(full_text),
                'engine': 'EasyOCR',
                'language': language
            }
            
            logger.info(f"EasyOCR extracted {metadata['word_count']} words")
            return True, full_text, metadata
            
        except Exception as e:
            logger.error(f"EasyOCR extraction error: {e}")
            return False, str(e), {}
    
    # ============================================================
    # TESSERACT EXTRACTION
    # ============================================================
    
    def _extract_with_tesseract(self, image: np.ndarray) -> Tuple[bool, str, Dict]:
        """Extract text using Tesseract"""
        try:
            if not TESSERACT_AVAILABLE:
                return False, "Tesseract not available. Install: pip install pytesseract", {}
            
            logger.info("Using Tesseract for text extraction")
            
            # Convert to PIL
            if isinstance(image, np.ndarray):
                pil_img = Image.fromarray(image)
            else:
                pil_img = image
            
            # Try different PSM modes
            configs = [
                r'--oem 3 --psm 6',  # Uniform block of text
                r'--oem 3 --psm 4',  # Single column
                r'--oem 3 --psm 3',  # Automatic
            ]
            
            for config in configs:
                try:
                    text = pytesseract.image_to_string(pil_img, config=config)
                    if text and text.strip():
                        text = self._clean_text(text)
                        if len(text.split()) > 3:  # At least a few words
                            metadata = {
                                'word_count': len(text.split()),
                                'char_count': len(text),
                                'engine': 'Tesseract'
                            }
                            logger.info(f"Tesseract extracted {metadata['word_count']} words")
                            return True, text, metadata
                except:
                    continue
            
            return False, "No text detected by Tesseract", {}
            
        except Exception as e:
            logger.error(f"Tesseract extraction error: {e}")
            return False, str(e), {}
    
    # ============================================================
    # PDF EXTRACTION
    # ============================================================
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[bool, str, Dict]:
        """Extract text from PDF"""
        try:
            if not Path(pdf_path).exists():
                return False, f"File not found: {pdf_path}", {}
            
            all_text = []
            
            # Try PyMuPDF
            if PYMUPDF_AVAILABLE:
                try:
                    doc = fitz.open(pdf_path)
                    for page_num in range(len(doc)):
                        page = doc[page_num]
                        text = page.get_text()
                        if text and text.strip():
                            all_text.append(text.strip())
                    doc.close()
                    
                    if all_text:
                        full_text = '\n\n'.join(all_text)
                        full_text = self._clean_text(full_text)
                        metadata = {
                            'pages': len(all_text),
                            'word_count': len(full_text.split()),
                            'engine': 'PyMuPDF'
                        }
                        return True, full_text, metadata
                except Exception as e:
                    logger.warning(f"PyMuPDF failed: {e}")
            
            # Fallback: PDF to images
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(pdf_path, dpi=150)
                all_text = []
                
                for img in images:
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        tmp_path = tmp.name
                        img.save(tmp_path, 'PNG')
                    
                    success, text, _ = self.extract_text(tmp_path, preprocess=True)
                    
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
                    
                    if success and text.strip():
                        all_text.append(text.strip())
                
                if all_text:
                    full_text = '\n\n'.join(all_text)
                    full_text = self._clean_text(full_text)
                    metadata = {
                        'pages': len(images),
                        'word_count': len(full_text.split()),
                        'engine': 'PDF2Image + OCR'
                    }
                    return True, full_text, metadata
                    
            except ImportError:
                pass
            except Exception as e:
                logger.warning(f"PDF2Image failed: {e}")
            
            return False, "Could not extract text from PDF", {}
            
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return False, str(e), {}
    
    # ============================================================
    # UTILITY
    # ============================================================
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        
        import re
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?@#$%^&*()_+\-=\[\]{};:\'",<>/~`\n]', '', text)
        return text.strip()
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get OCR engine information"""
        return {
            'available': self.initialized,
            'backend': self.backend,
            'easyocr_available': EASYOCR_AVAILABLE,
            'tesseract_available': TESSERACT_AVAILABLE,
            'pymupdf_available': PYMUPDF_AVAILABLE
        }


# Singleton instance
ocr_engine = OCREngine()