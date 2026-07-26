# app/core/history.py
"""
History Manager - Simple and Fast
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import threading

from app.utils.logger import get_logger

logger = get_logger(__name__)


class HistoryManager:
    """Manage conversion history - Fast and simple"""
    
    def __init__(self):
        self.history_file = Path("data/history.json")
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.entries = []
        self.lock = threading.Lock()
        # Load with error handling
        try:
            self.load()
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            self.entries = []
    
    def load(self):
        """Load history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.entries = json.loads(content)
                    else:
                        self.entries = []
                logger.info(f"Loaded {len(self.entries)} history entries")
            else:
                self.entries = []
                # Create empty file
                self.save()
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            self.entries = []
    
    def save(self):
        """Save history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Failed to save history: {e}")
            return False
    
    def add_entry(self, input_file: str, output_file: str, format: str, 
                  success: bool, error: str = None) -> Dict:
        """Add a new history entry"""
        entry = {
            "input": input_file,
            "output": output_file,
            "format": format,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "error": error
        }
        
        with self.lock:
            self.entries.append(entry)
            if len(self.entries) > 1000:
                self.entries = self.entries[-1000:]
            self.save()
        
        logger.info(f"Added history entry: {Path(input_file).name} -> {format.upper()}")
        return entry
    
    def get_all(self) -> List[Dict]:
        """Get all history entries"""
        with self.lock:
            return self.entries.copy()
    
    def get_stats(self) -> Dict:
        """Get history statistics"""
        with self.lock:
            total = len(self.entries)
            successful = sum(1 for e in self.entries if e.get("success", False))
            failed = total - successful
            
            return {
                "total": total,
                "successful": successful,
                "failed": failed,
                "success_rate": f"{int((successful / total) * 100) if total > 0 else 0}%"
            }
    
    def clear(self):
        """Clear all history"""
        with self.lock:
            self.entries = []
            self.save()


# Singleton instance
history_manager = HistoryManager()