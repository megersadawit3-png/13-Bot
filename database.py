"""
የውሂብ ጎታ ክወናዎች - SQLite
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any

from config import DATABASE_FILE

# ============================================
# የውሂብ ጎታ ግንኙነት
# ============================================

def get_db():
    """የውሂብ ጎታ ግንኙነት መፍጠር"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """የውሂብ ጎታ ሰንጠረዦችን መፍጠር"""
    conn = get_db()
    cursor = conn.cursor()
    
    # ============================================
    # ተጠቃሚዎች
    # ============================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            full_name TEXT,
            phone TEXT,
            role TEXT DEFAULT 'user',
            language TEXT DEFAULT 'am',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ============================================
    # ደራሲዎች
    # ============================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            level TEXT DEFAULT 'Standard',
            is_verified BOOLEAN DEFAULT 0,
            total_sales INTEGER DEFAULT 0,
            avg_rating REAL DEFAULT 0,
            bio TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ============================================
    # ይዘቶች
    # ============================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author_id INTEGER REFERENCES authors(id),
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            file_id TEXT,
            sample_file_id TEXT,
            price REAL DEFAULT 0,
            total_sales INTEGER DEFAULT 0,
            status TEXT DEFAULT 'draft',
            copyright_declared BOOLEAN DEFAULT 0,
            drm_method TEXT,
            quality_score REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            published_at TIMESTAMP
        )
    ''')
    
    # ============================================
    # ግዢዎች
    # ============================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            content_id INTEGER REFERENCES content(id),
            amount REAL,
            status TEXT DEFAULT 'pending',
            purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ============================================
    # ቤተ-መጽሐፍት
    # ============================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            content_id INTEGER REFERENCES content(id),
            downloaded BOOLEAN DEFAULT 0,
            last_downloaded_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, content_id)
        )
    ''')
    
    # ============================================
    # ሪፖርቶች / ክርክሮች
    # ============================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER REFERENCES content(id),
            reporter_id INTEGER REFERENCES users(id),
            reason TEXT,
            status TEXT DEFAULT 'pending',
            admin_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP
        )
    ''')
    
    # ============================================
    # ግምገማዎች
    # ============================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            content_id INTEGER REFERENCES content(id),
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            review TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, content_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ የውሂብ ጎታ ተፈጥሯል!")

# ============================================
# የተጠቃሚ ክወናዎች
# ============================================

def create_user(telegram_id: int, username: str, full_name: str, language: str = 'am') -> int:
    """አዲስ ተጠቃሚ መፍጠር"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (telegram_id, username, full_name, language)
        VALUES (?, ?, ?, ?)
    ''', (telegram_id, username, full_name, language))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def get_user(telegram_id: int) -> Optional[Dict]:
    """ተጠቃሚ ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """በመታወቂያ ተጠቃሚ ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_all_users() -> List[Dict]:
    """ሁሉንም ተጠቃሚዎች ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = cursor.fetchall()
    conn.close()
    return [dict(user) for user in users]

def update_user_role(telegram_id: int, role: str):
    """የተጠቃሚ ሚና ማሻሻል"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET role = ? WHERE telegram_id = ?', (role, telegram_id))
    conn.commit()
    conn.close()

def get_user_language(telegram_id: int) -> str:
    """የተጠቃሚ ቋንቋ ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT language FROM users WHERE telegram_id = ?', (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'am'

def update_user_language(telegram_id: int, language: str):
    """የተጠቃሚ ቋንቋ ማሻሻል"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = ? WHERE telegram_id = ?', (language, telegram_id))
    conn.commit()
    conn.close()

# ============================================
# የደራሲ ክወናዎች
# ============================================

def create_author(user_id: int) -> int:
    """አዲስ ደራሲ መፍጠር"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO authors (user_id) VALUES (?)
    ''', (user_id,))
    conn.commit()
    author_id = cursor.lastrowid
    conn.close()
    return author_id

def get_author_by_user(user_id: int) -> Optional[Dict]:
    """በተጠቃሚ መታወቂያ ደራሲ ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM authors WHERE user_id = ?', (user_id,))
    author = cursor.fetchone()
    conn.close()
    return dict(author) if author else None

def get_author_by_id(author_id: int) -> Optional[Dict]:
    """በደራሲ መታወቂያ ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM authors WHERE id = ?', (author_id,))
    author = cursor.fetchone()
    conn.close()
    return dict(author) if author else None

