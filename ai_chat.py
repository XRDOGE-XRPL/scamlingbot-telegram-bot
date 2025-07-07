from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters
from telegram.constants import ParseMode
from localization import T
from keyboards import get_main_menu_keyboard
import logging

logger = logging.getLogger(__name__)

# Conversation states
AI_CHAT_MENU, AI_CHAT_ACTIVE, AI_CHAT_CREATE_IMAGE, AI_CHAT_NOTES = range(4)

async def ai_chat_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Chat starten", callback_data='start_chat')],
            [InlineKeyboardButton("Erstelle Bilder", callback_data='create_image')],
            [InlineKeyboardButton("Notizen", callback_data='notes')],
            [InlineKeyboardButton("Zurück", callback_data='back_to_main_menu')]
        ])
        if update.callback_query:
            await update.callback_query.edit_message_text("Willkommen im KI-Chat! Wähle eine Option:", reply_markup=keyboard)
        else:
            await update.message.reply_text("Willkommen im KI-Chat! Wähle eine Option:", reply_markup=keyboard)
        return AI_CHAT_MENU
    except Exception as e:
        logger.error(f"Error in ai_chat_menu: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("Ein Fehler ist aufgetreten.")
        else:
            await update.message.reply_text("Ein Fehler ist aufgetreten.")
        return AI_CHAT_MENU

async def ai_chat_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        data = query.data

        if data == 'start_chat':
            await query.edit_message_text("Du sprichst jetzt mit der KI. Stelle eine Frage oder schreibe eine Nachricht.\nBenutze /cancel, um den Chat zu beenden.")
            return AI_CHAT_ACTIVE
        elif data == 'create_image':
            await query.edit_message_text("Bitte beschreibe das Bild, das du erstellen möchtest:")
            return AI_CHAT_CREATE_IMAGE
        elif data == 'notes':
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Notiz hinzufügen", callback_data='add_note')],
                [InlineKeyboardButton("Notizen anzeigen", callback_data='show_notes')],
                [InlineKeyboardButton("Zurück", callback_data='ai_chat_menu')]
            ])
            await query.edit_message_text("Notizbereich: Wähle eine Option:", reply_markup=keyboard)
            return AI_CHAT_NOTES
        elif data == 'add_note':
            await query.edit_message_text("Schreibe deine Notiz. Benutze /cancel zum Beenden.")
            return AI_CHAT_NOTES
        elif data == 'show_notes':
            from ai_chat import ai_chat_show_notes_handler
            return await ai_chat_show_notes_handler(update, context)
        elif data == 'back_to_main_menu':
            from main import main_menu_view
            return await main_menu_view(update, context)
        else:
            await query.edit_message_text("Unbekannte Option.")
            return AI_CHAT_MENU
    except Exception as e:
        logger.error(f"Error in ai_chat_menu_handler: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("Ein Fehler ist aufgetreten.")
        else:
            await update.message.reply_text("Ein Fehler ist aufgetreten.")
        return AI_CHAT_MENU

async def ai_chat_active_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text.lower()
        if "wie geht es" in user_message:
            response = "Mir geht es als Bot immer ausgezeichnet! Wie kann ich dir helfen?"
        elif "wer bist du" in user_message:
            response = "Ich bin der ScamlingBot, eine Kreation, die dir bei vielen Aufgaben helfen soll."
        elif "wie ist das wetter" in user_message:
            get_weather_info = context.bot_data.get('get_weather_info')
            if get_weather_info:
                response = await get_weather_info(user_message)
            else:
                response = "Wetterdienst nicht verfügbar."
        else:
            response = f"Ich verarbeite deine Nachricht: '{update.message.text}'.\n(Dies ist eine Simulation.)"
        await update.message.reply_text(f"🤖 {response}")
        return AI_CHAT_ACTIVE
    except Exception as e:
        logger.error(f"Error in ai_chat_active_handler: {e}")
        await update.message.reply_text("Ein Fehler ist aufgetreten.")
        return AI_CHAT_ACTIVE

async def ai_chat_create_image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        description = update.message.text
        await update.message.reply_text(f"Bild wird erstellt mit Beschreibung: {description}\n(Dies ist eine Simulation.)")
        return AI_CHAT_MENU
    except Exception as e:
        logger.error(f"Error in ai_chat_create_image_handler: {e}")
        await update.message.reply_text("Ein Fehler ist aufgetreten.")
        return AI_CHAT_MENU

from notes_storage import add_user_note, get_user_notes

async def ai_chat_notes_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        note = update.message.text
        user_id = update.effective_user.id
        add_user_note(user_id, note)
        await update.message.reply_text(f"Notiz gespeichert: {note}")
        return AI_CHAT_MENU
    except Exception as e:
        logger.error(f"Error in ai_chat_notes_handler: {e}")
        await update.message.reply_text("Ein Fehler ist aufgetreten.")
        return AI_CHAT_MENU

async def ai_chat_show_notes_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        notes = get_user_notes(user_id)
        if not notes:
            await update.message.reply_text("Du hast keine gespeicherten Notizen.")
            return AI_CHAT_MENU
        text = "Deine Notizen:\n\n"
        for note_id, note_text, created_at in notes:
            text += f"- {created_at}: {note_text}\n"
        await update.message.reply_text(text)
        return AI_CHAT_MENU
    except Exception as e:
        logger.error(f"Error in ai_chat_show_notes_handler: {e}")
        await update.message.reply_text("Ein Fehler ist aufgetreten.")
        return AI_CHAT_MENU

async def ai_chat_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("KI-Chat beendet.", reply_markup=await get_main_menu_keyboard(context))
    except Exception as e:
        logger.error(f"Error in ai_chat_cancel: {e}")
        await update.message.reply_text("Ein Fehler ist aufgetreten.")
    return ConversationHandler.END
