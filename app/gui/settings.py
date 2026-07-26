"""
Settings Widget - No Theme Options
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGroupBox, QComboBox, QLineEdit,
    QCheckBox, QSpinBox, QFileDialog, QTabWidget,
    QScrollArea, QMessageBox, QFormLayout
)

from config import Config
from app.core.settings import SettingsManager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SettingsWidget(QWidget):
    """Settings Widget - No Theme Options"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.settings = SettingsManager.load()
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("⚙️ Settings")
        header.setStyleSheet("""
            font-size: 22px;
            font-weight: 700;
            color: #2D3436;
            font-family: 'Segoe UI', sans-serif;
        """)
        layout.addWidget(header)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)
        
        # ===== GENERAL SETTINGS =====
        general_group = self._create_general_group()
        content_layout.addWidget(general_group)
        
        # ===== CONVERSION SETTINGS =====
        conversion_group = self._create_conversion_group()
        content_layout.addWidget(conversion_group)
        
        # ===== THEME SETTINGS =====
        theme_group = self._create_theme_group()
        content_layout.addWidget(theme_group)
        
        # ===== VOICE SETTINGS =====
        voice_group = self._create_voice_group()
        content_layout.addWidget(voice_group)
        
        # ===== SAVE BUTTON =====
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background: #2E5A8A;
                color: white;
                padding: 12px 32px;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                font-size: 14px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: #1E3A5F;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        save_layout.addWidget(save_btn)
        save_layout.addStretch()
        
        content_layout.addLayout(save_layout)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            ""
        )
        if folder:
            self.folder_input.setText(folder)
            
    def load_settings(self):
        self.folder_input.setText(self.settings.get("output_folder", ""))
        self.format_combo.setCurrentText(self.settings.get("output_format", "pdf"))
        
        quality = self.settings.get("quality", "high")
        quality_map = {"low": 0, "medium": 1, "high": 2}
        self.quality_combo.setCurrentIndex(quality_map.get(quality, 2))
        
        self.keep_original.setChecked(self.settings.get("keep_original", True))
        self.auto_convert.setChecked(self.settings.get("auto_convert", False))
        self.voice_enabled.setChecked(self.settings.get("voice_enabled", True))

        
    def save_settings(self):
        try:
            # General
            output_folder = self.folder_input.text()
            if output_folder:
                # Ensure folder exists
                Path(output_folder).mkdir(parents=True, exist_ok=True)
                self.settings.set("output_folder", output_folder)
            
            self.settings.set("output_format", self.format_combo.currentText())
            
            # Conversion
            quality_map = {0: "low", 1: "medium", 2: "high"}
            self.settings.set("quality", quality_map.get(self.quality_combo.currentIndex(), "high"))
            self.settings.set("keep_original", self.keep_original.isChecked())
            self.settings.set("auto_convert", self.auto_convert.isChecked())
            
            # Voice
            self.settings.set("voice_enabled", self.voice_enabled.isChecked())
            
            self.settings.save()
            
            QMessageBox.information(self, "Settings", f"✅ Settings saved!\n\nOutput folder: {output_folder}")
            logger.info("Settings saved")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            QMessageBox.warning(self, "Error", f"❌ Failed to save settings: {e}")

    def _create_theme_switcher(self):
        """Create theme switcher"""
        from app.gui.themes import ThemeManager
        
        group = QGroupBox("Theme")
        layout = QVBoxLayout(group)
        
        self.theme_combo = QComboBox()
        themes = ThemeManager.get_theme_names_with_labels()
        for label, name in themes:
            self.theme_combo.addItem(label, name)
        
        # Set current theme
        current = self.settings.get("theme", "professional_blue")
        index = self.theme_combo.findData(current)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        layout.addWidget(self.theme_combo)
        
        return group

    def _on_theme_changed(self, index):
        """Handle theme change"""
        theme_name = self.theme_combo.currentData()
        from app.gui.themes import ThemeManager
        ThemeManager.apply_theme(theme_name)
        self.settings.set("theme", theme_name)
        self.settings.save()
    def _create_general_group(self):
        """Create general settings group"""
        group = QGroupBox("General Settings")
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #E8E8E8;
                border-radius: 10px;
                padding-top: 14px;
                font-weight: 600;
                font-size: 14px;
                color: #2D3436;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #2D3436;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(12)
        
        # Output folder
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Output Folder:"))
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select output folder...")
        self.folder_input.setStyleSheet("""
            QLineEdit {
                padding: 6px 12px;
                border: 1px solid #E8E8E8;
                border-radius: 6px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #2E5A8A;
            }
        """)
        folder_layout.addWidget(self.folder_input, 1)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet("""
            QPushButton {
                background: #2E5A8A;
                color: white;
                padding: 6px 16px;
                border: none;
                border-radius: 6px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #1E3A5F;
            }
        """)
        browse_btn.clicked.connect(self.browse_output_folder)
        folder_layout.addWidget(browse_btn)
        layout.addLayout(folder_layout)
        
        # Default format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Default Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['pdf', 'docx', 'jpg', 'png', 'mp3', 'mp4', 'zip'])
        self.format_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 1px solid #E8E8E8;
                border-radius: 6px;
                font-size: 12px;
                min-width: 120px;
            }
            QComboBox:focus {
                border-color: #2E5A8A;
            }
        """)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        layout.addLayout(format_layout)
        
        return group

    def _create_conversion_group(self):
        """Create conversion settings group"""
        group = QGroupBox("Conversion Settings")
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #E8E8E8;
                border-radius: 10px;
                padding-top: 14px;
                font-weight: 600;
                font-size: 14px;
                color: #2D3436;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #2D3436;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        # Quality
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Low", "Medium", "High"])
        self.quality_combo.setCurrentIndex(2)
        self.quality_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 1px solid #E8E8E8;
                border-radius: 6px;
                font-size: 12px;
                min-width: 100px;
            }
            QComboBox:focus {
                border-color: #2E5A8A;
            }
        """)
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        layout.addLayout(quality_layout)
        
        # Options
        self.keep_original = QCheckBox("Keep original files after conversion")
        self.keep_original.setStyleSheet("font-size: 12px; color: #2D3436;")
        layout.addWidget(self.keep_original)
        
        self.auto_convert = QCheckBox("Enable auto-conversion for watched folders")
        self.auto_convert.setStyleSheet("font-size: 12px; color: #2D3436;")
        layout.addWidget(self.auto_convert)
        
        return group

    def _create_theme_group(self):
        """Create theme settings group"""
        from app.gui.themes import ThemeManager
        
        group = QGroupBox("Theme")
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #E8E8E8;
                border-radius: 10px;
                padding-top: 14px;
                font-weight: 600;
                font-size: 14px;
                color: #2D3436;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #2D3436;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        self.theme_combo = QComboBox()
        themes = ThemeManager.get_theme_names_with_labels()
        for label, name in themes:
            self.theme_combo.addItem(label, name)
        
        # Set current theme
        current = self.settings.get("theme", "professional_blue")
        index = self.theme_combo.findData(current)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        layout.addWidget(self.theme_combo)
        
        return group

    def _create_voice_group(self):
        """Create voice settings group"""
        group = QGroupBox("Voice Settings")
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #E8E8E8;
                border-radius: 10px;
                padding-top: 14px;
                font-weight: 600;
                font-size: 14px;
                color: #2D3436;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #2D3436;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        self.voice_enabled = QCheckBox("Enable voice control")
        self.voice_enabled.setStyleSheet("font-size: 12px; color: #2D3436;")
        layout.addWidget(self.voice_enabled)
        
        return group

    def _on_theme_changed(self, index):
        """Handle theme change"""
        theme_name = self.theme_combo.currentData()
        from app.gui.themes import ThemeManager
        ThemeManager.apply_theme(theme_name)
        self.settings.set("theme", theme_name)
        self.settings.save()