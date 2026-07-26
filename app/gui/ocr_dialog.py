# app/gui/ocr_dialog.py
"""
OCR Dialog - Extract text from images and documents
"""

import os
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QProgressBar, QFileDialog,
    QMessageBox, QGroupBox, QComboBox, QCheckBox,
    QTabWidget, QWidget, QApplication, QScrollArea
)
from PySide6.QtGui import QFont, QIcon, QPixmap

from app.utils.logger import get_logger

logger = get_logger(__name__)


class OCRWorker(QThread):
    """Worker thread for OCR processing"""
    
    progress = Signal(int, str)
    finished = Signal(bool, str, dict)
    
    def __init__(self, file_path: str, language: str = 'en', preprocess: bool = True):
        super().__init__()
        self.file_path = file_path
        self.language = language
        self.preprocess = preprocess
        
    def run(self):
        try:
            self.progress.emit(10, "Loading OCR engine...")
            
            # Import OCR engine
            try:
                from app.ocr.ocr_engine import ocr_engine
                if not ocr_engine.is_available():
                    self.finished.emit(False, "OCR engine not available. Please install: pip install easyocr", {})
                    return
            except ImportError as e:
                self.finished.emit(False, f"OCR module not available: {str(e)}", {})
                return
            
            self.progress.emit(20, "Loading image...")
            
            # Check if file exists
            if not Path(self.file_path).exists():
                self.finished.emit(False, f"File not found: {self.file_path}", {})
                return
            
            # Determine file type
            ext = Path(self.file_path).suffix[1:].lower()
            
            self.progress.emit(40, "Preprocessing image...")
            
            # Extract text
            if ext == 'pdf':
                success, text, metadata = ocr_engine.extract_text_from_pdf(self.file_path)
            else:
                success, text, metadata = ocr_engine.extract_text(
                    self.file_path, 
                    self.language, 
                    self.preprocess
                )
            
            self.progress.emit(90, "Finalizing...")
            
            if success and text.strip():
                self.finished.emit(True, text, metadata)
            else:
                self.finished.emit(False, text if text else "No text detected in the image", {})
                
        except Exception as e:
            logger.error(f"OCR worker error: {e}")
            self.finished.emit(False, str(e), {})


