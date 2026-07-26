# app/gui/themes.py
"""
Theme Manager - Professional Clean Themes with Working Application
"""

from typing import Dict, List, Any
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor


class ThemeManager:
    """Complete theme management - Professional Clean"""
    
    THEMES = {
        # ===== PROFESSIONAL CLEAN =====
        "professional_blue": {
            "name": "Professional Blue",
            "primary": "#1E3A5F",
            "secondary": "#2E5A8A",
            "accent": "#3A7BD5",
            "bg": "#F0F4F8",
            "card_bg": "#FFFFFF",
            "text_primary": "#1A202C",
            "text_secondary": "#4A5568",
            "text_muted": "#A0AEC0",
            "success": "#38A169",
            "warning": "#D69E2E",
            "error": "#E53E3E",
            "border": "#E2E8F0",
            "hover": "#EDF2F7",
            "gradient": ["#1E3A5F", "#2E5A8A"],
            "font": "'Segoe UI', 'Helvetica Neue', sans-serif",
            "is_dark": False,
            "button_primary": "#2E5A8A",
            "button_primary_hover": "#1E3A5F",
            "button_secondary": "#EDF2F7",
            "button_secondary_hover": "#E2E8F0",
            "header_bg": "#1E3A5F",
            "header_text": "#FFFFFF",
        },
        
        "professional_slate": {
            "name": "Professional Slate",
            "primary": "#2D3748",
            "secondary": "#4A5568",
            "accent": "#718096",
            "bg": "#F7FAFC",
            "card_bg": "#FFFFFF",
            "text_primary": "#1A202C",
            "text_secondary": "#4A5568",
            "text_muted": "#A0AEC0",
            "success": "#38A169",
            "warning": "#D69E2E",
            "error": "#E53E3E",
            "border": "#E2E8F0",
            "hover": "#EDF2F7",
            "gradient": ["#2D3748", "#4A5568"],
            "font": "'Segoe UI', 'Helvetica Neue', sans-serif",
            "is_dark": False,
            "button_primary": "#4A5568",
            "button_primary_hover": "#2D3748",
            "button_secondary": "#EDF2F7",
            "button_secondary_hover": "#E2E8F0",
            "header_bg": "#2D3748",
            "header_text": "#FFFFFF",
        },
        
        "clean_teal": {
            "name": "Clean Teal",
            "primary": "#234E52",
            "secondary": "#2C7A7B",
            "accent": "#319795",
            "bg": "#F0F7F7",
            "card_bg": "#FFFFFF",
            "text_primary": "#1A202C",
            "text_secondary": "#4A5568",
            "text_muted": "#A0AEC0",
            "success": "#38A169",
            "warning": "#D69E2E",
            "error": "#E53E3E",
            "border": "#E2E8F0",
            "hover": "#EDF2F7",
            "gradient": ["#234E52", "#2C7A7B"],
            "font": "'Segoe UI', 'Helvetica Neue', sans-serif",
            "is_dark": False,
            "button_primary": "#2C7A7B",
            "button_primary_hover": "#234E52",
            "button_secondary": "#EDF2F7",
            "button_secondary_hover": "#E2E8F0",
            "header_bg": "#234E52",
            "header_text": "#FFFFFF",
        },
        
        "elegant_plum": {
            "name": "Elegant Plum",
            "primary": "#3C2A4D",
            "secondary": "#6B4C7A",
            "accent": "#8B6B9A",
            "bg": "#F8F5FA",
            "card_bg": "#FFFFFF",
            "text_primary": "#2D1A3D",
            "text_secondary": "#5A4A6A",
            "text_muted": "#A0AEC0",
            "success": "#38A169",
            "warning": "#D69E2E",
            "error": "#E53E3E",
            "border": "#E2E8F0",
            "hover": "#EDF2F7",
            "gradient": ["#3C2A4D", "#6B4C7A"],
            "font": "'Segoe UI', 'Helvetica Neue', sans-serif",
            "is_dark": False,
            "button_primary": "#6B4C7A",
            "button_primary_hover": "#3C2A4D",
            "button_secondary": "#EDF2F7",
            "button_secondary_hover": "#E2E8F0",
            "header_bg": "#3C2A4D",
            "header_text": "#FFFFFF",
        },
        
        "clean_white": {
            "name": "Clean White",
            "primary": "#2D3748",
            "secondary": "#4A5568",
            "accent": "#718096",
            "bg": "#F8F9FA",
            "card_bg": "#FFFFFF",
            "text_primary": "#1A202C",
            "text_secondary": "#4A5568",
            "text_muted": "#A0AEC0",
            "success": "#38A169",
            "warning": "#D69E2E",
            "error": "#E53E3E",
            "border": "#E8ECF0",
            "hover": "#F1F3F5",
            "gradient": ["#2D3748", "#4A5568"],
            "font": "'Segoe UI', 'Helvetica Neue', sans-serif",
            "is_dark": False,
            "button_primary": "#4A5568",
            "button_primary_hover": "#2D3748",
            "button_secondary": "#F1F3F5",
            "button_secondary_hover": "#E8ECF0",
            "header_bg": "#2D3748",
            "header_text": "#FFFFFF",
        },
        
        "soft_green": {
            "name": "Soft Green",
            "primary": "#276749",
            "secondary": "#38A169",
            "accent": "#48BB78",
            "bg": "#F5FAF7",
            "card_bg": "#FFFFFF",
            "text_primary": "#1A202C",
            "text_secondary": "#4A5568",
            "text_muted": "#A0AEC0",
            "success": "#38A169",
            "warning": "#D69E2E",
            "error": "#E53E3E",
            "border": "#E2E8F0",
            "hover": "#EDF2F7",
            "gradient": ["#276749", "#38A169"],
            "font": "'Segoe UI', 'Helvetica Neue', sans-serif",
            "is_dark": False,
            "button_primary": "#38A169",
            "button_primary_hover": "#276749",
            "button_secondary": "#EDF2F7",
            "button_secondary_hover": "#E2E8F0",
            "header_bg": "#276749",
            "header_text": "#FFFFFF",
        },
        
        "dark_pro": {
            "name": "Dark Pro",
            "primary": "#1A202C",
            "secondary": "#2D3748",
            "accent": "#4A5568",
            "bg": "#1A202C",
            "card_bg": "#2D3748",
            "text_primary": "#F7FAFC",
            "text_secondary": "#CBD5E0",
            "text_muted": "#718096",
            "success": "#48BB78",
            "warning": "#ECC94B",
            "error": "#FC8181",
            "border": "#4A5568",
            "hover": "#2D3748",
            "gradient": ["#1A202C", "#2D3748"],
            "font": "'Segoe UI', 'Helvetica Neue', sans-serif",
            "is_dark": True,
            "button_primary": "#4A5568",
            "button_primary_hover": "#718096",
            "button_secondary": "#2D3748",
            "button_secondary_hover": "#4A5568",
            "header_bg": "#0D1117",
            "header_text": "#FFFFFF",
        },
    }
    
    @classmethod
    def get_theme(cls, name: str) -> Dict:
        """Get theme by name"""
        return cls.THEMES.get(name, cls.THEMES["professional_blue"])
    
    @classmethod
    def get_all_themes(cls) -> List[str]:
        """Get all theme names"""
        return list(cls.THEMES.keys())
    
    @classmethod
    def get_theme_names_with_labels(cls) -> List[tuple]:
        """Get theme names with display labels"""
        return [
            ("Professional Blue", "professional_blue"),
            ("Professional Slate", "professional_slate"),
            ("Clean Teal", "clean_teal"),
            ("Elegant Plum", "elegant_plum"),
            ("Clean White", "clean_white"),
            ("Soft Green", "soft_green"),
            ("Dark Pro", "dark_pro"),
        ]
    
    @classmethod
    def get_stylesheet(cls, theme_name: str) -> str:
        """Get stylesheet for a theme"""
        theme = cls.get_theme(theme_name)
        c = theme
        
        return f"""
            /* ===== GLOBAL ===== */
            QWidget {{
                background-color: {c['bg']};
                color: {c['text_primary']};
                font-family: {c['font']};
                font-size: 13px;
            }}
            
            /* ===== MAIN WINDOW ===== */
            QMainWindow, QDialog {{
                background-color: {c['bg']};
            }}
            
            /* ===== HEADER ===== */
            QFrame[class="header"] {{
                background-color: {c['header_bg']};
                border-bottom: 2px solid {c['secondary']};
            }}
            
            QLabel[class="header-title"] {{
                font-size: 20px;
                font-weight: 600;
                color: {c['header_text']};
                font-family: {c['font']};
                letter-spacing: 0.3px;
            }}
            
            /* ===== LABELS ===== */
            QLabel {{
                color: {c['text_primary']};
                font-weight: 400;
            }}
            
            QLabel[class="status"] {{
                color: {c['text_secondary']};
                font-size: 12px;
            }}
            
            /* ===== BUTTONS ===== */
            QPushButton {{
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 13px;
                font-family: {c['font']};
            }}
            
            QPushButton[class="primary"] {{
                background-color: {c['button_primary']};
                color: #FFFFFF;
                border: none;
            }}
            QPushButton[class="primary"]:hover {{
                background-color: {c['button_primary_hover']};
            }}
            QPushButton[class="primary"]:pressed {{
                background-color: {c['button_primary_hover']};
            }}
            QPushButton[class="primary"]:disabled {{
                background-color: {c['text_muted']};
                color: {c['text_secondary']};
            }}
            
            QPushButton[class="secondary"] {{
                background-color: {c['button_secondary']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
            }}
            QPushButton[class="secondary"]:hover {{
                background-color: {c['button_secondary_hover']};
            }}
            
            QPushButton[class="danger"] {{
                background-color: {c['error']};
                color: #FFFFFF;
                border: none;
            }}
            QPushButton[class="danger"]:hover {{
                background-color: {c['error']}CC;
            }}
            
            QPushButton[class="icon-btn"] {{
                background-color: transparent;
                border: 1px solid {c['border']};
                border-radius: 6px;
                color: {c['text_secondary']};
                font-size: 18px;
                padding: 6px;
            }}
            QPushButton[class="icon-btn"]:hover {{
                background-color: {c['hover']};
                color: {c['text_primary']};
            }}
            
            /* ===== LINE EDIT ===== */
            QLineEdit {{
                background-color: {c['card_bg']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {c['text_primary']};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {c['accent']};
            }}
            QLineEdit::placeholder {{
                color: {c['text_muted']};
            }}
            
            /* ===== COMBO BOX ===== */
            QComboBox {{
                background-color: {c['card_bg']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 6px 10px;
                color: {c['text_primary']};
                font-size: 12px;
                min-width: 100px;
            }}
            QComboBox:focus {{
                border-color: {c['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {c['text_secondary']};
                margin-right: 4px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {c['card_bg']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 4px;
                selection-background-color: {c['secondary']};
                selection-color: #FFFFFF;
            }}
            
            /* ===== LIST WIDGET ===== */
            QListWidget {{
                background-color: {c['card_bg']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 4px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 4px;
                color: {c['text_primary']};
                font-size: 13px;
            }}
            QListWidget::item:hover {{
                background-color: {c['hover']};
            }}
            QListWidget::item:selected {{
                background-color: {c['secondary']};
                color: #FFFFFF;
            }}
            
            /* ===== PROGRESS BAR ===== */
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: {c['border']};
                height: 6px;
            }}
            QProgressBar::chunk {{
                background-color: {c['secondary']};
                border-radius: 4px;
            }}
            
            /* ===== GROUP BOX ===== */
            QGroupBox {{
                border: 1px solid {c['border']};
                border-radius: 8px;
                padding-top: 12px;
                margin-top: 8px;
                color: {c['text_primary']};
                font-weight: 600;
                font-size: 13px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: {c['text_primary']};
                background: {c['bg']};
            }}
            
            /* ===== CHECK BOX ===== */
            QCheckBox {{
                color: {c['text_primary']};
                font-size: 12px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {c['border']};
                background-color: {c['card_bg']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {c['secondary']};
                border-color: {c['secondary']};
            }}
            
            /* ===== DROP ZONE ===== */
            QWidget[class="drop-zone"] {{
                background-color: {c['card_bg']};
                border: 2px dashed {c['border']};
                border-radius: 8px;
            }}
            QWidget[class="drop-zone"]:hover {{
                border-color: {c['secondary']};
                background-color: {c['hover']};
            }}
            
            /* ===== MENU ===== */
            QMenu {{
                background-color: {c['card_bg']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 4px;
                color: {c['text_primary']};
            }}
            QMenu::item {{
                padding: 6px 24px 6px 20px;
                border-radius: 4px;
                color: {c['text_primary']};
            }}
            QMenu::item:selected {{
                background-color: {c['secondary']};
                color: #FFFFFF;
            }}
            
            /* ===== TEXT EDIT ===== */
            QTextEdit {{
                background-color: {c['card_bg']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 10px;
                color: {c['text_primary']};
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border-color: {c['accent']};
            }}
            
            /* ===== SCROLL BAR ===== */
            QScrollBar:vertical {{
                background: {c['bg']};
                border: none;
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {c['border']};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {c['text_muted']};
            }}
            
            QScrollBar:horizontal {{
                background: {c['bg']};
                border: none;
                height: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal {{
                background: {c['border']};
                border-radius: 4px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {c['text_muted']};
            }}
            
            /* ===== STATS CARD ===== */
            QFrame[class="stats-card"] {{
                background-color: {c['card_bg']};
                border-radius: 8px;
                border: 1px solid {c['border']};
                padding: 12px;
            }}
            
            /* ===== CARD ===== */
            QFrame[class="card"] {{
                background-color: {c['card_bg']};
                border-radius: 8px;
                border: 1px solid {c['border']};
            }}
            
            /* ===== STATUS BAR ===== */
            QStatusBar {{
                background-color: {c['card_bg']};
                color: {c['text_secondary']};
                border-top: 1px solid {c['border']};
                padding: 4px 16px;
            }}
            
            /* ===== TOOLTIP ===== */
            QToolTip {{
                background-color: {c['primary']};
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
            }}
            
            /* ===== SPLASH SCREEN ===== */
            QSplashScreen {{
                background-color: {c['primary']};
            }}
        """
    
    @classmethod
    def apply_theme(cls, theme_name: str):
        """Apply theme to the entire application"""
        theme = cls.get_theme(theme_name)
        stylesheet = cls.get_stylesheet(theme_name)
        app = QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)
            # Also set palette for system colors
            palette = app.palette()
            if theme['is_dark']:
                palette.setColor(QPalette.Window, QColor(theme['bg']))
                palette.setColor(QPalette.WindowText, QColor(theme['text_primary']))
                palette.setColor(QPalette.Base, QColor(theme['card_bg']))
                palette.setColor(QPalette.Text, QColor(theme['text_primary']))
                palette.setColor(QPalette.Button, QColor(theme['card_bg']))
                palette.setColor(QPalette.ButtonText, QColor(theme['text_primary']))
            else:
                palette.setColor(QPalette.Window, QColor(theme['bg']))
                palette.setColor(QPalette.WindowText, QColor(theme['text_primary']))
                palette.setColor(QPalette.Base, QColor(theme['card_bg']))
                palette.setColor(QPalette.Text, QColor(theme['text_primary']))
                palette.setColor(QPalette.Button, QColor(theme['card_bg']))
                palette.setColor(QPalette.ButtonText, QColor(theme['text_primary']))
            app.setPalette(palette)
        return theme
    
    @classmethod
    def get_professional_colors(cls) -> Dict:
        """Get professional color palette"""
        return {
            "primary": "#1E3A5F",
            "secondary": "#2E5A8A",
            "accent": "#3A7BD5",
            "success": "#38A169",
            "warning": "#D69E2E",
            "error": "#E53E3E",
            "background": "#F0F4F8",
            "card": "#FFFFFF",
            "text": "#1A202C",
            "text_secondary": "#4A5568",
            "border": "#E2E8F0",
        }


# Create a singleton instance
Theme = ThemeManager