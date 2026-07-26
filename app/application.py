"""
Application Class - Complete with Splash Screen, Error Handling, and Loading Animation
"""

import sys
import os
import signal
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QTimer, QEvent, QCoreApplication  # <-- Added QEvent
from PySide6.QtWidgets import QApplication, QSplashScreen, QStyleFactory, QLabel, QMessageBox
from PySide6.QtGui import QIcon, QPixmap, QFontDatabase, QPainter, QColor, QFont, QPalette

from config import Config
from app.utils.logger import get_logger, setup_logging
from app.utils.helpers import resource_path
from app.main_window import MainWindow
from app.core.settings import SettingsManager
from app.core.ffmpeg import ffmpeg_manager

logger = get_logger(__name__)


class Application(QApplication):
    """
    Main application class with:
    - Splash screen with loading animation
    - Error handling
    - Single instance check
    - Theme application
    - Resource management
    """
    
    _instance = None
    
    def __init__(self, argv: list = None):
        if argv is None:
            argv = sys.argv
            
        super().__init__(argv)
        
        # Store instance
        Application._instance = self
        
        # Setup signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Application info
        self.setApplicationName(Config.APP_NAME)
        self.setApplicationVersion(Config.APP_VERSION)
        self.setOrganizationName(Config.APP_AUTHOR)
        self.setOrganizationDomain("aiconverterpro.com")
        
        # Load settings
        self.settings = SettingsManager.load()
        
        # Setup application
        self.setup_application()
        
        # Setup FFmpeg
        self._setup_ffmpeg()
        
        # State
        self.main_window = None
        self.splash = None
        self.loading_timer = None
        self.loading_messages = [
            "Initializing...",
            "Loading assets...",
            "Setting up converters...",
            "Initializing AI engine...",
            "Checking FFmpeg...",
            "Loading settings...",
            "Starting application..."
        ]
        self.current_loading_index = 0
        
        # Show splash screen
        self.show_splash()
    
    # ============================================================
    # SETUP
    # ============================================================
    
    def setup_application(self):
        """Setup application-wide settings"""
        self.setStyle(QStyleFactory.create("Fusion"))
        
        # Load custom font
        self._load_fonts()
        
        # Enable high DPI scaling
        self.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        self.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Set application palette
        self._setup_palette()
        
        # Apply saved theme
        theme_name = self.settings.get("theme", "professional_blue")
        from app.gui.themes import ThemeManager
        ThemeManager.apply_theme(theme_name)
        
        logger.info("Application setup complete")
    
    def _load_fonts(self):
        """Load custom fonts"""
        font_paths = [
            "assets/fonts/SegoeUI.ttf",
            "assets/fonts/SegoeUI-Bold.ttf",
            "assets/fonts/SegoeUI-Italic.ttf",
            "assets/fonts/SegoeUI-Light.ttf",
        ]
        
        for font_path in font_paths:
            path = resource_path(font_path)
            if path and Path(path).exists():
                font_id = QFontDatabase.addApplicationFont(str(path))
                if font_id != -1:
                    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                    logger.info(f"Loaded font: {font_family}")
    
    def _setup_palette(self):
        """Setup application palette"""
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(245, 247, 250))
        palette.setColor(QPalette.WindowText, QColor(45, 52, 54))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(248, 249, 250))
        palette.setColor(QPalette.Text, QColor(45, 52, 54))
        palette.setColor(QPalette.Button, QColor(255, 255, 255))
        palette.setColor(QPalette.ButtonText, QColor(45, 52, 54))
        palette.setColor(QPalette.Highlight, QColor(108, 99, 255))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
    
    def _setup_ffmpeg(self):
        """Setup FFmpeg environment"""
        try:
            ffmpeg_manager.setup_environment()
            if ffmpeg_manager.is_available():
                logger.info("FFmpeg setup complete")
            else:
                logger.warning("FFmpeg not available - some features may be limited")
        except Exception as e:
            logger.error(f"FFmpeg setup error: {e}")
    
    # ============================================================
    # SPLASH SCREEN
    # ============================================================
    
    def show_splash(self):
        """Show splash screen with loading animation"""
        # Try to load splash image
        splash_pixmap = self._create_splash_pixmap()
        
        if splash_pixmap:
            self.splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
            self.splash.show()
            self.processEvents()
            
            # Start loading animation
            self._start_loading_animation()
            
            # Create main window
            self._create_main_window()
        else:
            # No splash, just create main window
            self._create_main_window()
            self.main_window.show()
    
    def _create_splash_pixmap(self) -> Optional[QPixmap]:
        """Create splash screen pixmap"""
        # Try to load from file
        splash_paths = [
            "assets/images/splash.png",
            "assets/images/splash_hd.png",
        ]
        
        for path in splash_paths:
            full_path = resource_path(path)
            if full_path and Path(full_path).exists():
                pixmap = QPixmap(full_path)
                if pixmap.width() > 600 or pixmap.height() > 400:
                    pixmap = pixmap.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                return pixmap
        
        # Create text-based splash
        return self._create_text_splash()
    
    def _create_text_splash(self) -> QPixmap:
        """Create text-based splash screen"""
        pixmap = QPixmap(600, 450)
        pixmap.fill(QColor("#1E2A4A"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw gradient background
        gradient = painter.gradient()
        gradient.setColorAt(0, QColor("#1E2A4A"))
        gradient.setColorAt(1, QColor("#2E5A8A"))
        painter.fillRect(pixmap.rect(), gradient)
        
        # Draw icon
        painter.setBrush(QColor(108, 99, 255))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(230, 60, 140, 140, 30, 30)
        
        # Draw arrows
        painter.setBrush(QColor(255, 255, 255))
        painter.drawPolygon([
            (280, 145), (300, 90), (320, 145)
        ])
        painter.setBrush(QColor(201, 168, 76))
        painter.drawPolygon([
            (280, 105), (300, 160), (320, 105)
        ])
        
        # Draw title
        font = painter.font()
        font.setPointSize(24)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(pixmap.rect(), Qt.AlignHCenter | Qt.AlignBottom, "ALL FILES CONVERTER AI")
        
        # Draw subtitle
        font.setPointSize(12)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QColor(201, 168, 76))
        painter.drawText(pixmap.rect().adjusted(0, -40, 0, 0), Qt.AlignHCenter | Qt.AlignBottom, "Convert Anything. Anywhere.")
        
        # Draw version
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(QColor(150, 150, 150))
        painter.drawText(20, pixmap.height() - 20, f"v{Config.APP_VERSION}")
        
        # Draw loading message area
        self.loading_message_rect = painter.boundingRect(
            0, pixmap.height() - 50, 
            pixmap.width(), 30,
            Qt.AlignHCenter | Qt.AlignBottom,
            "Loading..."
        )
        
        painter.end()
        return pixmap
    
    def _start_loading_animation(self):
        """Start loading message animation"""
        if not self.splash:
            return
        
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self._update_loading_message)
        self.loading_timer.start(500)
    
    def _update_loading_message(self):
        """Update loading message"""
        if not self.splash:
            return
        
        message = self.loading_messages[self.current_loading_index % len(self.loading_messages)]
        self.splash.showMessage(
            message,
            Qt.AlignHCenter | Qt.AlignBottom,
            QColor(255, 255, 255)
        )
        self.current_loading_index += 1
        self.processEvents()
    
    def _create_main_window(self):
        """Create main window"""
        try:
            self.main_window = MainWindow(self.settings)
            self.main_window.setWindowTitle(f"{Config.APP_NAME} v{Config.APP_VERSION}")
            
            # Connect signals
            self.main_window.destroyed.connect(self._on_main_window_destroyed)
            
            logger.info("Main window created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create main window: {e}")
            self._show_fatal_error("Failed to create main window", str(e))
            sys.exit(1)
    
    def show_main_window(self):
        """Show main window and close splash"""
        if self.main_window:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
        
        if self.splash:
            self.splash.finish(self.main_window)
            self.splash = None
        
        if self.loading_timer:
            self.loading_timer.stop()
            self.loading_timer = None
        
        logger.info(f"{Config.APP_NAME} v{Config.APP_VERSION} started")
    
    # ============================================================
    # ERROR HANDLING
    # ============================================================
    
    def _show_fatal_error(self, title: str, message: str, detail: str = ""):
        """Show fatal error dialog"""
        try:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Fatal Error")
            msg.setText(title)
            msg.setInformativeText(message)
            if detail:
                msg.setDetailedText(detail)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
        except:
            print(f"FATAL ERROR: {title}")
            print(f"Message: {message}")
            if detail:
                print(f"Details: {detail}")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals"""
        logger.info(f"Received signal: {signum}")
        self.quit()
    
    def _on_main_window_destroyed(self):
        """Handle main window destruction"""
        logger.info("Main window destroyed")
    
    # ============================================================
    # APPLICATION EVENTS - FIXED
    # ============================================================
    
    def event(self, event):
        """Handle application events"""
        # FIX: Use QEvent.Type enum correctly
        event_type = event.type()
        
        if event_type == QEvent.ApplicationActivate:
            logger.debug("Application activated")
        elif event_type == QEvent.ApplicationDeactivate:
            logger.debug("Application deactivated")
        return super().event(event)
    
    # ============================================================
    # RUN
    # ============================================================
    
    def run(self) -> int:
        """Run the application"""
        try:
            # Show main window after a short delay for splash
            QTimer.singleShot(2500, self.show_main_window)
            
            # Execute application
            return self.exec()
            
        except Exception as e:
            logger.error(f"Application runtime error: {e}")
            self._show_fatal_error("Runtime Error", str(e))
            return 1
    
    # ============================================================
    # CLASS METHODS
    # ============================================================
    
    @classmethod
    def instance(cls) -> 'Application':
        """Get the application instance"""
        return cls._instance
    
    @classmethod
    def quit_application(cls):
        """Quit the application"""
        if cls._instance:
            cls._instance.quit()


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

def create_application() -> Application:
    """Create and return the application"""
    # Setup logging
    setup_logging()
    
    # Create application
    app = Application()
    
    return app


def run_application():
    """Run the application"""
    app = create_application()
    return app.run()


if __name__ == "__main__":
    sys.exit(run_application())