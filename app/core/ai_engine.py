# app/core/ai_engine.py
"""
ULTRA-INTELLIGENT AI ENGINE - Advanced Natural Language Processing
Features: NLP, Sentiment Analysis, Smart Suggestions, Context Memory, Learning
"""

import re
import logging
import os
import subprocess
import random
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class AIEngine:
    """
    Ultra-Intelligent AI Assistant with NLP and Context Awareness
    """
    
    # ============================================================
    # INITIALIZATION
    # ============================================================
    
    def __init__(self):
        self.loaded = True
        self.loading = False
        self.model_name = "Ultra-Intelligent Assistant v3.0"
        self.converter = None
        
        # Advanced Context Memory
        self.context = {
            'conversation_history': [],
            'user_preferences': {},
            'file_context': [],
            'last_intent': None,
            'last_entities': {},
            'session_start': datetime.now(),
            'interaction_count': 0,
            'user_name': None,
            'favorite_formats': [],
            'recent_actions': [],
            'learning_data': {}
        }
        
        # Sentiment Analysis
        self.sentiment_keywords = {
            'positive': ['good', 'great', 'excellent', 'amazing', 'awesome', 'love', 'perfect', 'nice'],
            'negative': ['bad', 'terrible', 'awful', 'horrible', 'hate', 'disappointed', 'worst'],
            'frustration': ['slow', 'stuck', 'confused', 'help', 'struggling', 'problem']
        }
        
        # Intent Categories
        self.intents = {
            'greeting': ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good evening', 'howdy'],
            'farewell': ['bye', 'goodbye', 'see you', 'later', 'farewell', 'take care'],
            'conversion': ['convert', 'change', 'transform', 'make', 'turn into', 'to'],
            'extract': ['extract', 'get', 'pull', 'retrieve', 'take out'],
            'compress': ['compress', 'zip', 'archive', 'pack', 'reduce size'],
            'extract_text': ['ocr', 'read text', 'text from image', 'scan text'],
            'resize': ['resize', 'scale', 'change size', 'make smaller', 'make larger'],
            'rotate': ['rotate', 'flip', 'turn', 'mirror'],
            'quality': ['quality', 'resolution', 'bitrate', 'compression'],
            'format_info': ['what is', 'tell me about', 'explain', 'format', 'type'],
            'batch': ['batch', 'multiple', 'all files', 'every file', 'bulk'],
            'status': ['status', 'info', 'how many', 'progress', 'current'],
            'history': ['history', 'previous', 'past', 'recent', 'last'],
            'clear': ['clear', 'remove', 'delete', 'erase', 'wipe'],
            'open': ['open', 'navigate', 'go to', 'show', 'browse'],
            'save': ['save', 'store', 'keep', 'export', 'download'],
            'settings': ['settings', 'preferences', 'options', 'config'],
            'theme': ['theme', 'dark mode', 'light mode', 'appearance', 'color'],
            'help': ['help', 'assist', 'support', 'guide', 'what can you do'],
            'suggestion': ['suggest', 'recommend', 'advise', 'idea'],
            'analytics': ['stats', 'statistics', 'analytics', 'report', 'summary'],
            'files': ['files', 'documents', 'folders', 'items'],
            'search': ['search', 'find', 'look for', 'locate'],
            'rename': ['rename', 'name', 'title'],
            'move': ['move', 'copy', 'duplicate', 'transfer'],
            'cancel': ['cancel', 'stop', 'abort', 'quit'],
        }
        
        # Entity Extraction Patterns
        self.entity_patterns = {
            'file_extension': r'\.([a-zA-Z0-9]+)\b',
            'number': r'\b(\d+)\b',
            'format': r'\b(pdf|docx|doc|txt|jpg|jpeg|png|gif|mp3|wav|mp4|avi|zip|rar|epub|mobi|csv|xlsx|pptx|json|xml|html)\b',
            'folder': r'\b(documents|downloads|desktop|pictures|videos|music)\b',
            'size': r'\b(\d+)\s*(kb|mb|gb|tb)\b',
            'time': r'\b(\d{1,2}):(\d{2})\b',
            'percentage': r'\b(\d+)%\b',
        }
        
        # Format Aliases with Descriptions
        self.format_knowledge = {
            'pdf': {
                'name': 'PDF',
                'full_name': 'Portable Document Format',
                'description': 'Universal document format that preserves formatting across platforms',
                'best_for': 'Documents, forms, official papers',
                'aliases': ['pdf', 'adobe', 'portable document']
            },
            'docx': {
                'name': 'DOCX',
                'full_name': 'Microsoft Word Document',
                'description': 'Standard word processing format for editable documents',
                'best_for': 'Editables documents, reports, letters',
                'aliases': ['word', 'document', 'doc']
            },
            'jpg': {
                'name': 'JPG',
                'full_name': 'Joint Photographic Experts Group',
                'description': 'Lossy image format with excellent compression for photographs',
                'best_for': 'Photos, images for web, social media',
                'aliases': ['jpg', 'jpeg', 'photo', 'image']
            },
            'png': {
                'name': 'PNG',
                'full_name': 'Portable Network Graphics',
                'description': 'Lossless image format with transparency support',
                'best_for': 'Graphics, logos, images with transparency',
                'aliases': ['png', 'transparent']
            },
            'mp3': {
                'name': 'MP3',
                'full_name': 'MPEG Audio Layer III',
                'description': 'Popular audio format with good quality-to-size ratio',
                'best_for': 'Music, podcasts, audio files',
                'aliases': ['mp3', 'audio', 'music']
            },
            'mp4': {
                'name': 'MP4',
                'full_name': 'MPEG-4 Part 14',
                'description': 'Universal video format compatible with most devices',
                'best_for': 'Videos, movies, sharing online',
                'aliases': ['mp4', 'video', 'movie']
            },
            'zip': {
                'name': 'ZIP',
                'full_name': 'ZIP Archive',
                'description': 'Standard archive format for file compression',
                'best_for': 'Compressing multiple files, sharing groups of files',
                'aliases': ['zip', 'archive', 'compress']
            },
            'epub': {
                'name': 'EPUB',
                'full_name': 'Electronic Publication',
                'description': 'Open ebook format for reflowable content',
                'best_for': 'Ebooks, digital publications, reading on devices',
                'aliases': ['epub', 'ebook', 'book']
            }
        }
        
        # Smart Suggestions
        self.suggestions = {
            'conversion': [
                "I can convert your files to PDF for better sharing.",
                "Consider converting images to JPG for smaller file sizes.",
                "For high-quality images, PNG format is a good choice.",
                "MP3 format is perfect for audio files you want to share.",
                "Archive your files with ZIP to save space and organize."
            ],
            'optimization': [
                "Compress your images to reduce file size without losing quality.",
                "Use high quality for important documents, medium for everyday use.",
                "Batch conversion can save time when processing multiple files."
            ],
            'useful': [
                "Use OCR to extract text from scanned documents.",
                "Camera scanning lets you digitize paper documents.",
                "History tracks all your conversions - you can review them anytime.",
                "Try different themes to customize your experience."
            ]
        }
        
        # Learning Data (persistent)
        self._load_learning_data()
        
        logger.info("🧠 Ultra-Intelligent AI Assistant v3.0 initialized")
        logger.info(f"📊 Intents: {len(self.intents)} | Entity patterns: {len(self.entity_patterns)}")
    
    # ============================================================
    # MAIN PROCESSOR
    # ============================================================
    
    def process_request(self, query: str, dashboard=None) -> str:
        """Process user query with advanced NLP"""
        if not query or not query.strip():
            return self._get_random_response('empty')
        
        query = query.strip()
        self.context['interaction_count'] += 1
        self.context['last_query'] = query
        
        # Update learning data
        self._update_learning(query)
        
        # ===== STEP 1: Sentiment Analysis =====
        sentiment = self._analyze_sentiment(query)
        
        # ===== STEP 2: Intent Detection =====
        intent, confidence = self._detect_intent(query)
        self.context['last_intent'] = intent
        
        # ===== STEP 3: Entity Extraction =====
        entities = self._extract_entities(query)
        self.context['last_entities'] = entities
        
        # ===== STEP 4: Context Awareness =====
        context_info = self._get_context_info()
        
        # ===== STEP 5: Generate Response =====
        
        # Handle negative sentiment with empathy
        if sentiment == 'negative':
            return self._handle_negative_sentiment(query)
        
        if sentiment == 'frustration':
            return self._handle_frustration(query)
        
        # Process by intent
        if intent == 'greeting':
            return self._handle_greeting(query, context_info)
        
        if intent == 'farewell':
            return self._handle_farewell()
        
        if intent == 'help':
            return self._handle_help(entities)
        
        if intent == 'conversion':
            return self._handle_conversion(query, entities, dashboard)
        
        if intent == 'format_info':
            return self._handle_format_info(entities)
        
        if intent == 'extract_text':
            return self._handle_ocr(dashboard)
        
        if intent == 'compress':
            return self._handle_compress(entities, dashboard)
        
        if intent == 'resize':
            return self._handle_resize(entities, dashboard)
        
        if intent == 'quality':
            return self._handle_quality(entities, dashboard)
        
        if intent == 'status':
            return self._handle_status(dashboard)
        
        if intent == 'history':
            return self._handle_history()
        
        if intent == 'clear':
            return self._handle_clear(dashboard)
        
        if intent == 'open':
            return self._handle_open(entities)
        
        if intent == 'theme':
            return self._handle_theme(entities, dashboard)
        
        if intent == 'suggestion':
            return self._handle_suggestion(query, dashboard)
        
        if intent == 'analytics':
            return self._handle_analytics(dashboard)
        
        if intent == 'search':
            return self._handle_search(entities, dashboard)
        
        if intent == 'save':
            return self._handle_save(entities, dashboard)
        
        if intent == 'batch':
            return self._handle_batch(dashboard)
        
        if intent == 'cancel':
            return self._handle_cancel(dashboard)
        
        if intent == 'settings':
            return self._handle_settings(entities, dashboard)
        
        if intent == 'rename':
            return self._handle_rename(entities, dashboard)
        
        if intent == 'move':
            return self._handle_move(entities, dashboard)
        
        # ===== STEP 6: Smart Fallback =====
        return self._handle_smart_fallback(query, entities, dashboard)
    
    # ============================================================
    # SENTIMENT ANALYSIS
    # ============================================================
    
    def _analyze_sentiment(self, query: str) -> str:
        """Analyze sentiment of user query"""
        q = query.lower()
        
        # Check for frustration
        for word in self.sentiment_keywords['frustration']:
            if word in q:
                return 'frustration'
        
        # Check for negative
        for word in self.sentiment_keywords['negative']:
            if word in q:
                return 'negative'
        
        # Check for positive
        for word in self.sentiment_keywords['positive']:
            if word in q:
                return 'positive'
        
        return 'neutral'
    
    def _handle_negative_sentiment(self, query: str) -> str:
        """Handle negative sentiment with empathy"""
        empathetic = [
            "I understand this can be frustrating. Let me help you resolve this.",
            "I'm sorry to hear that. Let's work together to fix this issue.",
            "I understand your concern. Let me find a solution for you."
        ]
        return random.choice(empathetic) + "\n\n" + self._handle_smart_fallback(query, {}, None)
    
    def _handle_frustration(self, query: str) -> str:
        """Handle frustration with patience"""
        helpful = [
            "I hear you. Let me simplify this for you.",
            "I understand this is challenging. Let me break it down step by step.",
            "Don't worry, I'm here to help. Let's tackle this together."
        ]
        return random.choice(helpful) + "\n\n" + self._handle_help({})
    
    # ============================================================
    # INTENT DETECTION
    # ============================================================
    
    def _detect_intent(self, query: str) -> Tuple[str, float]:
        """Detect intent with confidence score"""
        q = query.lower()
        
        # Check each intent
        for intent, keywords in self.intents.items():
            for keyword in keywords:
                if keyword in q:
                    # Check context for confirmation
                    if self.context.get('awaiting_confirmation') == intent and 'confirm' in q:
                        return intent, 0.95
                    return intent, 0.85
        
        # Multi-intent detection
        intents_found = []
        for intent, keywords in self.intents.items():
            for keyword in keywords:
                if keyword in q:
                    intents_found.append(intent)
                    break
        
        if len(intents_found) > 1:
            # Priority: conversion > format_info > help > others
            priority = ['conversion', 'format_info', 'help', 'status', 'history']
            for p in priority:
                if p in intents_found:
                    return p, 0.75
        
        # Check if contains format name
        for fmt in self.format_knowledge:
            if fmt in q:
                if 'convert' in q or 'to' in q:
                    return 'conversion', 0.70
                return 'format_info', 0.65
        
        return 'unknown', 0.3
    
    # ============================================================
    # ENTITY EXTRACTION
    # ============================================================
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract entities from query"""
        entities = {}
        
        # Extract file extensions
        ext_match = re.search(self.entity_patterns['file_extension'], query)
        if ext_match:
            entities['extension'] = ext_match.group(1)
        
        # Extract numbers
        num_matches = re.findall(self.entity_patterns['number'], query)
        if num_matches:
            entities['numbers'] = [int(n) for n in num_matches]
        
        # Extract formats
        fmt_matches = re.findall(self.entity_patterns['format'], query)
        if fmt_matches:
            entities['formats'] = list(set(fmt_matches))
        
        # Extract folders
        folder_matches = re.findall(self.entity_patterns['folder'], query)
        if folder_matches:
            entities['folders'] = folder_matches
        
        # Extract size
        size_match = re.search(self.entity_patterns['size'], query)
        if size_match:
            entities['size'] = {
                'value': int(size_match.group(1)),
                'unit': size_match.group(2)
            }
        
        return entities
    
    # ============================================================
    # HANDLERS
    # ============================================================
    
    def _handle_greeting(self, query: str, context: dict) -> str:
        """Handle greeting with personalization"""
        name = self.context.get('user_name')
        
        if name:
            greeting = f"Welcome back, {name}! 👋 "
        else:
            greeting = "Hello! 👋 "
        
        time_of_day = self._get_time_of_day()
        greeting += f"Good {time_of_day}! "
        
        # Personalize based on context
        if self.context['interaction_count'] > 1:
            greeting += f"This is our {self.context['interaction_count']}th interaction. "
        
        # Check if user has files
        if context.get('file_count', 0) > 0:
            greeting += f"You have {context['file_count']} file(s) ready. Want to convert them?"
        else:
            greeting += "How can I help you with your files today?"
        
        # Ask for name if first time
        if not name and self.context['interaction_count'] == 1:
            greeting += "\n\nBy the way, what's your name? (I'll remember it!)"
        
        return greeting
    
    def _handle_farewell(self) -> str:
        """Handle farewell"""
        farewells = [
            "Goodbye! 👋 Have a great day!",
            "See you later! 😊 Come back anytime you need file conversion.",
            "Take care! 🚀 I'm always here when you need me.",
            "Until next time! 💫 Happy file converting!",
            "Bye for now! 👋 Remember, I'm just a conversation away."
        ]
        return random.choice(farewells)
    
    def _handle_help(self, entities: dict) -> str:
        """Handle help requests with smart suggestions"""
        help_text = "🤖 **AI Assistant - Complete Help**\n\n"
        
        # Check if asking for specific help
        if 'formats' in str(entities):
            help_text += self._get_supported_formats()
            return help_text
        
        help_text += """**📁 File Operations**
  • "Open Documents" - Opens Documents folder
  • "Pick report.pdf" - Finds and adds file
  • "Show history" - Shows recent conversions

