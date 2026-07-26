"""
Sidebar Navigation - Light Theme with Visible Text
"""

from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QSpacerItem, QSizePolicy, QFrame
)
from PySide6.QtGui import QIcon, QFont

from config import Config
from app.utils.helpers import resource_path


class SidebarButton(QPushButton):
    def __init__(self, text, icon_path, parent=None):
        super().__init__(parent)
        self.setText(text)
        
        if icon_path:
            icon_path_full = resource_path(icon_path)
            if icon_path_full and Path(icon_path_full).exists():
                icon = QIcon(icon_path_full)
                self.setIcon(icon)
                self.setIconSize(QSize(20, 20))
        
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        
        # FIXED: Dark text for visibility on light background
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 10px 14px;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                background: transparent;
                color: #2D3436;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton:hover {
                background: #E8E8E8;
                color: #2D3436;
            }
            QPushButton:checked {
                background: #6C63FF;
                color: white;
            }
            QPushButton:checked:hover {
                background: #5A52D5;
                color: white;
            }
            QPushButton QIcon {
                margin-right: 12px;
            }
        """)


class Sidebar(QWidget):
    page_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFixedWidth(220)
        self.setMinimumWidth(220)
        self.setMaximumWidth(260)
        
        # Light theme background with visible text
        self.setStyleSheet("""
            Sidebar {
                background: #FFFFFF;
                border-right: 1px solid #E8E8E8;
            }
            QLabel {
                color: #2D3436;
            }
            QPushButton {
                color: #2D3436;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(4)
        
        # Logo
        logo_widget = QWidget()
        logo_layout = QVBoxLayout(logo_widget)
        logo_layout.setContentsMargins(8, 0, 8, 12)
        logo_layout.setSpacing(4)
        
        logo_label = QLabel("📁")
        logo_label.setStyleSheet("font-size: 28px; color: #2D3436;")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)
        
        name_label = QLabel(Config.APP_NAME)
        name_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2D3436;
            font-family: 'Segoe UI', sans-serif;
        """)
        name_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(name_label)
        
        version_label = QLabel(f"v{Config.APP_VERSION}")
        version_label.setStyleSheet("""
            font-size: 10px;
            color: #636E72;
        """)
        version_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(version_label)
        
        layout.addWidget(logo_widget)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background: #E8E8E8; max-height: 1px; margin: 4px 0;")
        layout.addWidget(separator)
        layout.addSpacing(8)
        
        self.nav_buttons = []
        
        nav_items = [
            ("Dashboard", "dashboard"),
            ("AI Assistant", "ai"),
            ("History", "history"),
            ("Settings", "settings"),
        ]
        
        for text, page in nav_items:
            btn = SidebarButton(text, None)
            btn.clicked.connect(lambda checked, p=page: self.navigate_to(p))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)
        
        layout.addSpacerItem(QSpacerItem(
            20, 40,
            QSizePolicy.Minimum,
            QSizePolicy.Expanding
        ))
        
        # Bottom section
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(4)
        
        version_info = QLabel("All Files Converter AI")
        version_info.setStyleSheet("""
            font-size: 10px;
            color: #636E72;
            font-weight: 500;
            padding: 4px;
        """)
        version_info.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(version_info)
        
        layout.addWidget(bottom_widget)
        
        # Set first button as checked
        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)
        
    def navigate_to(self, page: str):
        for btn in self.nav_buttons:
            btn.setChecked(False)
        
        page_map = {"dashboard": 0, "ai": 1, "history": 2, "settings": 3}
        if page in page_map:
            self.nav_buttons[page_map[page]].setChecked(True)
        
        self.page_changed.emit(page)