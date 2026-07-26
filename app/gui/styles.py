"""
Styles - Theme Manager
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

class ThemeManager:
    """Theme management for the application"""
    
    def __init__(self):
        self.current_theme = "light"
        
    def apply_theme(self, widget, theme: str = None):
        """Apply theme to widget"""
        if theme:
            self.current_theme = theme
            
        if self.current_theme == "dark":
            self._apply_dark_theme(widget)
        else:
            self._apply_light_theme(widget)
            
    def _apply_light_theme(self, widget):
        """Apply light theme"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(245, 246, 250))
        palette.setColor(QPalette.WindowText, QColor(45, 52, 54))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(248, 249, 250))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(45, 52, 54))
        palette.setColor(QPalette.Text, QColor(45, 52, 54))
        palette.setColor(QPalette.Button, QColor(255, 255, 255))
        palette.setColor(QPalette.ButtonText, QColor(45, 52, 54))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.Link, QColor(108, 99, 255))
        palette.setColor(QPalette.Highlight, QColor(108, 99, 255))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        widget.setPalette(palette)
        
    def _apply_dark_theme(self, widget):
        """Apply dark theme"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 46))
        palette.setColor(QPalette.WindowText, QColor(232, 232, 232))
        palette.setColor(QPalette.Base, QColor(20, 20, 34))
        palette.setColor(QPalette.AlternateBase, QColor(35, 35, 52))
        palette.setColor(QPalette.ToolTipBase, QColor(30, 30, 46))
        palette.setColor(QPalette.ToolTipText, QColor(232, 232, 232))
        palette.setColor(QPalette.Text, QColor(232, 232, 232))
        palette.setColor(QPalette.Button, QColor(45, 45, 68))
        palette.setColor(QPalette.ButtonText, QColor(232, 232, 232))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.Link, QColor(108, 99, 255))
        palette.setColor(QPalette.Highlight, QColor(108, 99, 255))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        widget.setPalette(palette)
        
    def get_color(self, name: str) -> str:
        """Get color by name"""
        colors = {
            # Light theme
            "bg": "#F5F6FA",
            "fg": "#2D3436",
            "accent": "#6C63FF",
            "secondary": "#FF6584",
            "success": "#00C9A7",
            "warning": "#FFC857",
            "card_bg": "#FFFFFF",
            "border": "#E8E8E8",
            
            # Dark theme (overrides)
            "bg_dark": "#1E1E2E",
            "fg_dark": "#E8E8E8",
            "card_bg_dark": "#2D2D44",
            "border_dark": "#3D3D5C"
        }
        
        if self.current_theme == "dark" and name in ["bg", "fg", "card_bg", "border"]:
            return colors.get(f"{name}_dark", colors.get(name, ""))
        return colors.get(name, "")