def get_all_authors() -> List[Dict]:
    """ሁሉንም ደራሲዎች ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM authors ORDER BY created_at DESC')
    authors = cursor.fetchall()
    conn.close()
    return [dict(author) for author in authors]

def update_author_level(author_id: int, level: str):
    """የደራሲ ደረጃ ማሻሻል"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE authors SET level = ?, is_verified = 1 WHERE id = ?', (level, author_id))
    conn.commit()
    conn.close()

def update_author_sales(author_id: int):
    """የደራሲ ሽያጭ ቆጣሪ መጨመር"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE authors SET total_sales = total_sales + 1 WHERE id = ?', (author_id,))
    conn.commit()
    conn.close()

# ============================================
# የይዘት ክወናዎች
# ============================================

def create_content(
    author_id: int, 
    title: str, 
    description: str, 
    category: str, 
    file_id: str, 
    price: float,
    sample_file_id: str = None
) -> int:
    """አዲስ ይዘት መፍጠር"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO content (author_id, title, description, category, file_id, sample_file_id, price, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
    ''', (author_id, title, description, category, file_id, sample_file_id, price))
    conn.commit()
    content_id = cursor.lastrowid
    conn.close()
    return content_id

def get_content(content_id: int) -> Optional[Dict]:
    """ይዘት ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM content WHERE id = ?', (content_id,))
    content = cursor.fetchone()
    conn.close()
    return dict(content) if content else None

def get_all_content() -> List[Dict]:
    """ሁሉንም ይዘቶች ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM content ORDER BY created_at DESC')
    content = cursor.fetchall()
    conn.close()
    return [dict(row) for row in content]

def get_published_content() -> List[Dict]:
    """የታተሙ ይዘቶችን ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, u.username as author_name 
        FROM content c
        JOIN authors a ON c.author_id = a.id
        JOIN users u ON a.user_id = u.id
        WHERE c.status = 'published'
        ORDER BY c.created_at DESC
    ''')
    content = cursor.fetchall()
    conn.close()
    return [dict(row) for row in content]

def get_pending_content() -> List[Dict]:
    """ለግምገማ የቀረቡ ይዘቶችን ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, u.username as author_name, u.full_name as author_full_name
        FROM content c
        JOIN authors a ON c.author_id = a.id
        JOIN users u ON a.user_id = u.id
        WHERE c.status = 'pending'
        ORDER BY c.created_at ASC
    ''')
    content = cursor.fetchall()
    conn.close()
    return [dict(row) for row in content]

def get_content_by_author(author_id: int) -> List[Dict]:
    """በደራሲ ይዘቶችን ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM content WHERE author_id = ? ORDER BY created_at DESC', (author_id,))
    content = cursor.fetchall()
    conn.close()
    return [dict(row) for row in content]

def update_content_status(content_id: int, status: str):
    """የይዘት ሁኔታ ማሻሻል"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE content SET status = ? WHERE id = ?', (status, content_id))
    if status == 'published':
        cursor.execute('UPDATE content SET published_at = CURRENT_TIMESTAMP WHERE id = ?', (content_id,))
    conn.commit()
    conn.close()

def increment_sales(content_id: int) -> int:
    """የሽያጭ ቁጥር መጨመር እና አዲሱን ቁጥር መመለስ"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE content SET total_sales = total_sales + 1 WHERE id = ? RETURNING total_sales', (content_id,))
    result = cursor.fetchone()
    conn.commit()
    conn.close()
    return result[0] if result else 0

def update_content_price(content_id: int, price: float):
    """የይዘት ዋጋ ማሻሻል"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE content SET price = ? WHERE id = ?', (price, content_id))
    conn.commit()
    conn.close()

# ============================================
# የግዢ ክወናዎች
# ============================================

def create_purchase(user_id: int, content_id: int, amount: float) -> int:
    """አዲስ ግዢ መፍጠር"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO purchases (user_id, content_id, amount, status)
        VALUES (?, ?, ?, 'completed')
    ''', (user_id, content_id, amount))
    conn.commit()
    purchase_id = cursor.lastrowid
    conn.close()
    return purchase_id

def get_all_purchases() -> List[Dict]:
    """ሁሉንም ግዢዎች ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, c.title, u.username 
        FROM purchases p
        JOIN content c ON p.content_id = c.id
        JOIN users u ON p.user_id = u.id
        ORDER BY p.purchased_at DESC
    ''')
    purchases = cursor.fetchall()
    conn.close()
    return [dict(purchase) for purchase in purchases]

