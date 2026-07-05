"""
የቦቱ ውቅር ፋይል
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# የቦት ቶከኖች
# ============================================

# የተጠቃሚ ቦት ቶከን (ከBotFather ያገኙት)
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# የአስተዳዳሪ ቦት ቶከን (ከBotFather ያገኙት)
ADMIN_BOT_TOKEN = os.getenv('ADMIN_BOT_TOKEN', '')

# ============================================
# አስተዳዳሪዎች
# ============================================

# የአስተዳዳሪ ተጠቃሚዎች የቴሌግራም መታወቂያ
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]

# ============================================
# የውሂብ ጎታ
# ============================================

DATABASE_FILE = os.getenv('DATABASE_FILE', 'marketplace.db')

# ============================================
# የስርዓት ውቅሮች
# ============================================

# የሽያጭ ገደብ (50 ሽያጭ ለአገልግሎት ክፍያ)
SALES_THRESHOLD = 50

# የተጠቃሚ ቋንቋ ነባሪ
DEFAULT_LANGUAGE = 'am'

# የሚደገፉ ቋንቋዎች
SUPPORTED_LANGUAGES = ['am', 'en', 'or']

# ============================================
# የይዘት ምድቦች
# ============================================

CONTENT_CATEGORIES = {
    'ebook': '📚 ኢ-መጽሐፍ / eBook / Kitaaba Elektiroonii',
    'magazine': '📰 መጽሔት / Magazine / Magaazii',
    'handout': '📋 ማስታወሻ / Handout / Karoora',
    'question_bank': '❓ የጥያቄ ባንክ / Question Bank / Bankii Gaaffii',
    'research_paper': '📄 የምርምር ወረቀት / Research Paper / Waraqata Qorannoo'
}

# ============================================
# የደራሲ ደረጃዎች
# ============================================

AUTHOR_LEVELS = {
    'standard': '📌 Standard / መደበኛ / Idilee',
    'verified': '✅ Verified / የተረጋገጠ / Mirkanaa'e',
    'trusted': '⭐ Trusted / የታመነ / Amanamaa',
    'top': '🏆 Top / ከፍተኛ / Ol'aanaa',
    'editors_choice': '👑 Editor\'s Choice / የአርታኢ ምርጫ / Filannaa Gulaalaa'
}

# ============================================
# የይዘት ሁኔታዎች
# ============================================

CONTENT_STATUS = {
    'draft': '📝 Draft / ረቂቅ / Barreeffama',
    'pending': '⏳ Pending Review / በግምገማ ላይ / Eegala',
    'published': '📖 Published / የታተመ / Maxxanfame',
    'suspended': '⛔ Suspended / የታገደ / Dhaabate',
    'rejected': '❌ Rejected / የተሰረዘ / Hafame'
}
