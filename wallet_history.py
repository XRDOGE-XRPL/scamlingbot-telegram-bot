import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
DB_NAME = 'scamlingbot.db'

def init_wallet_history_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wallet_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            currency TEXT NOT NULL,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL, -- e.g., 'deposit', 'withdrawal', 'purchase', 'sale'
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_wallet_transaction(user_id: int, currency: str, amount: float, transaction_type: str, description: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO wallet_transactions (user_id, currency, amount, transaction_type, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, currency, amount, transaction_type, description))
        conn.commit()
    except Exception as e:
        logger.error(f"Error logging wallet transaction: {e}")
    finally:
        conn.close()

def get_wallet_transactions(user_id: int, currency: str = None, limit: int = 50):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        if currency:
            cursor.execute('''
                SELECT amount, transaction_type, timestamp, description
                FROM wallet_transactions
                WHERE user_id = ? AND currency = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, currency, limit))
        else:
            cursor.execute('''
                SELECT amount, transaction_type, currency, timestamp, description
                FROM wallet_transactions
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        logger.error(f"Error fetching wallet transactions: {e}")
        return []
    finally:
        conn.close()
