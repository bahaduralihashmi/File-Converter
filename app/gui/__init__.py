"""
GUI Package
"""

from .dashboard import ProfessionalDashboard
from .sidebar import Sidebar
from .topbar import TopBar
from .ai_chat import AIChatWidget
from .history import HistoryWidget
from .settings import SettingsWidget
from .cards import StatsCard
from .progress_widget import ProgressWidget
from .dialogs import Dialogs, ProgressDialog, SettingsDialog
from .styles import ThemeManager
from .ocr_dialog import OCRDialog

# Alias for backward compatibility
Dashboard = ProfessionalDashboard

__all__ = [
    'Dashboard',
    'ProfessionalDashboard',
    'Sidebar',
    'TopBar',
    'AIChatWidget',
    'HistoryWidget',
    'SettingsWidget',
    'StatsCard',
    'ProgressWidget',
    'Dialogs',
    'ProgressDialog',
    'SettingsDialog',
    'ThemeManager',
    'OCRDialog'
]