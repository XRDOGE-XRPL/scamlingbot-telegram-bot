import logging
import datetime
from database import get_user_internal_balance, get_user_products, get_wallet_transactions, get_affiliate_stats
from telegram import ParseMode

logger = logging.getLogger(__name__)

async def send_daily_summary(context):
    user_id = context.job.chat_id
    try:
        balance = get_user_internal_balance(user_id)
        products = get_user_products(user_id)
        transactions = get_wallet_transactions(user_id, limit=5)
        affiliate_stats = get_affiliate_stats(user_id)

        product_count = len(products) if products else 0
        transaction_count = len(transactions) if transactions else 0

        message = f"📅 Dein tägliches Summary für {datetime.date.today()}:\n\n"
        message += f"💰 Internes Guthaben: {balance:.2f} SCAMCOIN\n"
        message += f"🛍️ Anzahl deiner Produkte im Marktplatz: {product_count}\n"
        message += f"📜 Letzte {transaction_count} Transaktionen:\n"
        for tx in transactions:
            if len(tx) == 5:
                amount, tx_type, currency, timestamp, description = tx
            else:
                amount, tx_type, timestamp, description = tx
                currency = ""
            message += f"- {timestamp}: {tx_type} {amount} {currency} - {description}\n"
        message += f"\n📈 Affiliate Statistiken:\n"
        message += f"- Klicks: {affiliate_stats['clicks']}\n"
        message += f"- Verkäufe: {affiliate_stats['sales_count']}\n"
        message += f"- Einnahmen: {affiliate_stats['total_revenue']:.2f} SCAMCOIN\n"

        await context.bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Fehler beim Senden des täglichen Summary an Nutzer {user_id}: {e}")