class OCRDialog(QDialog):
    """OCR Dialog for text extraction"""
    
    def __init__(self, parent=None, file_path: str = None):
        super().__init__(parent)
        
        self.parent = parent
        self.file_path = file_path
        self.worker = None
        self.camera_scanner = None
        self.preview_timer = None
        
        self.setWindowTitle("📄 OCR - Extract Text")
        self.setMinimumSize(800, 650)
        self.setModal(True)
        
        self.setup_ui()
        
        # If file path provided, start OCR automatically
        if file_path and Path(file_path).exists():
            self.start_ocr()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("📄 Optical Character Recognition")
        header_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2D3436;
        """)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E8E8E8;
                border-radius: 8px;
                padding: 10px;
                background: white;
            }
            QTabBar::tab {
                padding: 8px 16px;
                border: none;
                border-radius: 6px 6px 0 0;
                color: #2D3436;
            }
            QTabBar::tab:selected {
                background: #6C63FF;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #E8E8E8;
            }
        """)
        
        # Tab 1: File Upload
        file_tab = self._create_file_tab()
        tabs.addTab(file_tab, "📁 File")
        
        # Tab 2: Camera Scan
        camera_tab = self._create_camera_tab()
        tabs.addTab(camera_tab, "📷 Camera")
        
        layout.addWidget(tabs)
        
        # Progress
        progress_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background: #E8E8E8;
                height: 8px;
            }
            QProgressBar::chunk {
                background: #6C63FF;
                border-radius: 4px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        progress_layout.addWidget(self.status_label)
        
        layout.addLayout(progress_layout)
        
        # Results with scroll
        results_group = QGroupBox("Extracted Text")
        results_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #E8E8E8;
                border-radius: 8px;
                padding-top: 12px;
                color: #2D3436;
                font-weight: 600;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
                color: #2D3436;
            }
        """)
        results_layout = QVBoxLayout(results_group)
        
        # Text display with scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #F5F7FA;
                border: none;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #D0D0D0;
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #B0B0B0;
            }
        """)
        
        text_container = QWidget()
        text_container_layout = QVBoxLayout(text_container)
        text_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setPlaceholderText("Extracted text will appear here...")
        self.text_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E8E8E8;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                color: #2D3436;
                background: #FFFFFF;
                min-height: 150px;
            }
        """)
        self.text_display.setMinimumHeight(150)
        text_container_layout.addWidget(self.text_display)
        
        scroll_area.setWidget(text_container)
        results_layout.addWidget(scroll_area, 1)
        
        # Copy and Save buttons
        result_btn_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 16px;
                border: 1px solid #E8E8E8;
                border-radius: 6px;
                background: white;
                color: #2D3436;
            }
            QPushButton:hover {
                background: #F5F7FA;
            }
        """)
        self.copy_btn.clicked.connect(self.copy_text)
        result_btn_layout.addWidget(self.copy_btn)
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 16px;
                border: none;
                border-radius: 6px;
                background: #6C63FF;
                color: white;
            }
            QPushButton:hover {
                background: #5A52D5;
            }
        """)
        self.save_btn.clicked.connect(self.save_text)
        result_btn_layout.addWidget(self.save_btn)
        
        result_btn_layout.addStretch()
        
        self.word_count_label = QLabel("Words: 0")
        self.word_count_label.setStyleSheet("color: #A0A0A0; font-size: 11px;")
        result_btn_layout.addWidget(self.word_count_label)
        
        results_layout.addLayout(result_btn_layout)
        
        layout.addWidget(results_group, 1)
    
    def _create_file_tab(self):
        """Create file upload tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # File selection
        file_group = QGroupBox("Select File")
        file_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #E8E8E8;
                border-radius: 6px;
                padding-top: 10px;
                color: #2D3436;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
            }
        """)
        file_layout = QHBoxLayout(file_group)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #636E72;")
        file_layout.addWidget(self.file_label, 1)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 16px;
                border: none;
                border-radius: 6px;
                background: #6C63FF;
                color: white;
            }
            QPushButton:hover {
                background: #5A52D5;
            }
        """)
        self.browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_btn)
        
        layout.addWidget(file_group)
        
        # OCR Options
        options_group = QGroupBox("OCR Options")
        options_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #E8E8E8;
                border-radius: 6px;
                padding-top: 10px;
                color: #2D3436;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 6px;
            }
        """)
        options_layout = QVBoxLayout(options_group)
        
        # Language
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['en', 'ur', 'ar', 'fr', 'de', 'es', 'zh'])
        self.lang_combo.setCurrentText('en')
        self.lang_combo.setToolTip("Language for OCR")
        self.lang_combo.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #E8E8E8;
                border-radius: 4px;
                color: #2D3436;
                background: white;
            }
        """)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        options_layout.addLayout(lang_layout)
        
        # Preprocess
        self.preprocess_check = QCheckBox("Preprocess image (recommended)")
        self.preprocess_check.setChecked(True)
        self.preprocess_check.setToolTip("Enhance image for better text recognition")
        self.preprocess_check.setStyleSheet("color: #2D3436;")
        options_layout.addWidget(self.preprocess_check)
        
        layout.addWidget(options_group)
        
        # Extract button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.extract_btn = QPushButton("🔍 Extract Text")
        self.extract_btn.setStyleSheet("""
            QPushButton {
                background: #6C63FF;
                color: white;
                padding: 10px 30px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #5A52D5;
            }
            QPushButton:disabled {
                background: #A0A0A0;
            }
        """)
        self.extract_btn.clicked.connect(self.start_ocr)
        btn_layout.addWidget(self.extract_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        return tab
    
    def _create_camera_tab(self):
        """Create camera scan tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        
        # Camera preview
        self.camera_label = QLabel("Camera preview will appear here")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("""
            QLabel {
                border: 2px solid #E8E8E8;
                border-radius: 8px;
                background: #F5F6FA;
                min-height: 300px;
                color: #A0A0A0;
                font-size: 14px;
            }
        """)
        self.camera_label.setMinimumHeight(300)
        layout.addWidget(self.camera_label)
        
        # Camera controls
        camera_btn_layout = QHBoxLayout()
        camera_btn_layout.setSpacing(10)
        
        self.start_camera_btn = QPushButton("📷 Start Camera")
        self.start_camera_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                background: #00C9A7;
                color: white;
            }
            QPushButton:hover {
                background: #00B897;
            }
            QPushButton:disabled {
                background: #A0A0A0;
            }
        """)
        self.start_camera_btn.clicked.connect(self.start_camera_preview)
        camera_btn_layout.addWidget(self.start_camera_btn)
        
        self.capture_btn = QPushButton("📸 Capture & OCR")
        self.capture_btn.setEnabled(False)
        self.capture_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                background: #6C63FF;
                color: white;
            }
            QPushButton:hover {
                background: #5A52D5;
            }
            QPushButton:disabled {
                background: #A0A0A0;
            }
        """)
        self.capture_btn.clicked.connect(self.capture_and_ocr)
        camera_btn_layout.addWidget(self.capture_btn)
        
        self.stop_camera_btn = QPushButton("⏹ Stop Camera")
        self.stop_camera_btn.setEnabled(False)
        self.stop_camera_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                background: #FF6B6B;
                color: white;
            }
            QPushButton:hover {
                background: #E55555;
            }
            QPushButton:disabled {
                background: #A0A0A0;
            }
        """)
        self.stop_camera_btn.clicked.connect(self.stop_camera_preview)
        camera_btn_layout.addWidget(self.stop_camera_btn)
        
        camera_btn_layout.addStretch()
        layout.addLayout(camera_btn_layout)
        
        layout.addStretch()
        return tab
    
    def browse_file(self):
        """Browse for image or PDF file"""
        file_filter = "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.webp);;PDF Files (*.pdf);;All Files (*.*)"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File for OCR",
            "",
            file_filter
        )
        
        if file_path:
            self.file_path = file_path
            self.file_label.setText(Path(file_path).name)
            self.file_label.setStyleSheet("color: #2D3436; font-weight: 500;")
            self.text_display.clear()
            self.word_count_label.setText("Words: 0")
            self.progress_bar.setValue(0)
            self.status_label.setText("File loaded. Click 'Extract Text' to start.")
    
    def start_ocr(self):
        """Start OCR process"""
        if not self.file_path or not Path(self.file_path).exists():
            QMessageBox.warning(self, "No File", "Please select a file first!")
            return
        
        # Check if OCR is available
        try:
            from app.ocr.ocr_engine import ocr_engine
            if not ocr_engine.is_available():
                QMessageBox.warning(self, "OCR Not Available", 
                    "OCR is not available.\n\nPlease install:\npip install easyocr")
                return
        except ImportError as e:
            QMessageBox.warning(self, "OCR Not Available", 
                f"OCR module not available: {str(e)}\n\nPlease install:\npip install easyocr")
            return
        
        # Disable button during processing
        self.extract_btn.setEnabled(False)
        self.extract_btn.setText("⏳ Processing...")
        self.progress_bar.setValue(0)
        self.status_label.setText("Processing...")
        
        # Create worker
        self.worker = OCRWorker(
            self.file_path,
            self.lang_combo.currentText(),
            self.preprocess_check.isChecked()
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_ocr_finished)
        self.worker.start()
    
    def update_progress(self, value, message):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    # In ocr_dialog.py, update the on_ocr_finished method:

    def on_ocr_finished(self, success, text, metadata):
        """Handle OCR completion - Show full text"""
        self.extract_btn.setEnabled(True)
        self.extract_btn.setText("🔍 Extract Text")
        self.progress_bar.setValue(100 if success else 0)
        
        if success and text.strip():
            # Show ALL extracted text
            self.text_display.setText(text)
            word_count = len(text.split())
            char_count = len(text)
            self.word_count_label.setText(f"Words: {word_count} | Characters: {char_count}")
            self.status_label.setText(f"✅ OCR complete! {word_count} words extracted")
            
            # Show more detailed success message
            engine = metadata.get('engine', 'Unknown')
            confidence = metadata.get('confidence', 0)
            QMessageBox.information(
                self,
                "OCR Complete",
                f"✅ Successfully extracted {word_count} words!\n\n"
                f"📊 Engine: {engine}\n"
                f"📝 Characters: {char_count}\n"
                f"🎯 Confidence: {confidence:.1%}" if confidence else ""
            )
        else:
            self.text_display.setText(f"❌ OCR failed:\n\n{text}")
            self.status_label.setText("❌ OCR failed")
            QMessageBox.warning(self, "OCR Failed", f"Could not extract text:\n\n{text}")
    
    def start_camera_preview(self):
        """Start camera preview"""
        try:
            import cv2
        except ImportError:
            QMessageBox.warning(self, "Camera Error", "OpenCV is not installed!\n\npip install opencv-python")
            return
        
        try:
            from app.ocr.camera import CameraScanner
            self.camera_scanner = CameraScanner()
        except ImportError:
            QMessageBox.warning(self, "Camera Error", "Camera module not available")
            return
        
        if not self.camera_scanner.is_camera_available():
            QMessageBox.warning(self, "Camera Error", "No camera detected!")
            return
        
        if self.camera_scanner.open_camera():
            self.start_camera_btn.setEnabled(False)
            self.capture_btn.setEnabled(True)
            self.stop_camera_btn.setEnabled(True)
            self.status_label.setText("📷 Camera started. Position document and click Capture.")
            
            # Start preview timer
            self.preview_timer = QTimer()
            self.preview_timer.timeout.connect(self.update_camera_preview)
            self.preview_timer.start(50)
        else:
            QMessageBox.warning(self, "Camera Error", "Could not open camera!")
    
    def update_camera_preview(self):
        """Update camera preview frame"""
        if self.camera_scanner:
            frame = self.camera_scanner.get_preview_frame()
            if frame is not None:
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                from PySide6.QtGui import QImage
                qimage = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)
                
                scaled_pixmap = pixmap.scaled(
                    self.camera_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.camera_label.setPixmap(scaled_pixmap)
    
    def capture_and_ocr(self):
        """Capture document and run OCR"""
        if self.camera_scanner:
            success, filename, processed = self.camera_scanner.scan_document()
            
            if success:
                self.status_label.setText(f"📷 Document captured: {filename}")
                self.file_path = filename
                self.file_label.setText(f"Scanned: {Path(filename).name}")
                self.file_label.setStyleSheet("color: #2D3436; font-weight: 500;")
                
                # Auto-run OCR on captured image
                self.start_ocr()
            else:
                QMessageBox.warning(self, "Capture Error", "Could not capture document. Try again.")
    
    def stop_camera_preview(self):
        """Stop camera preview"""
        if hasattr(self, 'preview_timer') and self.preview_timer:
            self.preview_timer.stop()
            self.preview_timer = None
        
        if self.camera_scanner:
            self.camera_scanner.close_camera()
            self.camera_scanner = None
        
        self.start_camera_btn.setEnabled(True)
        self.capture_btn.setEnabled(False)
        self.stop_camera_btn.setEnabled(False)
        self.camera_label.setText("Camera stopped")
        self.camera_label.setPixmap(QPixmap())
        self.status_label.setText("Camera stopped")
    
    # ===== TEXT OPERATIONS =====
    
    def copy_text(self):
        """Copy extracted text to clipboard"""
        text = self.text_display.toPlainText()
        if text and text.strip():
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.status_label.setText("✅ Text copied to clipboard!")
            QMessageBox.information(self, "Copied", "✅ Text copied to clipboard!")
        else:
            self.status_label.setText("⚠️ No text to copy")
            QMessageBox.warning(self, "No Text", "No text to copy!")
    
    def save_text(self):
        """Save extracted text to file"""
        text = self.text_display.toPlainText()
        if not text or not text.strip():
            QMessageBox.warning(self, "No Text", "No text to save!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Extracted Text",
            f"extracted_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.status_label.setText(f"✅ Text saved to: {Path(file_path).name}")
                QMessageBox.information(self, "Saved", f"✅ Text saved to:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Save Error", f"Could not save file:\n{str(e)}")
    
    def closeEvent(self, event):
        """Handle close event"""
        self.stop_camera_preview()
        event.accept()