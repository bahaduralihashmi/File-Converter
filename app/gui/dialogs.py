"""
Dialogs - Complete
Custom dialog windows for the application
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QMessageBox,
    QLineEdit, QComboBox, QCheckBox, QFileDialog
)
from PySide6.QtGui import QIcon, QFont

from config import Config
from app.utils.helpers import format_file_size


class Dialogs:
    """Dialog factory class"""
    
    @staticmethod
    def show_info(parent, title: str, message: str):
        """Show info dialog"""
        QMessageBox.information(parent, title, message)
        
    @staticmethod
    def show_warning(parent, title: str, message: str):
        """Show warning dialog"""
        QMessageBox.warning(parent, title, message)
        
    @staticmethod
    def show_error(parent, title: str, message: str):
        """Show error dialog"""
        QMessageBox.critical(parent, title, message)
        
    @staticmethod
    def show_question(parent, title: str, message: str) -> bool:
        """Show question dialog - FIXED for PySide6"""
        reply = QMessageBox.question(
            parent,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
        
    @staticmethod
    def show_about(parent):
        """Show about dialog"""
        QMessageBox.about(
            parent,
            f"About {Config.APP_NAME}",
            f"""
            <h2>{Config.APP_NAME}</h2>
            <p><b>Version:</b> {Config.APP_VERSION}</p>
            <p><b>Author:</b> {Config.APP_AUTHOR}</p>
            <p><b>Year:</b> {Config.APP_YEAR}</p>
            <br>
            <p>Professional file conversion tool with AI assistance.</p>
            <p>Supports 1000+ file formats.</p>
            <br>
            <p><a href="{Config.APP_WEBSITE}">{Config.APP_WEBSITE}</a></p>
            """
        )


class ProgressDialog(QDialog):
    """Progress dialog for conversions"""
    
    def __init__(self, parent=None, title="Converting..."):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 150)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Message
        self.message_label = QLabel("Preparing conversion...")
        self.message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        layout.addWidget(self.cancel_btn, alignment=Qt.AlignCenter)
        
        self.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #2D3436;
            }
            QProgressBar {
                border: none;
                border-radius: 4px;
                background: #E8E8E8;
                height: 20px;
            }
            QProgressBar::chunk {
                background: #6C63FF;
                border-radius: 4px;
            }
            QPushButton {
                padding: 8px 24px;
                border: none;
                border-radius: 6px;
                background: #FF6B6B;
                color: white;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #E55555;
            }
        """)
        
    def update_progress(self, value: int, message: str = None):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        if message:
            self.message_label.setText(message)


class SettingsDialog(QDialog):
    """Settings dialog"""
    
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Theme
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)
        
        # Output folder
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Output Folder:"))
        self.folder_input = QLineEdit()
        folder_layout.addWidget(self.folder_input)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(browse_btn)
        layout.addLayout(folder_layout)
        
        # Default format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Default Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(Config.get_output_formats())
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        layout.addLayout(format_layout)
        
        # Options
        self.auto_convert_cb = QCheckBox("Enable auto-conversion")
        layout.addWidget(self.auto_convert_cb)
        
        self.keep_original_cb = QCheckBox("Keep original files")
        layout.addWidget(self.keep_original_cb)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 10px;
            }
            QLabel {
                font-size: 13px;
                color: #2D3436;
            }
            QLineEdit, QComboBox {
                padding: 6px 12px;
                border: 1px solid #E8E8E8;
                border-radius: 6px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #6C63FF;
            }
            QPushButton {
                padding: 8px 24px;
                border: none;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:first-child {
                background: #6C63FF;
                color: white;
            }
            QPushButton:first-child:hover {
                background: #5A52D5;
            }
            QPushButton:last-child {
                background: #E8E8E8;
                color: #2D3436;
            }
            QPushButton:last-child:hover {
                background: #D8D8D8;
            }
            QCheckBox {
                font-size: 13px;
                color: #2D3436;
            }
        """)
        
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            ""
        )
        if folder:
            self.folder_input.setText(folder)
            
    def load_settings(self):
        if self.settings:
            self.theme_combo.setCurrentText(self.settings.get("theme", "Light").title())
            self.folder_input.setText(self.settings.get("output_folder", ""))
            self.format_combo.setCurrentText(self.settings.get("output_format", "pdf"))
            self.auto_convert_cb.setChecked(self.settings.get("auto_convert", False))
            self.keep_original_cb.setChecked(self.settings.get("keep_original", True))
            
    def save_settings(self):
        if self.settings:
            self.settings.set("theme", self.theme_combo.currentText().lower())
            self.settings.set("output_folder", self.folder_input.text())
            self.settings.set("output_format", self.format_combo.currentText())
            self.settings.set("auto_convert", self.auto_convert_cb.isChecked())
            self.settings.set("keep_original", self.keep_original_cb.isChecked())
            self.settings.save()
            
        self.accept()