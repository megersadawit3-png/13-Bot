"""
የቦቱ ውቅር ፋይል - የተሻሻለ
"""

import os
import logging
from dotenv import load_dotenv
from typing import List

load_dotenv()

# ============================================
# ሎግ ማዋቀር
# ============================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# ============================================
# የቦት ቶከኖች
# ============================================

BOT_TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_BOT_TOKEN = os.getenv('ADMIN_BOT_TOKEN', '')

if not BOT_TOKEN or not ADMIN_BOT_TOKEN:
    raise ValueError("❌ የቦት ቶከኖች አልተገኙም! .env ፋይሉን ያረጋግጡ")

# ============================================
# አስተዳዳሪዎች
# ============================================

def parse_admin_ids(admin_ids_str: str) -> List[int]:
    """የአስተዳዳሪ መታወቂያዎችን መተርጎም"""
    if not admin_ids_str:
        return []
    return [int(id.strip()) for id in admin_ids_str.split(',') if id.strip().isdigit()]

ADMIN_IDS = parse_admin_ids(os.getenv('ADMIN_IDS', ''))

if not ADMIN_IDS:
    print("⚠️ ምንም አስተዳዳሪ አልተገኘም! እባክዎ ADMIN_IDS ያዘጋጁ")

# ============================================
# የውሂብ ጎታ
# ============================================

DATABASE_FILE = os.getenv('DATABASE_FILE', 'marketplace.db')
DATABASE_RETRY_COUNT = 3
DATABASE_RETRY_DELAY = 0.5

# ============================================
# የስርዓት ውቅሮች
# ============================================

SALES_THRESHOLD = int(os.getenv('SALES_THRESHOLD', 50))
DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'am')
SUPPORTED_LANGUAGES = ['am', 'en', 'or']

# የማስታወቂያ ገደቦች
MAX_BROADCAST_RETRIES = 3
BROADCAST_DELAY = 0.05  # ሴኮንድ

# የፋይል ገደቦች
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# ============================================
# የይዘት ምድቦች
# ============================================

CONTENT_CATEGORIES = {
    'ebook': '📚 ኢ-መጽሐፍ',
    'magazine': '📰 መጽሔት',
    'handout': '📋 ማስታወሻ',
    'question_bank': '❓ የጥያቄ ባንክ',
    'research_paper': '📄 የምርምር ወረቀት'
}

CATEGORY_NAMES = {
    'am': {
        'ebook': 'ኢ-መጽሐፍ',
        'magazine': 'መጽሔት',
        'handout': 'ማስታወሻ',
        'question_bank': 'የጥያቄ ባንክ',
        'research_paper': 'የምርምር ወረቀት'
    },
    'en': {
        'ebook': 'E-Book',
        'magazine': 'Magazine',
        'handout': 'Handout',
        'question_bank': 'Question Bank',
        'research_paper': 'Research Paper'
    },
    'or': {
        'ebook': 'Kitaaba Elektiroonii',
        'magazine': 'Magaazii',
        'handout': 'Karoora',
        'question_bank': 'Bankii Gaaffii',
        'research_paper': 'Waraqata Qorannoo'
    }
}

# ============================================
# የደራሲ ደረጃዎች
# ============================================

AUTHOR_LEVELS = {
    'standard': '📌 መደበኛ',
    'verified': '✅ የተረጋገጠ',
    'trusted': '⭐ የታመነ',
    'top': '🏆 ከፍተኛ',
    'editors_choice': '👑 የአርታኢ ምርጫ'
}

AUTHOR_LEVEL_ORDER = ['standard', 'verified', 'trusted', 'top', 'editors_choice']

# ============================================
# የይዘት ሁኔታዎች
# ============================================

CONTENT_STATUS = {
    'draft': '📝 ረቂቅ',
    'pending': '⏳ በግምገማ ላይ',
    'published': '📖 የታተመ',
    'suspended': '⛔ የታገደ',
    'rejected': '❌ የተሰረዘ'
}

# ============================================
# የማሳያ ውቅሮች
# ============================================

ITEMS_PER_PAGE = 5
MAX_TITLE_LENGTH = 30
MAX_DESCRIPTION_PREVIEW = 80
