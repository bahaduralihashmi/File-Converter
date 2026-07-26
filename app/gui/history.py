# app/gui/history.py
"""
History Widget - Complete with Scroll Support
"""

from pathlib import Path
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QGroupBox, QMessageBox, QScrollArea
)

from app.core.history import HistoryManager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class HistoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.history = HistoryManager()
        
        self.setup_ui()
        self.load_history()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("📋 Conversion History"))
        header_layout.addStretch()
        
        self.stats_label = QLabel("")
        self.stats_label.setStyleSheet("color: #A0AEC0; font-size: 12px;")
        header_layout.addWidget(self.stats_label)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #2E5A8A;
                color: white;
                padding: 6px 16px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #1E3A5F;
            }
        """)
        refresh_btn.clicked.connect(self.load_history)
        header_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #E53E3E;
                color: white;
                padding: 6px 16px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #C53030;
            }
        """)
        clear_btn.clicked.connect(self.clear_history)
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        # Table with scroll
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Input File", "Output File", "Format", "Status", "Time"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                background: #FFFFFF;
                color: #1A202C;
                gridline-color: #E2E8F0;
            }
            QTableWidget::item {
                padding: 8px;
                color: #1A202C;
            }
            QTableWidget::item:selected {
                background: #2E5A8A;
                color: white;
            }
            QHeaderView::section {
                background: #F7FAFC;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #E2E8F0;
                color: #1A202C;
                font-weight: 600;
            }
        """)
        self.table.setMinimumHeight(300)
        table_layout.addWidget(self.table)
        
        # Wrap table in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #F7FAFC;
                border: none;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #CBD5E0;
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A0AEC0;
            }
        """)
        scroll_area.setWidget(table_container)
        layout.addWidget(scroll_area, 1)
        
        # Stats
        stats_group = QGroupBox("Statistics")
        stats_layout = QHBoxLayout(stats_group)
        
        self.total_label = QLabel("📊 Total: 0")
        self.success_label = QLabel("✅ Success: 0")
        self.failed_label = QLabel("❌ Failed: 0")
        self.rate_label = QLabel("📈 Rate: 0%")
        
        for label in [self.total_label, self.success_label, self.failed_label, self.rate_label]:
            label.setStyleSheet("font-weight: 500; color: #1A202C; font-size: 12px;")
            stats_layout.addWidget(label)
            stats_layout.addStretch()
        
        layout.addWidget(stats_group)
        
    # app/gui/history.py - Fix the load_history method

    def load_history(self):
        """Load history data into table"""
        try:
            entries = self.history.get_all()
            logger.info(f"Loading {len(entries)} history entries")
            
            # Clear table
            self.table.setRowCount(0)
            
            if not entries:
                logger.info("No history entries found")
                self.table.setRowCount(1)
                empty_item = QTableWidgetItem("No history entries yet. Convert some files to see them here!")
                empty_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(0, 0, empty_item)
                self.table.setSpan(0, 0, 1, 5)
                self.update_stats()
                return
            
            self.table.setRowCount(len(entries))
            self.table.clearSpans()  # Clear any spans
            
            for row, entry in enumerate(entries):
                input_path = entry.get("input", "")
                output_path = entry.get("output", "")
                
                input_name = Path(input_path).name if input_path else "Unknown"
                output_name = Path(output_path).name if output_path else "Unknown"
                
                self.table.setItem(row, 0, QTableWidgetItem(input_name))
                self.table.setItem(row, 1, QTableWidgetItem(output_name))
                self.table.setItem(row, 2, QTableWidgetItem(entry.get("format", "Unknown").upper()))
                
                status = "✅ Success" if entry.get("success") else "❌ Failed"
                status_item = QTableWidgetItem(status)
                if entry.get("success"):
                    status_item.setForeground(Qt.GlobalColor.green)
                else:
                    status_item.setForeground(Qt.GlobalColor.red)
                self.table.setItem(row, 3, status_item)
                
                timestamp = entry.get("timestamp", "")
                if timestamp:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(timestamp)
                        timestamp = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                self.table.setItem(row, 4, QTableWidgetItem(timestamp))
            
            self.update_stats()
            logger.info("History table updated successfully")
            
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            self.table.setRowCount(1)
            error_item = QTableWidgetItem(f"Error loading history: {str(e)}")
            error_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, error_item)
            self.table.setSpan(0, 0, 1, 5)
        
    def update_stats(self):
        stats = self.history.get_stats()
        self.total_label.setText(f"📊 Total: {stats['total']}")
        self.success_label.setText(f"✅ Success: {stats['successful']}")
        self.failed_label.setText(f"❌ Failed: {stats['failed']}")
        self.rate_label.setText(f"📈 Rate: {stats['success_rate']}")
        self.stats_label.setText(f"{stats['total']} entries")
        
    def clear_history(self):
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Delete all history entries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.history.clear()
            self.load_history()
    
    def refresh(self):
        """Refresh history display - called from dashboard"""
        logger.info("History refresh called")
        self.load_history()