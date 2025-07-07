import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters
from telegram.constants import ParseMode

from database import (
    get_user_stats, get_feedback, get_all_user_ids
)
from keyboards import (
    get_admin_menu_keyboard
)

logger = logging.getLogger(__name__)

from main import States

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != context.bot_data.get('ADMIN_USER_ID'):
            await update.message.reply_text("🚫 Du bist nicht berechtigt.")
            return ConversationHandler.END
        await update.message.reply_text("Bitte gib das Admin-Passwort ein:")
    except Exception as e:
        logger.error(f"Error in admin_command: {e}")
        await update.message.reply_text("Ein Fehler ist aufgetreten.")
    return States.ADMIN_LOGIN_PASSWORD

async def admin_password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.text == context.bot_data.get('ADMIN_PASSWORD'):
            await update.message.reply_text("✅ Admin-Login erfolgreich!", reply_markup=get_admin_menu_keyboard())
            return ConversationHandler.END
        else:
            await update.message.reply_text("❌ Falsches Passwort.")
            return States.ADMIN_LOGIN_PASSWORD
    except Exception as e:
        logger.error(f"Error in admin_password_handler: {e}")
        await update.message.reply_text("Ein Fehler ist aufgetreten.")
        return States.ADMIN_LOGIN_PASSWORD

async def admin_bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        stats = get_user_stats()
        text = f"📊 Bot Status\n\nGesamtzahl Nutzer: {stats['total_users']}\nNutzer mit Feedback: {stats['users_with_feedback']}\nGesamtzahl Produkte: {stats['total_products']}\nGesamtzahl Transaktionen: {stats['total_transactions']}"
        await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_admin_menu_keyboard())
    except Exception as e:
        logger.error(f"Error in admin_bot_status: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("Ein Fehler ist aufgetreten.", reply_markup=get_admin_menu_keyboard())

async def admin_read_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        feedbacks = get_feedback()
        if not feedbacks:
            await update.callback_query.edit_message_text("Kein Feedback verfügbar.", reply_markup=get_admin_menu_keyboard())
            return
        report = "**Feedback der Nutzer:**\n\n"
        for username, text, date in feedbacks[:10]:
            report += f"Von: {username} ({date[:10]})\n{text}\n---\n"
        await update.callback_query.edit_message_text(report, reply_markup=get_admin_menu_keyboard())
    except Exception as e:
        logger.error(f"Error in admin_read_feedback: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("Ein Fehler ist aufgetreten.", reply_markup=get_admin_menu_keyboard())

async def admin_check_news_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.callback_query.edit_message_text("Starte manuelle News-Prüfung...", reply_markup=get_admin_menu_keyboard())
        # Assuming check_and_post_news is imported or accessible
        await context.bot_data['check_and_post_news'](context)
        await update.callback_query.edit_message_text("Manuelle News-Prüfung abgeschlossen.", reply_markup=get_admin_menu_keyboard())
    except Exception as e:
        logger.error(f"Error in admin_check_news_manual: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("Ein Fehler ist aufgetreten.", reply_markup=get_admin_menu_keyboard())

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.effective_user.id != context.bot_data.get('ADMIN_USER_ID'):
            return ConversationHandler.END
        await update.callback_query.edit_message_text("Bitte sende mir die Nachricht für den Broadcast. Nutze /cancel zum Abbrechen.")
    except Exception as e:
        logger.error(f"Error in broadcast_start: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("Ein Fehler ist aufgetreten.")
    return States.ADMIN_BROADCAST_MESSAGE

async def broadcast_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['broadcast_message'] = update.message.text
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Ja", callback_data='yes'), InlineKeyboardButton("Nein", callback_data='no')]
        ])
        await update.message.reply_text(f"Vorschau:\n\n{update.message.text}\n\nSoll diese Nachricht an alle Nutzer gesendet werden?", reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in broadcast_message_handler: {e}")
        await update.message.reply_text("Ein Fehler ist aufgetreten.")
    return States.ADMIN_BROADCAST_CONFIRM

async def broadcast_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        if query.data == 'no':
            await update.edit_message_text("Broadcast abgebrochen.", reply_markup=get_admin_menu_keyboard())
            context.user_data.pop('broadcast_message', None)
            return ConversationHandler.END

        message = context.user_data.pop('broadcast_message', None)
        if not message:
            await update.edit_message_text("Fehler: Keine Nachricht gefunden.", reply_markup=get_admin_menu_keyboard())
            return ConversationHandler.END

        await update.edit_message_text("Sende Broadcast...")
        sent, failed = 0, 0
        for user_id in get_all_user_ids():
            try:
                await context.bot.send_message(chat_id=user_id, text=message)
                sent += 1
                await asyncio.sleep(0.1)
            except Exception:
                failed += 1
        await update.edit_message_text(f"Broadcast abgeschlossen!\nGesendet: {sent}\nFehlgeschlagen: {failed}", reply_markup=get_admin_menu_keyboard())
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in broadcast_confirm_handler: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("Ein Fehler ist aufgetreten.", reply_markup=get_admin_menu_keyboard())
        return ConversationHandler.END
