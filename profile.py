import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)
DB_NAME = 'scamlingbot.db'

# Conversation states for profile management
PROFILE_VIEW, PROFILE_EDIT_NAME, PROFILE_EDIT_USERNAME = range(3)

def get_user_profile(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT first_name, last_name, username FROM users WHERE id = ?', (user_id,))
    profile = cursor.fetchone()
    conn.close()
    return profile

def update_user_profile(user_id: int, first_name: str = None, last_name: str = None, username: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if first_name:
        cursor.execute('UPDATE users SET first_name = ? WHERE id = ?', (first_name, user_id))
    if last_name:
        cursor.execute('UPDATE users SET last_name = ? WHERE id = ?', (last_name, user_id))
    if username:
        cursor.execute('UPDATE users SET username = ? WHERE id = ?', (username, user_id))
    conn.commit()
    conn.close()

async def profile_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)
    if not profile:
        await update.message.reply_text("Profil nicht gefunden.")
        return ConversationHandler.END
    first_name, last_name, username = profile
    text = f"Dein Profil:\n\nVorname: {first_name or ''}\nNachname: {last_name or ''}\nBenutzername: @{username or ''}"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Vorname bearbeiten", callback_data='edit_first_name')],
        [InlineKeyboardButton("Nachname bearbeiten", callback_data='edit_last_name')],
        [InlineKeyboardButton("Benutzername bearbeiten", callback_data='edit_username')],
        [InlineKeyboardButton("Zurück", callback_data='back_to_main_menu')]
    ])
    await update.message.reply_text(text, reply_markup=keyboard)
    return PROFILE_VIEW

async def profile_edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == 'edit_first_name':
        await query.edit_message_text("Bitte gib deinen neuen Vornamen ein:")
        context.user_data['edit_field'] = 'first_name'
    elif data == 'edit_last_name':
        await query.edit_message_text("Bitte gib deinen neuen Nachnamen ein:")
        context.user_data['edit_field'] = 'last_name'
    elif data == 'edit_username':
        await query.edit_message_text("Bitte gib deinen neuen Benutzernamen ein (ohne @):")
        context.user_data['edit_field'] = 'username'
    else:
        await query.edit_message_text("Unbekannte Aktion.", reply_markup=None)
        return ConversationHandler.END
    return PROFILE_EDIT_NAME

async def profile_edit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    field = context.user_data.get('edit_field')
    new_value = update.message.text.strip()
    if not field or not new_value:
        await update.message.reply_text("Ungültige Eingabe. Bitte erneut versuchen.")
        return PROFILE_EDIT_NAME
    if field == 'first_name':
        update_user_profile(user_id, first_name=new_value)
    elif field == 'last_name':
        update_user_profile(user_id, last_name=new_value)
    elif field == 'username':
        update_user_profile(user_id, username=new_value)
    else:
        await update.message.reply_text("Unbekanntes Feld.")
        return ConversationHandler.END
    await update.message.reply_text("Profil erfolgreich aktualisiert.")
    return await profile_view(update, context)

async def profile_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Aktion abgebrochen.")
    return ConversationHandler.END
