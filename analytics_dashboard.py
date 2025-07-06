import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)
DB_NAME = 'scamlingbot.db'

def get_usage_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(DISTINCT id) FROM users')
        total_users = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM feedback')
        total_feedback = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM products')
        total_products = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM transactions')
        total_transactions = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM wallets')
        total_wallets = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM pools')
        total_pools = cursor.fetchone()[0]
        return {
            'total_users': total_users,
            'total_feedback': total_feedback,
            'total_products': total_products,
            'total_transactions': total_transactions,
            'total_wallets': total_wallets,
            'total_pools': total_pools
        }
    except Exception as e:
        logger.error(f"Error fetching usage stats: {e}")
        return {}
    finally:
        conn.close()

async def analytics_dashboard_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_usage_stats()
    if not stats:
        await update.message.reply_text("Keine Nutzungsdaten verfügbar.")
        return
    text = (
        f"📊 Analytics Dashboard:\n\n"
        f"Gesamtzahl Nutzer: {stats.get('total_users', 0)}\n"
        f"Gesamtzahl Feedback: {stats.get('total_feedback', 0)}\n"
        f"Gesamtzahl Produkte: {stats.get('total_products', 0)}\n"
        f"Gesamtzahl Transaktionen: {stats.get('total_transactions', 0)}\n"
        f"Gesamtzahl Wallets: {stats.get('total_wallets', 0)}\n"
        f"Gesamtzahl Pools: {stats.get('total_pools', 0)}"
    )
    await update.message.reply_text(text)
