import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters
from telegram.constants import ParseMode

from database import (
    add_user_wallet, get_user_wallets, remove_user_wallet,
    get_user_internal_balance, update_user_internal_balance
)
from wallet_history import (
    init_wallet_history_table, log_wallet_transaction, get_wallet_transactions
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

async def internal_transfer_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.callback_query.edit_message_text("Bitte gib die Nutzer-ID des Empfängers ein:")
    except Exception as e:
        logger.error(f"Error in internal_transfer_start: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("Ein Fehler ist aufgetreten.")
    return States.INTERNAL_TRANSFER_RECEIVER

async def internal_transfer_receiver_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        receiver_id_text = update.message.text.strip()
        if not receiver_id_text.isdigit():
            await update.message.reply_text("Ungültige Nutzer-ID. Bitte gib eine gültige Zahl ein.")
            return States.INTERNAL_TRANSFER_RECEIVER
        context.user_data['transfer_receiver_id'] = int(receiver_id_text)
        await update.message.reply_text("Bitte gib den Betrag ein, den du überweisen möchtest:")
    except Exception as e:
        logger.error(f"Error in internal_transfer_receiver_handler: {e}")
        await update.message.reply_text("Ein Fehler ist aufgetreten. Bitte versuche es später erneut.")
        return States.INTERNAL_TRANSFER_RECEIVER
    return States.INTERNAL_TRANSFER_AMOUNT

async def internal_transfer_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Ungültiger Betrag. Bitte gib eine positive Zahl ein.")
        return States.INTERNAL_TRANSFER_AMOUNT

    sender_id = update.effective_user.id
    receiver_id = context.user_data.get('transfer_receiver_id')
    sender_balance = get_user_internal_balance(sender_id)

    if amount > sender_balance:
        await update.message.reply_text(f"Unzureichendes Guthaben. Dein aktuelles Guthaben: {sender_balance:.2f} SCAMCOIN.")
        return States.INTERNAL_TRANSFER_AMOUNT

    # Update balances
    if update_user_internal_balance(sender_id, -amount) and update_user_internal_balance(receiver_id, amount):
        log_wallet_transaction(sender_id, "SCAMCOIN", -amount, "transfer", f"Überweisung an Nutzer {receiver_id}")
        log_wallet_transaction(receiver_id, "SCAMCOIN", amount, "transfer", f"Empfang von Nutzer {sender_id}")
        await update.message.reply_text(f"✅ Überweisung von {amount:.2f} SCAMCOIN an Nutzer {receiver_id} erfolgreich.")
    else:
        await update.message.reply_text("❌ Fehler bei der Überweisung. Bitte versuche es später erneut.")

    return ConversationHandler.END
from keyboards import (
    get_my_wallets_menu_keyboard, get_personal_area_menu_keyboard
)

async def wallet_transaction_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    transactions = get_wallet_transactions(user_id)
    if not transactions:
        await query.edit_message_text("Keine Transaktionen gefunden.", reply_markup=await get_my_wallets_menu_keyboard(context))
        return

    text = "Letzte Wallet-Transaktionen:\n\n"
    for tx in transactions:
        if len(tx) == 5:
            amount, tx_type, currency, timestamp, description = tx
        else:
            amount, tx_type, timestamp, description = tx
            currency = ""
        text += f"{timestamp}: {tx_type} {amount} {currency} - {description}\n"

    await query.edit_message_text(text, reply_markup=await get_my_wallets_menu_keyboard(context))

logger = logging.getLogger(__name__)

from main import States

async def my_wallets_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    wallets = get_user_wallets(query.from_user.id)
    internal_balance = get_user_internal_balance(query.from_user.id)

    text = "Deine registrierten Wallets:\n\n"
    text += f"▪️ Internes Guthaben: `{internal_balance:.2f} SCAMCOIN`\n"

    if wallets:
        text += "\nExterne Wallets:\n"
        text += "\n".join([f"▪️ {currency}: `{address}`" for _, currency, address in wallets])
    else:
        text += "Noch keine externen Wallets registriert."

    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=await get_my_wallets_menu_keyboard(context))

async def add_wallet_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.callback_query.edit_message_text("Gib die Währung der Wallet ein (z.B. BTC, ETH):")
    except Exception as e:
        logger.error(f"Error in add_wallet_start: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("Ein Fehler ist aufgetreten.")
    return States.ADD_WALLET_CURRENCY

async def add_wallet_currency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['wallet_currency'] = update.message.text.strip().upper()
        await update.message.reply_text(f"Gib nun die Wallet-Adresse für **{context.user_data['wallet_currency']}** ein:")
    except Exception as e:
        logger.error(f"Error in add_wallet_currency_handler: {e}")
        await update.message.reply_text("Ein Fehler ist aufgetreten. Bitte versuche es später erneut.")
        return States.ADD_WALLET_CURRENCY
    return States.ADD_WALLET_ADDRESS

async def add_wallet_address_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        address = update.message.text.strip()
        currency = context.user_data.pop('wallet_currency')
        user_id = update.effective_user.id
        if add_user_wallet(user_id, currency, address):
            # Log wallet addition as a transaction
            log_wallet_transaction(user_id, currency, 0.0, 'add_wallet', f'Added wallet {address}')
            await update.message.reply_text(f"✅ Wallet für **{currency}** wurde hinzugefügt!", parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text("❌ Fehler: Diese Wallet existiert bereits.")
        await my_wallets_menu(update, context)
    except Exception as e:
        logger.error(f"Error in add_wallet_address_handler: {e}")
        await update.message.reply_text("Ein Fehler ist aufgetreten. Bitte versuche es später erneut.")
    return ConversationHandler.END

async def remove_wallet_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        wallets = get_user_wallets(query.from_user.id)
        if not wallets:
            await query.answer("Du hast keine Wallets zum Entfernen.", show_alert=True)
            return ConversationHandler.END
        keyboard = [[InlineKeyboardButton(f"{currency}: {address[:10]}...", callback_data=f"del_wallet_{wid}")] for wid, currency, address in wallets]
        keyboard.append([InlineKeyboardButton("Abbrechen", callback_data="cancel_action")])
        await query.edit_message_text("Wähle die Wallet zum Entfernen:", reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        logger.error(f"Error in remove_wallet_start: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("Ein Fehler ist aufgetreten.")
    return States.REMOVE_WALLET_SELECT

async def remove_wallet_select_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        if query.data == "cancel_action":
            await my_wallets_menu(query, context)
            return ConversationHandler.END
        wallet_id = int(query.data.replace("del_wallet_", ""))
        user_id = query.from_user.id
        if remove_user_wallet(wallet_id, user_id):
            # Log wallet removal as a transaction
            log_wallet_transaction(user_id, '', 0.0, 'remove_wallet', f'Removed wallet id {wallet_id}')
            await query.answer("Wallet entfernt.", show_alert=True)
        else:
            await query.answer("Fehler beim Entfernen.", show_alert=True)
        await my_wallets_menu(query, context)
    except Exception as e:
        logger.error(f"Error in remove_wallet_select_handler: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("Ein Fehler ist aufgetreten.")
    return ConversationHandler.END