**🔄 Conversion**
  • "Convert to PDF" - Quick conversion
  • "Convert all to MP4" - Batch conversion
  • "Compress files" - Archive your files

**📷 Advanced Features**
  • "Scan with camera" - Document scanner
  • "OCR this image" - Extract text from image
  • "Resize to 800x600" - Resize images

**🎨 Customization**
  • "Change to Dark theme" - Theme switch
  • "High quality" - Quality settings
  • "Check status" - Current state

**💡 Smart Suggestions**
  • "Suggest something" - Get recommendations
  • "What should I do?" - Smart advice

**📊 Analytics**
  • "Show stats" - Conversion statistics
  • "How many files?" - File count

**❓ Need more help?**
  • Ask "What formats are supported?"
  • Ask "Tell me about PDF"
  • Ask "What can you do?" """
        
        return help_text
    
    def _handle_conversion(self, query: str, entities: dict, dashboard=None) -> str:
        """Handle conversion commands with smart suggestions"""
        formats = entities.get('formats', [])
        
        if not formats:
            # Try to detect format from query
            for fmt in self.format_knowledge:
                if fmt in query.lower():
                    formats.append(fmt)
            
            if not formats:
                return "📤 I didn't catch the format. Try: 'Convert to PDF' or 'Convert to MP3'"
        
        target_format = formats[0]
        
        # Check if format is supported
        if target_format not in self.format_knowledge:
            return f"⚠️ '{target_format}' is not supported. Try: PDF, DOCX, JPG, PNG, MP3, MP4, ZIP"
        
        # Check if dashboard is available
        if not dashboard or not hasattr(dashboard, 'quick_convert'):
            return f"🔄 Ready to convert to {target_format.upper()}! Click the convert button."
        
        # Check if files are present
        file_count = len(dashboard.current_files) if hasattr(dashboard, 'current_files') else 0
        
        if file_count == 0:
            suggestion = "Add some files first! You can drag and drop, or say 'Pick report.pdf'"
            return f"🔄 You want to convert to {target_format.upper()}! But you have no files loaded. {suggestion}"
        
        # Execute conversion
        dashboard.quick_convert(target_format)
        
        # Track favorite formats
        self._track_format_usage(target_format)
        
        return f"🔄 Converting {file_count} file(s) to {target_format.upper()}..."
    
    def _handle_format_info(self, entities: dict) -> str:
        """Handle format information requests"""
        formats = entities.get('formats', [])
        
        if not formats:
            return self._get_supported_formats()
        
        fmt = formats[0]
        
        if fmt not in self.format_knowledge:
            return f"⚠️ I don't have information about '{fmt}'. Try: PDF, DOCX, JPG, PNG, MP3, MP4"
        
        info = self.format_knowledge[fmt]
        return f"""📄 **{info['name']}** - {info['full_name']}

