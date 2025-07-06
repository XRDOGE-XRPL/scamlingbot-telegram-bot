import logging
import re
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

logger = logging.getLogger(__name__)

# Basic spam detection rules
SPAM_PATTERNS = [
    r"(free\s+money)",
    r"(click\s+here)",
    r"(buy\s+now)",
    r"(subscribe\s+now)",
    r"(visit\s+this\s+link)",
    r"(http[s]?://\S+)",  # URLs
    r"(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)",  # Emails
]

def is_spam(text: str) -> bool:
    text_lower = text.lower()
    for pattern in SPAM_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False

async def spam_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return
    if is_spam(message.text):
        try:
            await message.delete()
            await message.reply_text("Deine Nachricht wurde als Spam erkannt und gelöscht.")
            logger.info(f"Deleted spam message from user {message.from_user.id}")
        except Exception as e:
            logger.error(f"Failed to delete spam message: {e}")
