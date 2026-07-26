"""
Progress Widget - Complete
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QFrame
)

class ProgressWidget(QFrame):
    def __init__(self):
        super().__init__()
        
        self.setStyleSheet("""
            QFrame {
                background: #F8F9FA;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
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
        """)
        layout.addWidget(self.progress_bar)
        
        text_layout = QHBoxLayout()
        text_layout.setSpacing(0)
        
        self.message_label = QLabel("Ready to convert")
        self.message_label.setStyleSheet("""
            font-size: 12px;
            color: #A0A0A0;
        """)
        text_layout.addWidget(self.message_label)
        
        text_layout.addStretch()
        
        self.percent_label = QLabel("0%")
        self.percent_label.setStyleSheet("""
            font-size: 12px;
            font-weight: bold;
            color: #6C63FF;
        """)
        text_layout.addWidget(self.percent_label)
        
        layout.addLayout(text_layout)
        
    def update_progress(self, value, message=None):
        self.progress_bar.setValue(value)
        self.percent_label.setText(f"{value}%")
        if message:
            self.message_label.setText(message)
            
    def set_active(self, active):
        if active:
            self.setStyleSheet("""
                QFrame {
                    background: #F5F6FA;
                    border: 1px solid #6C63FF;
                    border-radius: 8px;
                    padding: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: #F8F9FA;
                    border-radius: 8px;
                    padding: 12px;
                }
            """)