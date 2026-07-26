"""
Main Window - Complete with Theme Support, Window Management, and Shortcuts
"""

from pathlib import Path

from PySide6.QtCore import Qt, QSize, QTimer, QSettings
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QMessageBox, QMenuBar, QMenu, QToolBar,
    QStatusBar, QLabel, QProgressBar, QSplitter
)
from PySide6.QtGui import QIcon, QAction, QKeySequence, QCloseEvent

from config import Config
from app.gui.sidebar import Sidebar
from app.gui.topbar import TopBar
from app.gui.dashboard import ProfessionalDashboard
from app.gui.ai_chat import AIChatWidget
from app.gui.history import HistoryWidget
from app.gui.settings import SettingsWidget
from app.utils.logger import get_logger
from app.utils.helpers import resource_path
from app.core.settings import SettingsManager

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main application window with complete functionality"""
    
    def __init__(self, settings: SettingsManager):
        super().__init__()
        
        self.settings = settings
        self.current_page = "dashboard"
        self.is_closing = False
        
        # Load window state
        self._load_window_state()
        
        # Setup UI
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.setup_shortcuts()
        
        # Apply saved theme
        self._apply_theme()
        
        logger.info("Main window initialized")
    
    # ============================================================
    # UI SETUP
    # ============================================================
    
    def setup_ui(self):
        """Setup main window UI"""
        # Window properties
        self.setWindowTitle(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        self.setMinimumSize(Config.MIN_WIDTH, Config.MIN_HEIGHT)
        self.resize(
            self.settings.get('window_width', Config.WINDOW_WIDTH),
            self.settings.get('window_height', Config.WINDOW_HEIGHT)
        )
        
        # Window icon
        icon_path = resource_path("assets/icons/app.ico")
        if icon_path and Path(icon_path).exists():
            self.setWindowIcon(QIcon(icon_path))
        
        # Central widget
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        central_widget.setStyleSheet("background: #F5F7FA;")
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.page_changed.connect(self.switch_page)
        main_layout.addWidget(self.sidebar)
        
        # Content area
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        content_widget.setStyleSheet("background: #F5F7FA;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Top bar
        self.topbar = TopBar(self)
        self.topbar.search_changed.connect(self._on_search_changed)
        content_layout.addWidget(self.topbar)
        
        # Pages
        self.pages = QStackedWidget()
        self.pages.setObjectName("pages")
        self.pages.setStyleSheet("background: #F5F7FA;")
        
        # Create pages
        self.dashboard_page = ProfessionalDashboard(self)
        self.ai_page = AIChatWidget(self)
        self.history_page = HistoryWidget(self)
        self.settings_page = SettingsWidget(self)
        
        # Add pages
        self.pages.addWidget(self.dashboard_page)  # index 0
        self.pages.addWidget(self.ai_page)         # index 1
        self.pages.addWidget(self.history_page)    # index 2
        self.pages.addWidget(self.settings_page)   # index 3
        
        content_layout.addWidget(self.pages)
        main_layout.addWidget(content_widget, 1)
        
        # Set initial page
        self.switch_page("dashboard")
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background: #FFFFFF;
                border-bottom: 1px solid #E8E8E8;
                color: #2D3436;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }
            QMenuBar::item {
                padding: 4px 10px;
                background: transparent;
            }
            QMenuBar::item:selected {
                background: #F5F7FA;
            }
            QMenuBar::item:pressed {
                background: #6C63FF;
                color: white;
            }
        """)
        
        # ===== FILE MENU =====
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open Files...", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(lambda: self.dashboard_page.add_files())
        file_menu.addAction(open_action)
        
        open_folder_action = QAction("Open &Folder...", self)
        open_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_folder_action.triggered.connect(lambda: self.dashboard_page.add_folder())
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        # Recent files
        self.recent_menu = file_menu.addMenu("Recent Files")
        self._update_recent_menu()
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # ===== EDIT MENU =====
        edit_menu = menubar.addMenu("&Edit")
        
        clear_action = QAction("&Clear All Files", self)
        clear_action.setShortcut(QKeySequence("Ctrl+W"))
        clear_action.triggered.connect(lambda: self.dashboard_page.remove_all_files())
        edit_menu.addAction(clear_action)
        
        edit_menu.addSeparator()
        
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(lambda: self.switch_page("settings"))
        edit_menu.addAction(settings_action)
        
        # ===== VIEW MENU =====
        view_menu = menubar.addMenu("&View")
        
        for page, label in [
            ("dashboard", "Dashboard"),
            ("ai", "AI Assistant"),
            ("history", "History"),
            ("settings", "Settings")
        ]:
            action = QAction(label, self)
            action.triggered.connect(lambda checked, p=page: self.switch_page(p))
            view_menu.addAction(action)
        
        view_menu.addSeparator()
        
        # Theme submenu
        theme_menu = view_menu.addMenu("Theme")
        themes = [
            ("Professional Blue", "professional_blue"),
            ("Professional Slate", "professional_slate"),
            ("Clean Teal", "clean_teal"),
            ("Elegant Plum", "elegant_plum"),
            ("Clean White", "clean_white"),
            ("Soft Green", "soft_green"),
            ("Dark Pro", "dark_pro"),
        ]
        for label, theme_name in themes:
            action = QAction(label, self)
            action.triggered.connect(lambda checked, t=theme_name: self._change_theme(t))
            theme_menu.addAction(action)
        
        # ===== CONVERT MENU =====
        convert_menu = menubar.addMenu("&Convert")
        
        convert_pdf = QAction("Convert to PDF", self)
        convert_pdf.triggered.connect(lambda: self.dashboard_page.quick_convert("pdf"))
        convert_menu.addAction(convert_pdf)
        
        convert_docx = QAction("Convert to DOCX", self)
        convert_docx.triggered.connect(lambda: self.dashboard_page.quick_convert("docx"))
        convert_menu.addAction(convert_docx)
        
        convert_menu.addSeparator()
        
        convert_jpg = QAction("Convert to JPG", self)
        convert_jpg.triggered.connect(lambda: self.dashboard_page.quick_convert("jpg"))
        convert_menu.addAction(convert_jpg)
        
        convert_png = QAction("Convert to PNG", self)
        convert_png.triggered.connect(lambda: self.dashboard_page.quick_convert("png"))
        convert_menu.addAction(convert_png)
        
        convert_menu.addSeparator()
        
        convert_mp3 = QAction("Convert to MP3", self)
        convert_mp3.triggered.connect(lambda: self.dashboard_page.quick_convert("mp3"))
        convert_menu.addAction(convert_mp3)
        
        convert_mp4 = QAction("Convert to MP4", self)
        convert_mp4.triggered.connect(lambda: self.dashboard_page.quick_convert("mp4"))
        convert_menu.addAction(convert_mp4)
        
        # ===== HELP MENU =====
        help_menu = menubar.addMenu("&Help")
        
        shortcuts_action = QAction("Keyboard Shortcuts", self)
        shortcuts_action.setShortcut(QKeySequence("Ctrl+Shift+?"))
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup status bar"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background: #FFFFFF;
                color: #636E72;
                font-size: 11px;
                border-top: 1px solid #E8E8E8;
                padding: 2px 10px;
            }
            QStatusBar::item {
                border: none;
            }
        """)
        
        # Status label
        self.status_label = QLabel("✅ Ready")
        status_bar.addWidget(self.status_label)
        
        # Progress bar
        self.status_progress = QProgressBar()
        self.status_progress.setRange(0, 100)
        self.status_progress.setValue(0)
        self.status_progress.setFixedWidth(100)
        self.status_progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 3px;
                background: #E8E8E8;
                height: 6px;
                max-height: 6px;
            }
            QProgressBar::chunk {
                background: #6C63FF;
                border-radius: 3px;
            }
        """)
        status_bar.addPermanentWidget(self.status_progress)
        
        # File count
        self.file_count_label = QLabel("📄 0 files")
        status_bar.addPermanentWidget(self.file_count_label)
        
        # Version
        version_label = QLabel(f"v{Config.APP_VERSION}")
        status_bar.addPermanentWidget(version_label)
    
    def setup_shortcuts(self):
        """Setup global keyboard shortcuts"""
        # Already set in menu actions
        pass
    
    # ============================================================
    # THEME
    # ============================================================
    
    def _apply_theme(self):
        """Apply saved theme"""
        theme = self.settings.get('theme', 'professional_blue')
        self._change_theme(theme)
    
    def _change_theme(self, theme_name: str):
        """Change application theme"""
        from app.gui.themes import ThemeManager
        
        # Save theme
        self.settings.set('theme', theme_name)
        self.settings.save()
        
        # Apply theme
        stylesheet = ThemeManager.get_stylesheet(theme_name)
        self.setStyleSheet(stylesheet)
        
        logger.info(f"Theme changed to: {theme_name}")
    
    # ============================================================
    # PAGE MANAGEMENT
    # ============================================================
    
    def switch_page(self, page_name: str):
        """Switch to a specific page"""
        page_index = {
            "dashboard": 0,
            "ai": 1,
            "history": 2,
            "settings": 3
        }.get(page_name, 0)
        
        self.pages.setCurrentIndex(page_index)
        self.current_page = page_name
        self.topbar.update_title(page_name)
        
        # Refresh page content
        if page_name == "history":
            self.refresh_history()
        elif page_name == "settings":
            if hasattr(self, 'settings_page'):
                self.settings_page.load_settings()
    
    def refresh_history(self):
        """Refresh history page"""
        if hasattr(self, 'history_page') and self.history_page:
            self.history_page.load_history()
            logger.info("History refreshed")
    
    # ============================================================
    # STATUS BAR
    # ============================================================
    
    def set_status(self, message: str, progress: int = None):
        """Set status bar message"""
        self.status_label.setText(message)
        
        if progress is not None:
            self.status_progress.setValue(progress)
            self.status_progress.setVisible(progress > 0 and progress < 100)
    
    def update_file_count(self, count: int):
        """Update file count in status bar"""
        self.file_count_label.setText(f"📄 {count} files")
    
    # ============================================================
    # RECENT FILES
    # ============================================================
    
    def _update_recent_menu(self):
        """Update recent files menu"""
        self.recent_menu.clear()
        
        recent_files = self.settings.get('recent_files', [])
        if not recent_files:
            no_recent = QAction("No recent files", self)
            no_recent.setEnabled(False)
            self.recent_menu.addAction(no_recent)
            return
        
        for file_path in recent_files[:10]:
            action = QAction(Path(file_path).name, self)
            action.setToolTip(file_path)
            action.triggered.connect(lambda checked, f=file_path: self._open_recent_file(f))
            self.recent_menu.addAction(action)
        
        self.recent_menu.addSeparator()
        
        clear_action = QAction("Clear Recent Files", self)
        clear_action.triggered.connect(self._clear_recent_files)
        self.recent_menu.addAction(clear_action)
    
    def _open_recent_file(self, file_path: str):
        """Open a recent file"""
        if Path(file_path).exists():
            self.dashboard_page._add_file_to_list(file_path)
        else:
            QMessageBox.warning(self, "File Not Found", f"File no longer exists:\n{file_path}")
            # Remove from recent
            recent = self.settings.get('recent_files', [])
            if file_path in recent:
                recent.remove(file_path)
                self.settings.set('recent_files', recent)
                self.settings.save()
                self._update_recent_menu()
    
    def _clear_recent_files(self):
        """Clear recent files list"""
        self.settings.set('recent_files', [])
        self.settings.save()
        self._update_recent_menu()
    
    # ============================================================
    # SEARCH
    # ============================================================
    
    def _on_search_changed(self, text: str):
        """Handle search text change"""
        if hasattr(self.dashboard_page, 'filter_files'):
            self.dashboard_page.filter_files(text)
    
    # ============================================================
    # WINDOW STATE
    # ============================================================
    
    def _load_window_state(self):
        """Load window state from settings"""
        # Window geometry will be restored in setup_ui
        pass
    
    def _save_window_state(self):
        """Save window state to settings"""
        if not self.is_closing:
            self.settings.set('window_width', self.width())
            self.settings.set('window_height', self.height())
            self.settings.save()
    
    def closeEvent(self, event: QCloseEvent):
        """Handle close event"""
        self.is_closing = True
        
        # Save window state
        self._save_window_state()
        
        # Clean up camera resources
        try:
            import cv2
            cv2.destroyAllWindows()
        except:
            pass
        
        # Close camera if open
        if hasattr(self, 'dashboard_page') and self.dashboard_page:
            self.dashboard_page.is_camera_active = False
        
        # Clean up voice
        try:
            from app.core.voice import voice_controller
            voice_controller.stop_listening()
        except:
            pass
        
        logger.info("Main window closed")
        event.accept()
    
    # ============================================================
    # DIALOGS
    # ============================================================
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
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
    
    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        shortcuts = """
        <h3>Keyboard Shortcuts</h3>
        <table>
        <tr><td><b>Ctrl+O</b></td><td>Open Files</td></tr>
        <tr><td><b>Ctrl+Shift+O</b></td><td>Open Folder</td></tr>
        <tr><td><b>Ctrl+Q</b></td><td>Quit Application</td></tr>
        <tr><td><b>Ctrl+W</b></td><td>Clear All Files</td></tr>
        <tr><td><b>Ctrl+,</b></td><td>Open Settings</td></tr>
        <tr><td><b>Ctrl+Shift+?</b></td><td>Show Shortcuts</td></tr>
        <tr><td><b>F5</b></td><td>Refresh</td></tr>
        <tr><td><b>ESC</b></td><td>Close Dialog/Cancel</td></tr>
        </table>
        """
        QMessageBox.information(self, "Keyboard Shortcuts", shortcuts)
    
    # ============================================================
    # DEPRECATED / BACKWARD COMPATIBILITY
    # ============================================================
    
    # Keep for backward compatibility
    def show_about(self):
        self.show_about()