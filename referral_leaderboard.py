import sqlite3
import logging

logger = logging.getLogger(__name__)
DB_NAME = 'scamlingbot.db'

def get_top_referrers(limit=10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT user_id, COUNT(*) as referral_count, SUM(sale_amount) as total_revenue
            FROM affiliate_sales
            GROUP BY user_id
            ORDER BY total_revenue DESC
            LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        return results
    except Exception as e:
        logger.error(f"Error fetching top referrers: {e}")
        return []
    finally:
        conn.close()

async def referral_leaderboard_handler(update, context):
    top_referrers = get_top_referrers()
    if not top_referrers:
        await update.message.reply_text("Keine Daten für das Referral Leaderboard verfügbar.")
        return

    text = "🏆 Referral Leaderboard:\n\n"
    rank = 1
    for user_id, count, revenue in top_referrers:
        text += f"{rank}. Nutzer {user_id} - Verkäufe: {count}, Einnahmen: {revenue:.2f} SCAMCOIN\n"
        rank += 1

    await update.message.reply_text(text)
