# app/gui/topbar.py
"""
Top Bar - Light Theme with Visible Text and Search
"""

from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame
)
from PySide6.QtGui import QIcon


class TopBar(QWidget):
    # Signal emitted when search text changes
    search_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        self.setFixedHeight(50)
        self.setStyleSheet("""
            TopBar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E8E8E8;
            }
            QLabel {
                color: #2D3436;
                background: transparent;
            }
            QPushButton {
                background: transparent;
                color: #2D3436;
            }
            QPushButton:hover {
                background: #F5F7FA;
                border-radius: 6px;
            }
            QLineEdit {
                background: #F5F7FA;
                border: 1px solid #E8E8E8;
                border-radius: 6px;
                padding: 4px 10px;
                color: #2D3436;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #6C63FF;
                background: #FFFFFF;
            }
            QLineEdit::placeholder {
                color: #A0A0A0;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(8)
        
        # Page title
        self.title_label = QLabel("Dashboard")
        self.title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #2D3436;
            font-family: 'Segoe UI', sans-serif;
        """)
        layout.addWidget(self.title_label)
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search files...")
        self.search_input.setFixedWidth(180)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: #F5F7FA;
                border: 1px solid #E8E8E8;
                border-radius: 6px;
                padding: 4px 10px;
                color: #2D3436;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #6C63FF;
                background: #FFFFFF;
            }
            QLineEdit::placeholder {
                color: #A0A0A0;
            }
        """)
        self.search_input.textChanged.connect(self.search_changed.emit)
        layout.addWidget(self.search_input)
        
        layout.addStretch()
        
        # Stats - FIXED: Added stats_label
        self.stats_label = QLabel("📄 0 files | 🔄 0 conversions")
        self.stats_label.setStyleSheet("""
            font-size: 11px;
            color: #636E72;
            padding: 0 8px;
            font-family: 'Segoe UI', sans-serif;
        """)
        layout.addWidget(self.stats_label)
        
        # Settings button
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 6px;
                background: transparent;
                color: #636E72;
                font-size: 16px;
                padding: 0px;
            }
            QPushButton:hover {
                background: #F5F7FA;
                color: #2D3436;
            }
        """)
        self.settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(self.settings_btn)
        
        # Voice button
        # self.voice_btn = QPushButton("🎤")
        # self.voice_btn.setFixedSize(32, 32)
        # self.voice_btn.setToolTip("Toggle Voice Control")
        # self.voice_btn.setCursor(Qt.PointingHandCursor)
        # self.voice_btn.setStyleSheet("""
        #     QPushButton {
        #         border: none;
        #         border-radius: 6px;
        #         background: transparent;
        #         color: #636E72;
        #         font-size: 14px;
        #         padding: 0px;
        #     }
        #     QPushButton:hover {
        #         background: #F5F7FA;
        #         color: #2D3436;
        #     }
        # """)
        # layout.addWidget(self.voice_btn)
        
        # Auto button
        # self.auto_btn = QPushButton("")
        # self.auto_btn.setFixedSize(32, 32)
        # self.auto_btn.setToolTip("Toggle Auto-Conversion")
        # self.auto_btn.setCursor(Qt.PointingHandCursor)
        # self.auto_btn.setStyleSheet("""
        #     QPushButton {
        #         border: none;
        #         border-radius: 6px;
        #         background: transparent;
        #         color: #636E72;
        #         font-size: 14px;
        #         padding: 0px;
        #     }
        #     QPushButton:hover {
        #         background: #F5F7FA;
        #         color: #2D3436;
        #     }
        # """)
        # layout.addWidget(self.auto_btn)
        
    def open_settings(self):
        """Open settings page"""
        main_window = self.window()
        if hasattr(main_window, 'switch_page'):
            main_window.switch_page('settings')
        else:
            for widget in main_window.children():
                if hasattr(widget, 'switch_page'):
                    widget.switch_page('settings')
                    break
        
    def update_title(self, page: str):
        """Update the page title"""
        titles = {
            "dashboard": "Dashboard",
            "ai": "AI Assistant",
            "history": "History",
            "settings": "Settings"
        }
        self.title_label.setText(titles.get(page, page.title()))
        
    def update_stats(self, file_count: int, conversion_count: int = 0):
        """Update the stats label"""
        self.stats_label.setText(f"📄 {file_count} files | 🔄 {conversion_count} conversions")
    
    def set_search_text(self, text: str):
        """Set search text programmatically"""
        self.search_input.setText(text)