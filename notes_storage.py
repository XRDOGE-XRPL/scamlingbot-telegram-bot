import sqlite3
import logging

logger = logging.getLogger(__name__)
DB_NAME = 'scamlingbot.db'

def init_notes_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            note TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_user_note(user_id: int, note: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO user_notes (user_id, note) VALUES (?, ?)', (user_id, note))
        conn.commit()
    except Exception as e:
        logger.error(f"Error adding user note: {e}")
    finally:
        conn.close()

def get_user_notes(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, note, created_at FROM user_notes WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        notes = cursor.fetchall()
        return notes
    except Exception as e:
        logger.error(f"Error fetching user notes: {e}")
        return []
    finally:
        conn.close()