def get_user_purchases(user_id: int) -> List[Dict]:
    """የተጠቃሚ ግዢዎችን ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, c.title, c.price 
        FROM purchases p
        JOIN content c ON p.content_id = c.id
        WHERE p.user_id = ?
        ORDER BY p.purchased_at DESC
    ''', (user_id,))
    purchases = cursor.fetchall()
    conn.close()
    return [dict(purchase) for purchase in purchases]

# ============================================
# የቤተ-መጽሐፍት ክወናዎች
# ============================================

def add_to_library(user_id: int, content_id: int):
    """ወደ ቤተ-መጽሐፍት መጨመር"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO library (user_id, content_id)
        VALUES (?, ?)
    ''', (user_id, content_id))
    conn.commit()
    conn.close()

def get_user_library(user_id: int) -> List[Dict]:
    """የተጠቃሚ ቤተ-መጽሐፍት ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, l.downloaded, l.last_downloaded_at
        FROM library l
        JOIN content c ON l.content_id = c.id
        WHERE l.user_id = ?
        ORDER BY l.created_at DESC
    ''', (user_id,))
    library = cursor.fetchall()
    conn.close()
    return [dict(row) for row in library]

def update_download_status(user_id: int, content_id: int):
    """የማውረድ ሁኔታ ማሻሻል"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE library 
        SET downloaded = 1, last_downloaded_at = CURRENT_TIMESTAMP
        WHERE user_id = ? AND content_id = ?
    ''', (user_id, content_id))
    conn.commit()
    conn.close()

# ============================================
# የሪፖርት ክወናዎች
# ============================================

def create_report(content_id: int, reporter_id: int, reason: str) -> int:
    """አዲስ ሪፖርት መፍጠር"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reports (content_id, reporter_id, reason, status)
        VALUES (?, ?, ?, 'pending')
    ''', (content_id, reporter_id, reason))
    conn.commit()
    report_id = cursor.lastrowid
    conn.close()
    return report_id

def get_reports(status: Optional[str] = None) -> List[Dict]:
    """ሪፖርቶችን ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    if status:
        cursor.execute('''
            SELECT r.*, c.title, u.username as reporter_name
            FROM reports r
            JOIN content c ON r.content_id = c.id
            JOIN users u ON r.reporter_id = u.id
            WHERE r.status = ?
            ORDER BY r.created_at DESC
        ''', (status,))
    else:
        cursor.execute('''
            SELECT r.*, c.title, u.username as reporter_name
            FROM reports r
            JOIN content c ON r.content_id = c.id
            JOIN users u ON r.reporter_id = u.id
            ORDER BY r.created_at DESC
        ''')
    reports = cursor.fetchall()
    conn.close()
    return [dict(report) for report in reports]

def get_report(report_id: int) -> Optional[Dict]:
    """አንድ ሪፖርት ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
    report = cursor.fetchone()
    conn.close()
    return dict(report) if report else None

def update_report_status(report_id: int, status: str, admin_notes: str = None):
    """የሪፖርት ሁኔታ ማሻሻል"""
    conn = get_db()
    cursor = conn.cursor()
    if admin_notes:
        cursor.execute('''
            UPDATE reports 
            SET status = ?, admin_notes = ?, resolved_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, admin_notes, report_id))
    else:
        cursor.execute('''
            UPDATE reports 
            SET status = ?, resolved_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, report_id))
    conn.commit()
    conn.close()

# ============================================
# የግምገማ ክወናዎች
# ============================================

def create_rating(user_id: int, content_id: int, rating: int, review: str = None):
    """ግምገማ መፍጠር"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO ratings (user_id, content_id, rating, review)
        VALUES (?, ?, ?, ?)
    ''', (user_id, content_id, rating, review))
    conn.commit()
    conn.close()

def get_content_ratings(content_id: int) -> List[Dict]:
    """የይዘት ግምገማዎችን ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, u.username
        FROM ratings r
        JOIN users u ON r.user_id = u.id
        WHERE r.content_id = ?
        ORDER BY r.created_at DESC
    ''', (content_id,))
    ratings = cursor.fetchall()
    conn.close()
    return [dict(rating) for rating in ratings]

def get_average_rating(content_id: int) -> float:
    """አማካይ ደረጃ ማግኘት"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT AVG(rating) FROM ratings WHERE content_id = ?', (content_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else 0