📝 **Description:** {info['description']}

✨ **Best for:** {info['best_for']}

📌 **Aliases:** {', '.join(info['aliases'])}

💡 **Tip:** {self._get_format_tip(fmt)}"""
    
    def _handle_status(self, dashboard=None) -> str:
        """Handle status with detailed information"""
        if not dashboard:
            return "📊 All Files Converter AI v3.0.0 is running."
        
        status = f"📊 **Application Status** - {datetime.now().strftime('%I:%M %p')}\n\n"
        status += f"• **Files loaded:** {len(dashboard.current_files) if hasattr(dashboard, 'current_files') else 0}\n"
        status += f"• **Output format:** {dashboard.format_combo.currentText() if hasattr(dashboard, 'format_combo') else 'PDF'}\n"
        status += f"• **Theme:** {getattr(dashboard, 'current_theme', 'light').title()}\n"
        status += f"• **Converting:** {'Yes' if getattr(dashboard, 'is_converting', False) else 'No'}\n"
        status += f"• **Session time:** {self._format_duration(datetime.now() - self.context['session_start'])}\n"
        status += f"• **Interactions:** {self.context['interaction_count']}\n"
        
        # Favorite formats
        if self.context['favorite_formats']:
            fav = self.context['favorite_formats'][:3]
            status += f"• **Favorite formats:** {', '.join(f.upper() for f in fav)}\n"
        
        # Learning stats
        if self.context['learning_data']:
            learned = len(self.context['learning_data'])
            status += f"• **Learned patterns:** {learned}\n"
        
        return status
    
    def _handle_history(self) -> str:
        """Handle history with detailed information"""
        try:
            from app.core.history import history_manager
            entries = history_manager.get_all()
            
            if not entries:
                return "📋 No conversion history yet. Start converting files to build history!"
            
            stats = history_manager.get_stats()
            
            response = f"📋 **Conversion History**\n\n"
            response += f"• **Total conversions:** {stats['total']}\n"
            response += f"• **Successful:** {stats['successful']}\n"
            response += f"• **Failed:** {stats['failed']}\n"
            response += f"• **Success rate:** {stats['success_rate']}\n\n"
            
            # Show recent 5
            recent = entries[-5:]
            response += "**Recent 5 conversions:**\n"
            for entry in reversed(recent):
                status = "✅" if entry.get('success') else "❌"
                input_name = Path(entry.get('input', '')).name
                output_name = Path(entry.get('output', '')).name
                timestamp = entry.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        timestamp = dt.strftime('%H:%M')
                    except:
                        pass
                response += f"• {status} {input_name} → {output_name} ({timestamp})\n"
            
            return response
            
        except Exception as e:
            return f"⚠️ Error loading history: {str(e)}"
    
    def _handle_clear(self, dashboard=None) -> str:
        """Handle clear commands"""
        if not dashboard:
            return "⚠️ No dashboard available to clear files."
        
        if hasattr(dashboard, 'remove_all_files'):
            if 'confirm' in self.context.get('last_query', '').lower():
                dashboard.remove_all_files()
                return "🗑️ All files cleared successfully!"
            else:
                self.context['awaiting_confirmation'] = 'clear'
                return "⚠️ Are you sure you want to clear all files? Say 'Confirm' to proceed."
        
        return "⚠️ Could not clear files. Please use the 'Clear All' button."
    
    def _handle_open(self, entities: dict) -> str:
        """Handle open folder commands"""
        folders = entities.get('folders', [])
        
        if not folders:
            return "📁 Which folder would you like to open? Options: Documents, Downloads, Desktop, Pictures"
        
        folder_map = {
            'documents': Path.home() / 'Documents',
            'downloads': Path.home() / 'Downloads',
            'desktop': Path.home() / 'Desktop',
            'pictures': Path.home() / 'Pictures',
            'videos': Path.home() / 'Videos',
            'music': Path.home() / 'Music'
        }
        
        folder = folders[0].lower()
        if folder in folder_map:
            try:
                subprocess.Popen(['explorer', str(folder_map[folder])])
                return f"📁 Opened {folder.capitalize()} folder successfully!"
            except:
                return f"⚠️ Could not open {folder}. Please try manually."
        
        return f"⚠️ Unknown folder: '{folder}'. Try: Documents, Downloads, Desktop"
    
    def _handle_theme(self, entities: dict, dashboard=None) -> str:
        """Handle theme change commands"""
        if not dashboard or not hasattr(dashboard, 'apply_theme'):
            return "⚠️ Theme change is not available."
        
        query = self.context['last_query']
        q = query.lower()
        
        themes = {
            'dark': ['dark', 'night', 'black', 'dark mode'],
            'light': ['light', 'white', 'day', 'light mode'],
            'professional_blue': ['professional blue', 'blue', 'corporate'],
            'clean_teal': ['clean teal', 'teal'],
            'elegant_plum': ['elegant plum', 'plum', 'purple'],
            'soft_green': ['soft green', 'green']
        }
        
        for theme_name, aliases in themes.items():
            for alias in aliases:
                if alias in q:
                    dashboard.apply_theme(theme_name)
                    return f"🎨 Theme changed to {theme_name.replace('_', ' ').title()}!"
        
        return "🎨 Available themes: Dark, Light, Professional Blue, Clean Teal, Elegant Plum, Soft Green"
    
    def _handle_suggestion(self, query: str, dashboard=None) -> str:
        """Handle smart suggestions"""
        q = query.lower()
        
        # Check for specific suggestions
        if 'file' in q or 'convert' in q:
            return random.choice(self.suggestions['conversion'])
        
        if 'optimize' in q or 'quality' in q or 'size' in q:
            return random.choice(self.suggestions['optimization'])
        
        if 'useful' in q or 'feature' in q:
            return random.choice(self.suggestions['useful'])
        
        # Default suggestions
        suggestions = []
        
        # Check files
        if dashboard and hasattr(dashboard, 'current_files'):
            file_count = len(dashboard.current_files)
            if file_count == 0:
                suggestions.append("📁 You haven't added any files. Try drag and drop or say 'Pick report.pdf'")
            else:
                suggestions.append(f"📄 You have {file_count} files ready to convert!")
        
        # Check for favorite formats
        if self.context['favorite_formats']:
            fav = self.context['favorite_formats'][0]
            suggestions.append(f"💡 You often use {fav.upper()}. Want to convert something to {fav.upper()}?")
        
        suggestions.append("💡 Try asking: 'Convert to PDF' or 'Open Documents'")
        suggestions.append("📷 Try scanning a document with the camera feature!")
        suggestions.append("📝 OCR can extract text from images - give it a try!")
        
        return "💡 **Smart Suggestions**\n\n• " + "\n• ".join(suggestions[:4])
    
    def _handle_analytics(self, dashboard=None) -> str:
        """Handle analytics and statistics"""
        try:
            from app.core.history import history_manager
            stats = history_manager.get_stats()
            
            response = "📊 **Analytics & Statistics**\n\n"
            response += f"• **Total conversions:** {stats['total']}\n"
            response += f"• **Success rate:** {stats['success_rate']}\n"
            response += f"• **Session interactions:** {self.context['interaction_count']}\n"
            response += f"• **Session duration:** {self._format_duration(datetime.now() - self.context['session_start'])}\n"
            
            if self.context['favorite_formats']:
                response += f"• **Favorite formats:** {', '.join(f.upper() for f in self.context['favorite_formats'][:5])}\n"
            
            if self.context['learning_data']:
                response += f"• **Learned patterns:** {len(self.context['learning_data'])}\n"
            
            return response
            
        except:
            return "📊 Analytics are available. Convert more files to see detailed statistics!"
    
    def _handle_search(self, entities: dict, dashboard=None) -> str:
        """Handle file search"""
        query = self.context['last_query']
        # Extract search term
        search_match = re.search(r'search (?:for )?([^\s].*)', query.lower())
        if search_match:
            search_term = search_match.group(1)
            if dashboard and hasattr(dashboard, 'filter_files'):
                dashboard.filter_files(search_term)
                return f"🔍 Searching for '{search_term}'..."
        
        return "🔍 Say 'Search for report' to find files in your list."
    
    def _handle_save(self, entities: dict, dashboard=None) -> str:
        """Handle save commands"""
        if dashboard and hasattr(dashboard, 'start_conversion'):
            # Check if formats specified
            formats = entities.get('formats', [])
            if formats:
                dashboard.quick_convert(formats[0])
                return f"💾 Converting and saving to {formats[0].upper()}..."
            
            dashboard.start_conversion()
            return "💾 Starting conversion and save process..."
        
        return "💾 Click the 'Convert Now' button to save your files."
    
    def _handle_compress(self, entities: dict, dashboard=None) -> str:
        """Handle compress commands"""
        formats = entities.get('formats', [])
        if 'zip' in str(formats) or 'archive' in self.context['last_query'].lower():
            # Set format to zip
            if dashboard and hasattr(dashboard, 'format_combo'):
                dashboard.format_combo.setCurrentText('ZIP')
                dashboard.start_conversion()
                return "📦 Compressing files to ZIP archive..."
        
        return "📦 Say 'Compress to ZIP' to archive your files."
    
    def _handle_resize(self, entities: dict, dashboard=None) -> str:
        """Handle resize commands"""
        numbers = entities.get('numbers', [])
        if numbers:
            size = numbers[0]
            return f"📐 Resizing to {size} pixels. This feature is available in the image converter."
        
        return "📐 Say 'Resize to 800x600' or 'Resize to 50%' to scale images."
    
    def _handle_quality(self, entities: dict, dashboard=None) -> str:
        """Handle quality settings"""
        query = self.context['last_query']
        q = query.lower()
        
        if 'high' in q:
            if dashboard and hasattr(dashboard, 'settings'):
                dashboard.settings.set('quality', 'high')
                dashboard.settings.save()
            return "✅ Quality set to HIGH (Best quality, larger files)"
        
        if 'medium' in q:
            if dashboard and hasattr(dashboard, 'settings'):
                dashboard.settings.set('quality', 'medium')
                dashboard.settings.save()
            return "✅ Quality set to MEDIUM (Balanced)"
        
        if 'low' in q:
            if dashboard and hasattr(dashboard, 'settings'):
                dashboard.settings.set('quality', 'low')
                dashboard.settings.save()
            return "✅ Quality set to LOW (Smaller files, faster)"
        
        return "⚙️ Quality options: High, Medium, Low. Say: 'High quality' or 'Medium quality'"
    
    def _handle_cancel(self, dashboard=None) -> str:
        """Handle cancel commands"""
        if dashboard and hasattr(dashboard, 'cancel_conversion'):
            dashboard.cancel_conversion()
            return "⏹️ Conversion cancelled successfully!"
        
        return "⚠️ No conversion in progress to cancel."
    
    def _handle_settings(self, entities: dict, dashboard=None) -> str:
        """Handle settings commands"""
        query = self.context['last_query']
        
        if 'folder' in query or 'output' in query:
            return "📁 Output folder can be changed in Settings → Output Folder"
        
        if 'format' in query:
            return "📄 Default format can be changed in Settings → Default Format"
        
        return "⚙️ Open Settings from the sidebar to change preferences."
    
    def _handle_rename(self, entities: dict, dashboard=None) -> str:
        """Handle rename commands"""
        return "📝 Rename files using: File → Save As during conversion."
    
    def _handle_move(self, entities: dict, dashboard=None) -> str:
        """Handle move commands"""
        return "📂 Files can be moved using drag and drop, or by selecting output folder during conversion."
    
    def _handle_ocr(self, dashboard=None) -> str:
        """Handle OCR commands"""
        if dashboard and hasattr(dashboard, 'open_ocr'):
            dashboard.open_ocr()
            return "📄 OCR dialog opened. Select an image to extract text."
        return "📄 OCR feature available. Click 'OCR Extract Text' in Quick Actions."
    
    def _handle_batch(self, dashboard=None) -> str:
        """Handle batch conversion"""
        if dashboard and hasattr(dashboard, 'start_conversion'):
            dashboard.start_conversion()
            return "📦 Starting batch conversion of all files..."
        return "📦 Use the 'Convert Now' button for batch conversion."
    
    def _handle_smart_fallback(self, query: str, entities: dict, dashboard=None) -> str:
        """Handle fallback with smart analysis"""
        q = query.lower()
        
        # Check if it's a question
        if '?' in q:
            if 'what' in q:
                return "❓ I'm not sure about that. Try asking: 'What formats are supported?' or 'What can you do?'"
            if 'how' in q:
                return "❓ To learn how to do something, try: 'Help' or 'What can you do?'"
            return "❓ I didn't understand that question. Try saying 'Help' for a list of commands."
        
        # Check for format mentions
        for fmt in self.format_knowledge:
            if fmt in q:
                return f"📄 I see you mentioned {fmt.upper()}. Would you like to convert to {fmt.upper()}? Say: 'Convert to {fmt.upper()}'"
        
        # Friendly fallback
        responses = [
            f"I understand you're asking about '{query}'. Try:\n• 'Help' for commands\n• 'Convert to PDF' to convert\n• 'Open Documents' to browse",
            f"Interesting query! I can help with file conversion. Try: 'Convert to PDF' or 'Help'",
            f"I'm not sure about '{query}'. I can help with file conversion, opening folders, and more."
        ]
        return random.choice(responses)
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def _get_time_of_day(self) -> str:
        """Get time of day greeting"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'
    
    def _format_duration(self, delta) -> str:
        """Format duration"""
        seconds = delta.total_seconds()
        minutes = int(seconds // 60)
        hours = int(minutes // 60)
        minutes = int(minutes % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return f"{int(seconds)}s"
    
    def _get_format_tip(self, fmt: str) -> str:
        """Get format-specific tips"""
        tips = {
            'pdf': "PDF is best for documents you want to share or print.",
            'docx': "DOCX is editable in Microsoft Word and most document editors.",
            'jpg': "JPG is perfect for photos and images for the web.",
            'png': "PNG is great for graphics and images with transparency.",
            'mp3': "MP3 offers good audio quality with small file sizes.",
            'mp4': "MP4 is the most compatible video format for all devices.",
            'zip': "ZIP saves space and makes it easy to share multiple files."
        }
        return tips.get(fmt, "Always choose the format that best fits your needs.")
    
    def _get_random_response(self, category: str) -> str:
        """Get random response for category"""
        responses = {
            'empty': [
                "Please ask me something! 😊",
                "I'm listening! What would you like to know?",
                "Don't be shy, ask me anything about file conversion!"
            ]
        }
        return random.choice(responses.get(category, ["Say something!"]))
    
    def _get_context_info(self) -> dict:
        """Get context information"""
        return {
            'file_count': len(self.context.get('file_context', [])),
            'interaction_count': self.context['interaction_count'],
            'session_duration': datetime.now() - self.context['session_start']
        }
    
    def _track_format_usage(self, format_name: str):
        """Track format usage for personalization"""
        if format_name not in self.context['favorite_formats']:
            self.context['favorite_formats'].append(format_name)
            # Keep only top 10
            if len(self.context['favorite_formats']) > 10:
                self.context['favorite_formats'] = self.context['favorite_formats'][-10:]
    
    def _update_learning(self, query: str):
        """Update learning data"""
        # Simple learning: track format mentions
        for fmt in self.format_knowledge:
            if fmt in query.lower():
                if fmt not in self.context['learning_data']:
                    self.context['learning_data'][fmt] = 1
                else:
                    self.context['learning_data'][fmt] += 1
        
        # Save learning
        self._save_learning_data()
    
    def _get_supported_formats(self) -> str:
        """Get supported formats with descriptions"""
        return """📄 **Supported Formats**

📚 **Documents:** PDF, DOCX, DOC, TXT, RTF, ODT, HTML, MD
🖼️ **Images:** JPG, PNG, GIF, BMP, TIFF, WEBP, ICO, SVG
🎵 **Audio:** MP3, WAV, AAC, FLAC, OGG, M4A, WMA
🎬 **Video:** MP4, AVI, MOV, MKV, WEBM, FLV, WMV
📦 **Archives:** ZIP, RAR, 7Z, TAR, GZ, BZ2, XZ
📚 **E-books:** EPUB, MOBI, AZW3, FB2
📊 **Spreadsheets:** XLSX, XLS, CSV, ODS, TSV

✨ **Over 100+ formats supported!**

💡 To learn about a specific format, say: "Tell me about PDF" """
    
    # ============================================================
    # PERSISTENT LEARNING
    # ============================================================
    
    def _get_learning_file(self) -> Path:
        """Get learning data file path"""
        from config import Config
        return Config.DATA_DIR / 'ai_learning.json'
    
    def _load_learning_data(self):
        """Load learning data from file"""
        try:
            learning_file = self._get_learning_file()
            if learning_file.exists():
                with open(learning_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.context['learning_data'] = data.get('format_usage', {})
                    self.context['favorite_formats'] = data.get('favorite_formats', [])
                    self.context['user_name'] = data.get('user_name')
                logger.info(f"📚 Loaded learning data with {len(self.context['learning_data'])} patterns")
        except Exception as e:
            logger.warning(f"Could not load learning data: {e}")
    
    def _save_learning_data(self):
        """Save learning data to file"""
        try:
            learning_file = self._get_learning_file()
            learning_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'format_usage': self.context['learning_data'],
                'favorite_formats': self.context['favorite_formats'],
                'user_name': self.context.get('user_name')
            }
            with open(learning_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save learning data: {e}")
    
    # ============================================================
    # PUBLIC API
    # ============================================================
    
    def set_user_name(self, name: str):
        """Set user name for personalization"""
        self.context['user_name'] = name
        self._save_learning_data()
    
    def set_converter(self, converter):
        """Set converter engine reference"""
        self.converter = converter
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            'loaded': True,
            'loading': False,
            'model_name': self.model_name,
            'type': 'Ultra-Intelligent Assistant',
            'ready': True,
            'context_size': len(self.context['conversation_history']),
            'formats_supported': len(self.format_knowledge),
            'intents': len(self.intents),
            'interactions': self.context['interaction_count'],
            'learned_patterns': len(self.context['learning_data']),
            'favorite_formats': self.context['favorite_formats'][:5]
        }
    
    def is_available(self) -> bool:
        """Check if AI is available"""
        return True
    
    def wait_for_loading(self, timeout: int = 1) -> bool:
        """Wait for loading (always ready)"""
        return True
    
    def clear_context(self):
        """Clear conversation context"""
        self.context['conversation_history'] = []
        self.context['last_query'] = None
        self.context['last_response'] = None
        logger.info("AI context cleared")


# Singleton instance
ai_engine = AIEngine()