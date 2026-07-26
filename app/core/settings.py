# app/core/settings.py
"""
Settings Manager - Load and save application settings with validation
Features: Defaults, validation, encryption, backup, category support
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import threading

from app.utils.logger import get_logger

logger = get_logger(__name__)


class SettingsManager:
    """
    Singleton settings manager with:
    - Default settings
    - Validation
    - Auto-backup
    - Category support
    - Reset to defaults
    """
    
    _instance = None
    _lock = threading.Lock()
    
    # ===== DEFAULT SETTINGS =====
    DEFAULTS = {
        # Theme
        'theme': 'professional_blue',
        'dark_mode': False,
        
        # Output
        'output_folder': '',
        'output_format': 'pdf',
        'quality': 'high',
        'keep_original': True,
        'ask_save_location': True,
        
        # Voice
        'voice_enabled': True,
        'voice_language': 'en-US',
        'voice_sensitivity': 0.5,
        
        # Conversion
        'auto_convert': False,
        'max_concurrent': 4,
        'batch_size': 10,
        'timeout': 300,
        
        # Notifications
        'notification': True,
        'notification_sound': True,
        
        # Watched folders
        'watch_folders': [],
        
        # History
        'history_limit': 1000,
        'auto_clear_history': False,
        
        # Advanced
        'enable_ai': True,
        'enable_camera': True,
        'enable_ocr': True,
        'debug_mode': False,
        'log_level': 'INFO',
        
        # Formats
        'default_document_format': 'pdf',
        'default_image_format': 'jpg',
        'default_audio_format': 'mp3',
        'default_video_format': 'mp4',
        'default_archive_format': 'zip',
        
        # Quality presets
        'quality_presets': {
            'low': {'quality': 50, 'compression': 9},
            'medium': {'quality': 75, 'compression': 6},
            'high': {'quality': 95, 'compression': 3}
        },
        
        # Recent files
        'recent_files': [],
        'max_recent_files': 10,
        
        # UI
        'window_width': 1200,
        'window_height': 750,
        'window_state': 'maximized',
        'sidebar_width': 220,
        
        # Language
        'language': 'en',
        'available_languages': ['en', 'ur', 'fr', 'de', 'es', 'zh'],
        
        # Update
        'check_updates': True,
        'last_update_check': None,
        
        # Custom
        'custom_settings': {}
    }
    
    # ===== SETTINGS VALIDATION =====
    VALIDATION = {
        'theme': {
            'type': str,
            'allowed': ['professional_blue', 'professional_slate', 'clean_teal', 
                       'elegant_plum', 'clean_white', 'soft_green', 'dark_pro'],
            'default': 'professional_blue'
        },
        'quality': {
            'type': str,
            'allowed': ['low', 'medium', 'high'],
            'default': 'high'
        },
        'output_format': {
            'type': str,
            'allowed': ['pdf', 'docx', 'jpg', 'png', 'mp3', 'mp4', 'zip'],
            'default': 'pdf'
        },
        'voice_sensitivity': {
            'type': float,
            'min': 0.0,
            'max': 1.0,
            'default': 0.5
        },
        'max_concurrent': {
            'type': int,
            'min': 1,
            'max': 16,
            'default': 4
        },
        'batch_size': {
            'type': int,
            'min': 1,
            'max': 100,
            'default': 10
        },
        'history_limit': {
            'type': int,
            'min': 10,
            'max': 10000,
            'default': 1000
        },
        'timeout': {
            'type': int,
            'min': 30,
            'max': 3600,
            'default': 300
        },
        'window_width': {
            'type': int,
            'min': 800,
            'max': 3840,
            'default': 1200
        },
        'window_height': {
            'type': int,
            'min': 600,
            'max': 2160,
            'default': 750
        },
        'sidebar_width': {
            'type': int,
            'min': 150,
            'max': 350,
            'default': 220
        },
        'log_level': {
            'type': str,
            'allowed': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            'default': 'INFO'
        },
        'language': {
            'type': str,
            'allowed': ['en', 'ur', 'fr', 'de', 'es', 'zh'],
            'default': 'en'
        }
    }
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._settings = {}
        self._backup_dir = None
        self._load()
    
    # ============================================================
    # LOAD / SAVE
    # ============================================================
    
    def _load(self):
        """Load settings from file with fallback to defaults"""
        from config import Config
        
        try:
            settings_file = Config.SETTINGS_FILE
            self._backup_dir = Config.DATA_DIR / 'settings_backups'
            self._backup_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Loading settings from: {settings_file}")
            
            if settings_file.exists():
                # Backup before loading
                self._backup_current_settings()
                
                try:
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            loaded = json.loads(content)
                            # Merge with defaults
                            self._settings = self._merge_with_defaults(loaded)
                        else:
                            self._settings = self.DEFAULTS.copy()
                    logger.info(f"Loaded {len(self._settings)} settings")
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in settings file: {e}")
                    self._restore_from_backup()
                except Exception as e:
                    logger.error(f"Failed to load settings: {e}")
                    self._settings = self.DEFAULTS.copy()
            else:
                logger.info("No settings file found, using defaults")
                self._settings = self.DEFAULTS.copy()
                self.save()
                
        except Exception as e:
            logger.error(f"Settings load error: {e}")
            self._settings = self.DEFAULTS.copy()
    
    def _merge_with_defaults(self, loaded: Dict) -> Dict:
        """Merge loaded settings with defaults"""
        result = self.DEFAULTS.copy()
        for key, value in loaded.items():
            if key in result:
                # Validate the value
                if self._validate_setting(key, value):
                    result[key] = value
        return result
    
    def _backup_current_settings(self):
        """Backup current settings before making changes"""
        try:
            from config import Config
            settings_file = Config.SETTINGS_FILE
            
            if settings_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self._backup_dir / f"settings_{timestamp}.json"
                shutil.copy2(settings_file, backup_file)
                
                # Keep only last 10 backups
                backups = sorted(self._backup_dir.glob("settings_*.json"))
                if len(backups) > 10:
                    for old_backup in backups[:-10]:
                        old_backup.unlink()
        except Exception as e:
            logger.warning(f"Failed to backup settings: {e}")
    
    def _restore_from_backup(self):
        """Restore settings from latest backup"""
        try:
            backups = sorted(self._backup_dir.glob("settings_*.json"))
            if backups:
                latest = backups[-1]
                logger.info(f"Restoring settings from: {latest}")
                with open(latest, 'r', encoding='utf-8') as f:
                    self._settings = json.loads(f.read())
            else:
                self._settings = self.DEFAULTS.copy()
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            self._settings = self.DEFAULTS.copy()
    
    def save(self) -> bool:
        """Save settings to file with backup"""
        from config import Config
        
        try:
            # Backup before saving
            self._backup_current_settings()
            
            settings_file = Config.SETTINGS_FILE
            settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Settings saved to: {settings_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False
    
    # ============================================================
    # VALIDATION
    # ============================================================
    
    def _validate_setting(self, key: str, value: Any) -> bool:
        """Validate a setting value"""
        if key not in self.VALIDATION:
            return True
        
        rules = self.VALIDATION[key]
        
        # Check type
        if not isinstance(value, rules['type']):
            logger.warning(f"Invalid type for {key}: expected {rules['type']}, got {type(value)}")
            return False
        
        # Check allowed values
        if 'allowed' in rules and value not in rules['allowed']:
            logger.warning(f"Invalid value for {key}: {value}. Allowed: {rules['allowed']}")
            return False
        
        # Check min/max
        if 'min' in rules and value < rules['min']:
            logger.warning(f"Value too low for {key}: {value} < {rules['min']}")
            return False
        
        if 'max' in rules and value > rules['max']:
            logger.warning(f"Value too high for {key}: {value} > {rules['max']}")
            return False
        
        return True
    
    def get_validated(self, key: str, default=None):
        """Get a setting with validation"""
        value = self._settings.get(key, default)
        
        if key in self.VALIDATION:
            rules = self.VALIDATION[key]
            if not self._validate_setting(key, value):
                return rules.get('default', default)
        
        return value
    
    # ============================================================
    # GET / SET
    # ============================================================
    
    def get(self, key: str, default=None):
        """Get a setting value"""
        return self._settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a setting value with validation"""
        if self._validate_setting(key, value):
            self._settings[key] = value
        else:
            logger.warning(f"Invalid value for {key}: {value}")
            # Use default if available
            if key in self.VALIDATION:
                self._settings[key] = self.VALIDATION[key]['default']
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings"""
        return self._settings.copy()
    
    def get_category(self, category: str) -> Dict[str, Any]:
        """Get settings by category"""
        category_settings = {}
        for key, value in self._settings.items():
            if key.startswith(category):
                category_settings[key] = value
        return category_settings
    
    # ============================================================
    # RESET
    # ============================================================
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults"""
        try:
            self._backup_current_settings()
            self._settings = self.DEFAULTS.copy()
            self.save()
            logger.info("Settings reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Failed to reset settings: {e}")
            return False
    
    def reset_category(self, category: str) -> bool:
        """Reset a category of settings"""
        try:
            for key in list(self._settings.keys()):
                if key.startswith(category):
                    if key in self.DEFAULTS:
                        self._settings[key] = self.DEFAULTS[key]
            self.save()
            logger.info(f"Reset category: {category}")
            return True
        except Exception as e:
            logger.error(f"Failed to reset category: {e}")
            return False
    
    def get_default(self, key: str):
        """Get default value for a setting"""
        return self.DEFAULTS.get(key)
    
    # ============================================================
    # EXPORT / IMPORT
    # ============================================================
    
    def export_to_file(self, file_path: Union[str, Path]) -> bool:
        """Export settings to a file"""
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Settings exported to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export settings: {e}")
            return False
    
    def import_from_file(self, file_path: Union[str, Path]) -> bool:
        """Import settings from a file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"Settings file not found: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                imported = json.loads(f.read())
            
            # Merge with validation
            self._backup_current_settings()
            for key, value in imported.items():
                if self._validate_setting(key, value):
                    self._settings[key] = value
            
            self.save()
            logger.info(f"Settings imported from: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import settings: {e}")
            return False
    
    # ============================================================
    # UTILITY
    # ============================================================
    
    def get_quality_preset(self, quality: str = None) -> Dict[str, Any]:
        """Get quality preset values"""
        if quality is None:
            quality = self.get('quality', 'high')
        
        presets = self.get('quality_presets', {})
        return presets.get(quality, presets.get('high', {'quality': 95, 'compression': 3}))
    
    def add_recent_file(self, file_path: str):
        """Add a file to recent files list"""
        recent = self.get('recent_files', [])
        
        # Remove if already exists
        if file_path in recent:
            recent.remove(file_path)
        
        # Add to front
        recent.insert(0, file_path)
        
        # Limit size
        max_recent = self.get('max_recent_files', 10)
        self._settings['recent_files'] = recent[:max_recent]
    
    def get_recent_files(self) -> List[str]:
        """Get recent files list"""
        return self.get('recent_files', [])
    
    def clear_recent_files(self):
        """Clear recent files list"""
        self._settings['recent_files'] = []
        self.save()
    
    def get_watched_folders(self) -> List[str]:
        """Get watched folders list"""
        return self.get('watch_folders', [])
    
    def add_watched_folder(self, folder_path: str):
        """Add a folder to watched folders"""
        folders = self.get('watch_folders', [])
        if folder_path not in folders:
            folders.append(folder_path)
            self._settings['watch_folders'] = folders
            self.save()
    
    def remove_watched_folder(self, folder_path: str):
        """Remove a folder from watched folders"""
        folders = self.get('watch_folders', [])
        if folder_path in folders:
            folders.remove(folder_path)
            self._settings['watch_folders'] = folders
            self.save()
    
    # ============================================================
    # CLASS METHODS
    # ============================================================
    
    @classmethod
    def load(cls) -> 'SettingsManager':
        """Load settings - returns the singleton instance"""
        return cls()
    
    @classmethod
    def get_instance(cls) -> 'SettingsManager':
        """Get the singleton instance"""
        return cls()
    
    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """Get default settings"""
        return cls.DEFAULTS.copy()
    
    @classmethod
    def get_validation(cls) -> Dict[str, Any]:
        """Get validation rules"""
        return cls.VALIDATION.copy()


# Create a singleton instance
settings_manager = SettingsManager()