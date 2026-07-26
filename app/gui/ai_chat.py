# app/gui/ai_chat.py - DEBUG VERSION
"""
AI Chat Widget - Debug Version to Fix Send Button
"""

from pathlib import Path

from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QLineEdit, QScrollArea,
    QFrame, QComboBox, QProgressBar, QMessageBox
)
from PySide6.QtGui import QTextCursor, QFont, QPixmap

from app.core.ai_engine import ai_engine
from app.core.image_ai import image_ai
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AIChatWidget(QWidget):
    """AI Chat Widget - Debug Version"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image_worker = None
        self.status_timer = None
        self.parent_dashboard = parent
        
        logger.info("=" * 50)
        logger.info("AIChatWidget INITIALIZED")
        logger.info(f"Parent: {parent}")
        logger.info("=" * 50)
        
        self.setup_ui()
        self.update_status()
        
        # Update status every 3 seconds
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(3000)
    
    def setup_ui(self):
        """Setup the chat UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        # Model status bar
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("🟢 AI Ready")
        self.status_label.setStyleSheet("""
            font-size: 11px;
            padding: 3px 12px;
            border-radius: 12px;
            background: #E8F5E9;
            color: #2E7D32;
        """)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.image_status = QLabel("🎨")
        self.image_status.setToolTip("Image Generation Status")
        self.image_status.setStyleSheet("font-size: 14px;")
        status_layout.addWidget(self.image_status)
        layout.addLayout(status_layout)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setMinimumHeight(300)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 12px;
                background: #FFFFFF;
                font-size: 13px;
                color: #1A202C;
                min-height: 300px;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background: #E2E8F0;
                height: 6px;
            }
            QProgressBar::chunk {
                background: #2E5A8A;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Quick actions
        quick_layout = QHBoxLayout()
        for label, cmd in [("📄 PDF", "convert to pdf"), ("❓ Help", "help")]:
            btn = QPushButton(label)
            btn.setStyleSheet("""
                QPushButton {
                    background: #EDF2F7;
                    border: 1px solid #E2E8F0;
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 10px;
                    color: #2D3748;
                }
                QPushButton:hover {
                    background: #E2E8F0;
                }
            """)
            btn.clicked.connect(lambda checked, c=cmd: self.send_message(c))
            quick_layout.addWidget(btn)
        quick_layout.addStretch()
        layout.addLayout(quick_layout)
        
        # ===== INPUT AREA =====
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask AI anything...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                font-size: 13px;
                color: #1A202C;
                background: #FFFFFF;
            }
            QLineEdit:focus {
                border-color: #2E5A8A;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        # ===== SEND BUTTON - WITH DEBUG =====
        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: #2E5A8A;
                color: #FFFFFF;
                padding: 8px 20px;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
                min-width: 60px;
            }
            QPushButton:hover {
                background: #1E3A5F;
            }
        """)
        # FIX: Direct connection with debug print
        self.send_btn.clicked.connect(self.on_send_clicked)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        # Info
        info_layout = QHBoxLayout()
        info_label = QLabel("💡 Works offline")
        info_label.setStyleSheet("font-size: 10px; color: #A0AEC0;")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # Welcome message
        self.add_message("AI Assistant", "👋 Welcome! How can I help you?")
    
    # ============================================================
    # SEND METHODS - WITH DEBUG
    # ============================================================
    
    def on_send_clicked(self):
        """Called when send button is clicked - DEBUG"""
        logger.info("=" * 50)
        logger.info("🔴 SEND BUTTON CLICKED!")
        logger.info(f"Input field text: '{self.input_field.text() if self.input_field else 'No input'}'")
        logger.info("=" * 50)
        self.send_message()
    
    def send_message(self, message: str = None):
        """Send a message - WITH DEBUG"""
        logger.info("=" * 50)
        logger.info("📩 send_message() CALLED")
        
        try:
            # Get message from input field if not provided
            if message is None:
                if not self.input_field:
                    logger.error("❌ No input field!")
                    return
                message = self.input_field.text().strip()
                logger.info(f"📝 Message from input: '{message}'")
            else:
                logger.info(f"📝 Message from param: '{message}'")
            
            # Check if message is empty
            if not message:
                logger.warning("⚠️ Empty message - ignoring")
                return
            
            # Clear input field
            if self.input_field:
                self.input_field.clear()
                logger.info("✅ Input field cleared")
            
            # Disable send button
            if self.send_btn:
                self.send_btn.setEnabled(False)
                self.send_btn.setText("⏳...")
                logger.info("✅ Send button disabled")
            
            # Add user message
            self.add_message("You", message)
            logger.info("✅ User message added")
            
            # Get dashboard
            dashboard = self._get_dashboard()
            logger.info(f"📊 Dashboard: {dashboard}")
            
            # Process with AI
            try:
                logger.info("🤖 Processing with AI engine...")
                response = ai_engine.process_request(message, dashboard)
                logger.info(f"🤖 AI response: '{response[:50]}...'")
                self.add_message("AI Assistant", response)
                logger.info("✅ AI response added")
            except Exception as e:
                logger.error(f"❌ AI engine error: {e}")
                self.add_message("AI Assistant", f"Error: {str(e)}")
            
        except Exception as e:
            logger.error(f"❌ Send message error: {e}")
            import traceback
            traceback.print_exc()
            self.add_message("AI Assistant", f"Error: {str(e)}")
        finally:
            # Re-enable send button
            if self.send_btn:
                self.send_btn.setEnabled(True)
                self.send_btn.setText("Send")
                logger.info("✅ Send button re-enabled")
            if self.input_field:
                self.input_field.setFocus()
                logger.info("✅ Focus restored")
        
        logger.info("=" * 50)
    
    def _get_dashboard(self):
        """Get dashboard reference"""
        parent = self.parent()
        logger.info(f"🔍 Getting dashboard from parent: {parent}")
        
        if hasattr(parent, 'dashboard_page'):
            logger.info("✅ Found dashboard_page")
            return parent.dashboard_page
        
        if hasattr(parent, 'add_files'):
            logger.info("✅ Parent is dashboard")
            return parent
        
        window = self.window()
        logger.info(f"🔍 Checking window: {window}")
        if hasattr(window, 'dashboard_page'):
            logger.info("✅ Found dashboard_page on window")
            return window.dashboard_page
        
        logger.warning("⚠️ No dashboard found")
        return None
    
    # ============================================================
    # ADD MESSAGE
    # ============================================================
    
    def add_message(self, sender: str, message: str):
        """Add a message to the chat display"""
        if not self.chat_display:
            logger.error("❌ No chat display!")
            return
        
        logger.info(f"📝 Adding message: {sender} - {message[:30]}...")
        
        self.chat_display.setUpdatesEnabled(False)
        
        try:
            if sender == "You":
                formatted = f'''
                <div style="margin: 4px 0; padding: 8px 12px; background: #EBF4FF; border-radius: 8px;">
                    <b style="color: #2B6CB0; font-size: 11px;">👤 {sender}:</b>
                    <p style="color: #1A202C; font-size: 13px; margin: 4px 0 0 0; white-space: pre-wrap;">{message}</p>
                </div>
                '''
            else:
                formatted = f'''
                <div style="margin: 4px 0; padding: 8px 12px; background: #F7FAFC; border-radius: 8px;">
                    <b style="color: #2E5A8A; font-size: 11px;">🤖 {sender}:</b>
                    <p style="color: #1A202C; font-size: 13px; margin: 4px 0 0 0; white-space: pre-wrap;">{message}</p>
                </div>
                '''
            
            cursor = self.chat_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.chat_display.setTextCursor(cursor)
            self.chat_display.insertHtml(formatted)
            
            # Auto-scroll
            scrollbar = self.chat_display.verticalScrollBar()
            if scrollbar:
                scrollbar.setValue(scrollbar.maximum())
            
            logger.info("✅ Message added to chat")
            
        finally:
            self.chat_display.setUpdatesEnabled(True)
    
    # ============================================================
    # STATUS
    # ============================================================
    
    def update_status(self):
        """Update status labels"""
        if self.status_label:
            self.status_label.setText("🟢 AI Ready")
    
    def closeEvent(self, event):
        """Clean up on close"""
        if self.status_timer:
            self.status_timer.stop()
        event.accept()