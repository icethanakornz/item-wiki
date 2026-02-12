import sqlite3
import os
from contextlib import contextmanager

DB_PATH = "item_wiki.db"


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """สร้างตารางในฐานข้อมูล"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # ตาราง items (ข้อมูลไอเท็มจริง)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                rarity TEXT NOT NULL,
                drop_location TEXT NOT NULL,
                tier TEXT NOT NULL,
                description TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ✅ ตาราง master_data (เก็บข้อมูลประเภท, ความหายาก, สถานที่ดรอป, Tier)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS master_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,  -- 'type', 'rarity', 'location', 'tier'
                value TEXT NOT NULL,
                color TEXT,              -- สำหรับความหายาก (เก็บสี)
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, value)
            )
        ''')

        # ✅ เพิ่มข้อมูลเริ่มต้น (ถ้ายังไม่มี)
        # ประเภทไอเท็มเริ่มต้น
        default_types = ["อาวุธ", "เกราะ", "เครื่องประดับ", "เครื่องราง", "อื่นๆ"]
        for idx, type_name in enumerate(default_types):
            cursor.execute('''
                INSERT OR IGNORE INTO master_data (category, value, sort_order)
                VALUES (?, ?, ?)
            ''', ('type', type_name, idx))

        # ความหายากเริ่มต้น
        default_rarities = [
            ("Common", "#808080", 0),
            ("Uncommon", "#27ae60", 1),
            ("Rare", "#2980b9", 2),
            ("Epic", "#8e44ad", 3),
            ("Legendary", "#f39c12", 4)
        ]
        for rarity, color, idx in default_rarities:
            cursor.execute('''
                INSERT OR IGNORE INTO master_data (category, value, color, sort_order)
                VALUES (?, ?, ?, ?)
            ''', ('rarity', rarity, color, idx))

        # สถานที่ดรอปเริ่มต้น
        default_locations = ["ดันเจี้ยนไฟ", "ป่าลึกลับ", "ยอดเขา", "ถ้ำแมงมุม", "รังมังกร"]
        for idx, loc in enumerate(default_locations):
            cursor.execute('''
                INSERT OR IGNORE INTO master_data (category, value, sort_order)
                VALUES (?, ?, ?)
            ''', ('location', loc, idx))

        # Tier เริ่มต้น
        default_tiers = ["T1", "T2", "T3", "T4"]
        for idx, tier in enumerate(default_tiers):
            cursor.execute('''
                INSERT OR IGNORE INTO master_data (category, value, sort_order)
                VALUES (?, ?, ?)
            ''', ('tier', tier, idx))

        conn.commit()


def execute_query(query, params=(), fetch_one=False):
    """รันคำสั่ง SQL และคืนค่าผลลัพธ์"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)

        if query.strip().upper().startswith('SELECT'):
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.lastrowid


def check_duplicate_name(name, exclude_id=None):
    """ตรวจสอบชื่อไอเท็มซ้ำ"""
    if exclude_id:
        query = "SELECT COUNT(*) as count FROM items WHERE LOWER(name) = LOWER(?) AND id != ?"
        result = execute_query(query, (name.strip(), exclude_id), fetch_one=True)
    else:
        query = "SELECT COUNT(*) as count FROM items WHERE LOWER(name) = LOWER(?)"
        result = execute_query(query, (name.strip(),), fetch_one=True)
    return result['count'] > 0 if result else False


# ===== ฟังก์ชันสำหรับจัดการ Master Data =====

def get_master_data(category):
    """ดึงข้อมูล master data ตามหมวดหมู่"""
    query = """
        SELECT * FROM master_data 
        WHERE category = ? 
        ORDER BY sort_order, value
    """
    return execute_query(query, (category,))


def add_master_data(category, value, color=None):
    """เพิ่มข้อมูล master data"""
    try:
        # หา sort_order ล่าสุด
        max_order = execute_query("""
            SELECT MAX(sort_order) as max_order 
            FROM master_data 
            WHERE category = ?
        """, (category,), fetch_one=True)
        next_order = (max_order['max_order'] or 0) + 1

        query = '''
            INSERT INTO master_data (category, value, color, sort_order)
            VALUES (?, ?, ?, ?)
        '''
        return execute_query(query, (category, value.strip(), color, next_order))
    except Exception as e:
        print(f"Error adding master data: {e}")
        return None


def delete_master_data(category, value):
    """ลบข้อมูล master data"""
    try:
        # ตรวจสอบว่ามีไอเท็มที่ใช้ข้อมูลนี้หรือไม่
        if category == 'type':
            check_query = "SELECT COUNT(*) as count FROM items WHERE type = ?"
        elif category == 'rarity':
            check_query = "SELECT COUNT(*) as count FROM items WHERE rarity = ?"
        elif category == 'location':
            check_query = "SELECT COUNT(*) as count FROM items WHERE drop_location = ?"
        elif category == 'tier':
            check_query = "SELECT COUNT(*) as count FROM items WHERE tier = ?"
        else:
            return False

        result = execute_query(check_query, (value,), fetch_one=True)
        if result and result['count'] > 0:
            return False  # มีไอเท็มใช้งานอยู่

        # ลบข้อมูล
        query = "DELETE FROM master_data WHERE category = ? AND value = ?"
        execute_query(query, (category, value))
        return True
    except Exception as e:
        print(f"Error deleting master data: {e}")
        return False


def update_master_data_color(category, value, color):
    """อัปเดตสีของความหายาก"""
    try:
        query = "UPDATE master_data SET color = ? WHERE category = ? AND value = ?"
        execute_query(query, (color, category, value))
        return True
    except Exception as e:
        print(f"Error updating color: {e}")
        return False
