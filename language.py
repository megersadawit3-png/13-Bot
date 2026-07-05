"""
የቋንቋ አስተዳዳሪ - ለሶስት ቋንቋዎች ድጋፍ
"""

import json
import os
from typing import Optional, Dict, Any

# ============================================
# ውቅር
# ============================================

LANGUAGE_FILES = {
    'am': os.path.join('locales', 'am.json'),
    'en': os.path.join('locales', 'en.json'),
    'or': os.path.join('locales', 'or.json')
}

LANGUAGE_NAMES = {
    'am': 'አማርኛ',
    'en': 'English',
    'or': 'Oromiffa'
}

LANGUAGE_FLAGS = {
    'am': '🇪🇹',
    'en': '🇬🇧',
    'or': '🇪🇹'
}

SUPPORTED_LANGUAGES = ['am', 'en', 'or']
DEFAULT_LANGUAGE = 'am'

# ============================================
# የቋንቋ አስተዳዳሪ ክፍል
# ============================================

class LanguageManager:
    """የቋንቋ አስተዳዳሪ"""
    
    def __init__(self):
        self.translations = {}
        self._load_all_translations()
    
    def _load_all_translations(self):
        """ሁሉንም ቋንቋዎች መጫን"""
        for code, file_path in LANGUAGE_FILES.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[code] = json.load(f)
            except FileNotFoundError:
                print(f"⚠️ የቋንቋ ፋይል አልተገኘም: {file_path}")
                self.translations[code] = {}
            except json.JSONDecodeError:
                print(f"⚠️ የቋንቋ ፋይል ስህተት: {file_path}")
                self.translations[code] = {}
    
    def get_text(self, lang: str, key: str, **kwargs) -> str:
        """በተመረጠ ቋንቋ ጽሁፍ ማግኘት"""
        # ቋንቋው ካልተገኘ ነባሪ ተጠቀም
        if lang not in self.translations or not self.translations.get(lang):
            lang = DEFAULT_LANGUAGE
        
        # ቁልፉን በነጥብ መለየት (e.g., "buttons.browse")
        keys = key.split('.')
        value = self.translations.get(lang, {})
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                value = None
                break
        
        # ካልተገኘ እንግሊዝኛ ሞክር
        if value is None:
            value = self.translations.get('en', {}).get(key, key)
        
        # ተለዋዋጮችን መተካት
        if kwargs and isinstance(value, str):
            try:
                value = value.format(**kwargs)
            except (KeyError, ValueError):
                # ተለዋዋጮች ካልተገኙ መልእክቱን እንደሱ መልስ
                pass
        
        return value if isinstance(value, str) else str(value)
    
    def get_language_name(self, lang: str) -> str:
        """የቋንቋ ስም ማግኘት"""
        return LANGUAGE_NAMES.get(lang, lang)
    
    def get_language_flag(self, lang: str) -> str:
        """የቋንቋ ባንዲራ ማግኘት"""
        return LANGUAGE_FLAGS.get(lang, '🌍')
    
    def get_supported_languages(self) -> list:
        """ሁሉንም የተደገፉ ቋንቋዎች ማግኘት"""
        return SUPPORTED_LANGUAGES
    
    def is_supported(self, lang: str) -> bool:
        """ቋንቋው የተደገፈ መሆኑን መፈተሽ"""
        return lang in SUPPORTED_LANGUAGES

# ============================================
# ግሎባል ኢንስታንስ እና ተግባራት
# ============================================

_lang_manager = LanguageManager()

def get_text(lang: str, key: str, **kwargs) -> str:
    """በቀላል መንገድ ጽሁፍ ለማግኘት"""
    return _lang_manager.get_text(lang, key, **kwargs)

def get_language_name(lang: str) -> str:
    """የቋንቋ ስም ማግኘት"""
    return _lang_manager.get_language_name(lang)

def get_language_flag(lang: str) -> str:
    """የቋንቋ ባንዲራ ማግኘት"""
    return _lang_manager.get_language_flag(lang)

def get_supported_languages() -> list:
    """ሁሉንም የተደገፉ ቋንቋዎች ማግኘት"""
    return _lang_manager.get_supported_languages()

def is_supported(lang: str) -> bool:
    """ቋንቋው የተደገፈ መሆኑን መፈተሽ"""
    return _lang_manager.is_supported(lang)
