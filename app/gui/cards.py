"""
Dashboard Cards - Complete
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QListWidget, QListWidgetItem, QPushButton,
    QFileDialog
)
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from pathlib import Path
from app.utils.helpers import format_file_size

class StatsCard(QFrame):
    def __init__(self, icon, label, value, color):
        super().__init__()
        
        self.setObjectName("statsCard")
        self.setFixedHeight(100)
        
        self.setStyleSheet("""
            QFrame#statsCard {
                background: white;
                border-radius: 12px;
                border: 1px solid #E8E8E8;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 32px;")
        icon_label.setFixedWidth(50)
        layout.addWidget(icon_label)
        
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #2D3436;
        """)
        text_layout.addWidget(self.value_label)
        
        self.label_label = QLabel(label)
        self.label_label.setStyleSheet("""
            font-size: 12px;
            color: #A0A0A0;
        """)
        text_layout.addWidget(self.label_label)
        
        layout.addWidget(text_widget)
        
    def set_value(self, value):
        self.value_label.setText(value)

class FileListWidget(QWidget):
    file_removed = Signal(str)
    
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        header = QLabel("📋 File List")
        header.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #2D3436;
        """)
        layout.addWidget(header)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #E8E8E8;
                border-radius: 8px;
                padding: 4px;
                background: white;
                min-height: 200px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background: #F5F6FA;
            }
            QListWidget::item:selected {
                background: #6C63FF;
                color: white;
            }
        """)
        self.list_widget.setMinimumHeight(200)
        layout.addWidget(self.list_widget)
        
    def add_file(self, file_path):
        path = Path(file_path)
        size = format_file_size(path.stat().st_size)
        
        item = QListWidgetItem(f"📄 {path.name} ({size})")
        item.setData(Qt.UserRole, file_path)
        self.list_widget.addItem(item)
        
    def add_files(self, file_paths):
        for file_path in file_paths:
            self.add_file(file_path)
        
    def remove_file(self, index):
        item = self.list_widget.takeItem(index)
        if item:
            file_path = item.data(Qt.UserRole)
            self.file_removed.emit(file_path)
            
    def clear(self):
        self.list_widget.clear()
        
    def get_files(self):
        files = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            files.append(item.data(Qt.UserRole))
        return files
        
    def update_status(self, file_path, status):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == file_path:
                current_text = item.text()
                parts = current_text.split(" (")
                if len(parts) >= 2:
                    new_text = f"{parts[0]} ({status})"
                else:
                    new_text = f"{current_text} ({status})"
                item.setText(new_text)
                break

class DropZoneWidget(QFrame):
    files_dropped = Signal(list)
    
    def __init__(self):
        super().__init__()
        
        self.setAcceptDrops(True)
        self.setMinimumHeight(120)
        
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px dashed #6C63FF;
                border-radius: 12px;
                padding: 20px;
            }
            QFrame:hover {
                background: #F5F6FA;
                border-color: #5A52D5;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel("📥")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        label = QLabel("Drag & drop your files here or click to browse")
        label.setStyleSheet("""
            font-size: 16px;
            color: #636E72;
        """)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        sub_label = QLabel("Supports 1000+ formats")
        sub_label.setStyleSheet("""
            font-size: 12px;
            color: #A0A0A0;
        """)
        sub_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub_label)
        
        self.mousePressEvent = self.browse_files
        
    def browse_files(self, event):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Convert",
            "",
            "All Files (*.*)"
        )
        if files:
            self.files_dropped.emit(files)
            
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame {
                    background: #F5F6FA;
                    border: 2px solid #6C63FF;
                    border-radius: 12px;
                    padding: 20px;
                }
            """)
            
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px dashed #6C63FF;
                border-radius: 12px;
                padding: 20px;
            }
            QFrame:hover {
                background: #F5F6FA;
                border-color: #5A52D5;
            }
        """)
        
    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path:
                files.append(file_path)
        if files:
            self.files_dropped.emit(files)
        self.dragLeaveEvent(event)