#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bulletin Formatter for Chhattisgarh News Bot
Formats verified news into WhatsApp/Telegram bulletin format
"""

import logging
from datetime import datetime
import pytz
from typing import List, Dict

logger = logging.getLogger(__name__)

class BulletinFormatter:
    def __init__(self):
        self.ist = pytz.timezone('Asia/Kolkata')
        
        # Emoji mapping for different news categories
        self.category_emojis = {
            'crime': '🚨',
            'politics': '📌', 
            'accident': '🚗',
            'development': '🛣️',
            'health': '💊',
            'weather': '🌧️',
            'education': '📚',
            'court': '⚖️',
            'government': '🏛️',
            'security': '🪖',
            'investigation': '🕵️',
            'water': '💧',
            'general': '📰'
        }
        
        # Keywords to emoji mapping
        self.keyword_emojis = {
            'हाई कोर्ट': '⚖️',
            'सुप्रीम कोर्ट': '⚖️',
            'न्यायालय': '⚖️',
            'फैसला': '⚖️',
            'ठगी': '🚨',
            'फ्रॉड': '🚨',
            'गिरफ्तार': '🚨',
            'अपराध': '🚨',
            'चोरी': '🚨',
            'हत्या': '🚨',
            'दुर्घटना': '🚗',
            'हादसा': '🚗',
            'मौत': '🚗',
            'घायल': '🚗',
            'सड़क': '🛣️',
            'परियोजना': '🛣️',
            'निर्माण': '🛣️',
            'फोरलेन': '🛣️',
            'पुल': '🛣️',
            'मुख्यमंत्री': '📌',
            'मंत्री': '📌',
            'सरकार': '📌',
            'नीति': '📌',
            'योजना': '📌',
            'नक्सल': '🪖',
            'सुरक्षा': '🪖',
            'पुलिस': '🪖',
            'आत्मसमर्पण': '🪖',
            'सीबीआई': '🕵️',
            'ईडी': '🕵️',
            'जांच': '🕵️',
            'छापेमारी': '🕵️',
            'रिश्वत': '🕵️',
            'बारिश': '🌧️',
            'मौसम': '🌧️',
            'तूफान': '🌧️',
            'बाढ़': '💧',
            'पानी': '💧',
            'डायरिया': '💧',
            'बीमारी': '💊',
            'अस्पताल': '💊',
            'डॉक्टर': '💊',
            'इलाज': '💊',
            'शिक्षा': '📚',
            'स्कूल': '📚',
            'कॉलेज': '📚',
            'परीक्षा': '📚',
            'छात्र': '📚'
        }

    def get_emoji_for_content(self, title: str, body: str) -> str:
        """Get appropriate emoji based on content"""
        text = f"{title} {body}".lower()
        
        # Check for specific keywords first
        for keyword, emoji in self.keyword_emojis.items():
            if keyword.lower() in text:
                return emoji
        
        # Fallback to category emoji
        return '📰'

    def create_headline(self, article: Dict) -> str:
        """Create formatted headline with emoji"""
        title = article.get('title', '')
        body = article.get('body', '')
        
        # Get appropriate emoji
        emoji = self.get_emoji_for_content(title, body)
        
        # Extract key topic from title
        topic = self.extract_topic(title)
        
        # Create formatted headline
        headline = f"{emoji} *{topic}*: {self.create_summary(article)}"
        
        return headline

    def extract_topic(self, title: str) -> str:
        """Extract main topic from title"""
        # Common patterns for topic extraction
        topic_patterns = {
            'हाई कोर्ट': 'हाई कोर्ट का फैसला',
            'सुप्रीम कोर्ट': 'सुप्रीम कोर्ट का फैसला',
            'ठगी': 'डिजिटल अरेस्ट फ्रॉड',
            'फ्रॉड': 'डिजिटल फ्रॉड',
            'दुर्घटना': 'सड़क हादसा',
            'हादसा': 'सड़क हादसा',
            'सड़क': 'फोरलेन सड़क परियोजना',
            'परियोजना': 'विकास परियोजना',
            'नक्सल': 'नक्सल विरोधी अभियान',
            'आत्मसमर्पण': 'नक्सल आत्मसमर्पण',
            'सीबीआई': 'सीबीआई की कार्रवाई',
            'ईडी': 'ईडी की कार्रवाई',
            'बारिश': 'मौसम अपडेट',
            'मौसम': 'मौसम अपडेट',
            'डायरिया': 'स्वास्थ्य चेतावनी',
            'बीमारी': 'स्वास्थ्य अलर्ट'
        }
        
        title_lower = title.lower()
        
        for keyword, topic in topic_patterns.items():
            if keyword in title_lower:
                return topic
        
        # If no pattern matches, use first few words
        words = title.split()[:3]
        return ' '.join(words)

    def create_summary(self, article: Dict) -> str:
        """Create 2-3 line summary"""
        title = article.get('title', '')
        body = article.get('body', '')
        
        # Combine title and body
        full_text = f"{title}. {body}"
        
        # Split into sentences
        sentences = [s.strip() for s in full_text.split('.') if s.strip()]
        
        # Select most important sentences (first 2-3)
        summary_sentences = sentences[:2]
        
        # Join and clean
        summary = '. '.join(summary_sentences)
        
        # Ensure it ends with period
        if not summary.endswith('.'):
            summary += '।'
        
        # Limit length (approximately 2-3 lines)
        if len(summary) > 200:
            summary = summary[:197] + '...'
        
        return summary

    def format_bulletin(self, verified_articles: List[Dict]) -> str:
        """Format complete bulletin"""
        if not verified_articles:
            return "आज कोई महत्वपूर्ण खबर उपलब्ध नहीं है।"
        
        # Get current date
        current_date = datetime.now(self.ist)
        date_str = current_date.strftime("%d %B %Y")
        
        # Convert English month to Hindi
        month_mapping = {
            'January': 'जनवरी', 'February': 'फरवरी', 'March': 'मार्च',
            'April': 'अप्रैल', 'May': 'मई', 'June': 'जून',
            'July': 'जुलाई', 'August': 'अगस्त', 'September': 'सितंबर',
            'October': 'अक्टूबर', 'November': 'नवंबर', 'December': 'दिसंबर'
        }
        
        for eng_month, hindi_month in month_mapping.items():
            date_str = date_str.replace(eng_month, hindi_month)
        
        # Start bulletin
        bulletin = f"🌟 *छत्तीसगढ़ की ताज़ा खबरें – {date_str}*\n\n"
        
        # Add each news item
        for i, article in enumerate(verified_articles[:8], 1):
            headline = self.create_headline(article)
            bulletin += f"{headline}\n\n"
        
        # Add footer
        bulletin += "⸻"
        
        return bulletin

    def format_for_tts(self, verified_articles: List[Dict]) -> str:
        """Format bulletin text for TTS (without emojis and markdown)"""
        if not verified_articles:
            return "आज छत्तीसगढ़ से कोई महत्वपूर्ण खबर उपलब्ध नहीं है।"
        
        # Get current date
        current_date = datetime.now(self.ist)
        date_str = current_date.strftime("%d %B %Y")
        
        # Convert to Hindi
        month_mapping = {
            'January': 'जनवरी', 'February': 'फरवरी', 'March': 'मार्च',
            'April': 'अप्रैल', 'May': 'मई', 'June': 'जून',
            'July': 'जुलाई', 'August': 'अगस्त', 'September': 'सितंबर',
            'October': 'अक्टूबर', 'November': 'नवंबर', 'December': 'दिसंबर'
        }
        
        for eng_month, hindi_month in month_mapping.items():
            date_str = date_str.replace(eng_month, hindi_month)
        
        # Start TTS script
        tts_text = f"छत्तीसगढ़ न्यूज़, आपका बॉट प्रस्तुत करता है {date_str} की मुख्य खबरें।\n\n"
        
        # Add each news item (without emojis)
        for i, article in enumerate(verified_articles[:8], 1):
            title = article.get('title', '')
            summary = self.create_summary(article)
            
            # Clean text for TTS
            clean_summary = self.clean_for_tts(summary)
            topic = self.extract_topic(title)
            
            tts_text += f"{topic}। {clean_summary}\n\n"
        
        tts_text += "यह थी आज की मुख्य खबरें। धन्यवाद।"
        
        return tts_text

    def clean_for_tts(self, text: str) -> str:
        """Clean text for natural TTS pronunciation"""
        # Number replacements for natural Hindi pronunciation
        number_replacements = {
            '22 लाख': 'बाईस लाख',
            '88 लाख': 'अट्ठासी लाख',
            '160 किमी': 'एक सौ साठ किलोमीटर',
            '13 इनामी': 'तेरह इनामी',
            '5 मौतें': 'पांच मौतें',
            '3 की मौत': 'तीन की मौत',
            '6 घायल': 'छह घायल',
            '3 डॉक्टर': 'तीन डॉक्टर'
        }
        
        # Abbreviation replacements
        abbrev_replacements = {
            'सीबीआई': 'सेंट्रल ब्यूरो ऑफ इन्वेस्टिगेशन',
            'ईडी': 'एनफोर्समेंट डायरेक्टोरेट',
            'एसपी': 'सुपरिंटेंडेंट ऑफ पुलिस',
            'डीएम': 'डिस्ट्रिक्ट मजिस्ट्रेट',
            'पीएचई': 'पब्लिक हेल्थ इंजीनियरिंग',
            'एफडी': 'फिक्स्ड डिपॉजिट'
        }
        
        # Apply replacements
        for original, replacement in number_replacements.items():
            text = text.replace(original, replacement)
        
        for original, replacement in abbrev_replacements.items():
            text = text.replace(original, replacement)
        
        # Remove special characters that might confuse TTS
        text = text.replace('*', '').replace('_', '').replace('`', '')
        
        return text