import sqlite3
import logging

logger = logging.getLogger(__name__)
DB_NAME = 'scamlingbot.db'

def init_affiliate_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Table to track affiliate link clicks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS affiliate_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_name TEXT,
            click_time TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Table to track affiliate sales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS affiliate_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_name TEXT,
            sale_amount REAL,
            sale_time TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def log_affiliate_click(user_id: int, product_name: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO affiliate_clicks (user_id, product_name)
            VALUES (?, ?)
        ''', (user_id, product_name))
        conn.commit()
    except Exception as e:
        logger.error(f"Error logging affiliate click: {e}")
    finally:
        conn.close()

def log_affiliate_sale(user_id: int, product_name: str, sale_amount: float):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO affiliate_sales (user_id, product_name, sale_amount)
            VALUES (?, ?, ?)
        ''', (user_id, product_name, sale_amount))
        conn.commit()
    except Exception as e:
        logger.error(f"Error logging affiliate sale: {e}")
    finally:
        conn.close()

def get_affiliate_stats(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(*) FROM affiliate_clicks WHERE user_id = ?', (user_id,))
        clicks = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*), SUM(sale_amount) FROM affiliate_sales WHERE user_id = ?', (user_id,))
        sales_data = cursor.fetchone()
        sales_count = sales_data[0] if sales_data[0] else 0
        total_revenue = sales_data[1] if sales_data[1] else 0.0
        return {
            'clicks': clicks,
            'sales_count': sales_count,
            'total_revenue': total_revenue
        }
    except Exception as e:
        logger.error(f"Error fetching affiliate stats: {e}")
        return {
            'clicks': 0,
            'sales_count': 0,
            'total_revenue': 0.0
        }
    finally:
        conn.close()
