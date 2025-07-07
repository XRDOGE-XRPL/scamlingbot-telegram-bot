# =================================================================================
# SCAMLINGBOT - VERSION 13.8 (FUNKTIONSERWEITERUNG: MARKTPLATZ)
# =================================================================================
# Diese Version erweitert den Bot um eine Marktplatz-Funktionalität für digitale Güter.
# Es wird ein internes Währungssystem für den Handel implementiert.
# =================================================================================

import os
import asyncio
import logging
import datetime
import json
import feedparser
import urllib.parse
import random
import hmac
import hashlib
from typing import Final, Callable, Awaitable

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode
from telegram.error import TelegramError

# Imports der modularen Dateien
from localization import T # Korrektur: get_lang entfernt
from database import (
    init_db, add_user_to_db, set_user_language, get_user_language_from_db,
    add_feedback, get_feedback, get_user_stats, get_all_user_ids,
    add_user_wallet, get_user_wallets, remove_user_wallet,
    add_user_pool, get_user_pools, remove_user_pool,
    mark_news_item_as_sent, check_if_news_item_sent,
    # NEU: Marktplatz-Funktionen aus der Datenbank
    add_product, get_all_active_products, get_product_by_id,
    process_transaction, get_user_products,
    # NEU: Wallet-Balance für internes System
    get_user_internal_balance, update_user_internal_balance
)
from keyboards import (
    get_main_menu_keyboard, get_geld_verdienen_menu_keyboard,
    get_krypto_swap_menu_keyboard, get_bilder_verkaufen_menu_keyboard,
    get_affiliate_links_menu_keyboard, get_tools_menu_keyboard,
    get_personal_area_menu_keyboard, get_my_wallets_menu_keyboard,
    get_my_pools_menu_keyboard, get_admin_menu_keyboard,
    # NEU: Marktplatz-Keyboards
    get_marketplace_menu_keyboard
)
from news_service import (
    check_and_post_news, NEWS_CHECK_INTERVAL_SECONDS,
    NEWS_FEED_URL, NEWS_MAX_TO_POST_PER_CHECK
)

# Import der API-Service-Funktionen
from services import (
    fetch_ethermine_stats, get_exchange_rate,
    fetch_crypto_prices_coingecko, get_single_crypto_price,
    get_weather_info, fetch_wallet_balance_blockchair,
    fetch_xrpl_account_info,
    fetch_publicpool_btc_stats,
    fetch_viabtc_btc_stats,
    # NEU: Placeholder für zukünftige externe Krypto-Transaktionen
    simulate_crypto_deposit, simulate_crypto_withdrawal
)


# =================================================================================
# 1. KONFIGURATION
# =================================================================================

# --- Logging-Einrichtung ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Lade sensible Daten aus Umgebungsvariablen oder nutze Fallbacks ---
BOT_TOKEN: Final[str] = os.environ.get("BOT_TOKEN", "7810871736:AAG1aECXYb5d08CQ_VXC5s-HmOkKtWuHrg0")
GROUP_CHAT_ID: Final[int] = int(os.environ.get("GROUP_CHAT_ID", -1002830458019))
ADMIN_USER_ID: Final[int] = int(os.environ.get("ADMIN_USER_ID", 5096684838))
ADMIN_PASSWORD: Final[str] = os.environ.get("ADMIN_PASSWORD", "your_secure_admin_password")

# --- Globale Marktplatz-Gebühr ---
MARKETPLACE_FEE_PERCENTAGE: Final[float] = 0.01 # 1%

# --- Zustände für ConversationHandler ---
class States:
    (
        CALCULATOR_FIRST_NUMBER, CALCULATOR_OPERATOR, CALCULATOR_SECOND_NUMBER,
        WEATHER_LOCATION,
        IMAGE_UPLOAD_RECEIVE, IMAGE_UPLOAD_DESCRIPTION,
        SWAP_SELECT_FROM, SWAP_SELECT_TO, SWAP_AMOUNT, SWAP_ADDRESS, SWAP_CONFIRM,
        AFFILIATE_PRODUCT_NAME,
        ADD_WALLET_CURRENCY, ADD_WALLET_ADDRESS, REMOVE_WALLET_SELECT,
        ADD_POOL_CRYPTO, # Auswahl der Krypto für Pool
        ADD_POOL_ADDRESS, # Wird nach ADD_POOL_CRYPTO genutzt
        REMOVE_POOL_SELECT,
        CHECK_POOL_STATS_SELECT, # Für nutzerspezifische Pool-Stats
        # NEU: Zustand für allgemeine Pool-Statistik-Auswahl
        GENERAL_POOL_STATS_SELECTION,
        ADMIN_LOGIN_PASSWORD, ADMIN_BROADCAST_MESSAGE, ADMIN_BROADCAST_CONFIRM,
        AI_CHAT_ACTIVE,
        FEEDBACK_MESSAGE,
        CRYPTO_GAME_ACTION,
        XRPL_ADDRESS_INPUT,
        # NEU: Zustände für den Marktplatz (Produkt einstellen)
        MARKETPLACE_ADD_PRODUCT_NAME,
        MARKETPLACE_ADD_PRODUCT_DESCRIPTION,
        MARKETPLACE_ADD_PRODUCT_PRICE,
        MARKETPLACE_ADD_PRODUCT_FILE, # Für den Upload der digitalen Datei
        MARKETPLACE_ADD_PRODUCT_CONFIRM,
        # NEU: Zustände für den Marktplatz (Produkt kaufen)
        MARKETPLACE_VIEW_PRODUCT, # Wenn ein spezifisches Produkt angezeigt wird
        MARKETPLACE_CONFIRM_BUY,
        # NEU: Zustände für das Aufladen/Abheben der internen Wallet
        INTERNAL_WALLET_DEPOSIT_AMOUNT,
        INTERNAL_WALLET_WITHDRAW_AMOUNT
    ) = range(36) # Die Gesamtzahl der Zustände (27 bestehende + 9 neue = 36)

# =================================================================================
# 2. LOKALISIERUNG & TEXTE (AUSGELAGERT IN 'localization.py')
# =================================================================================

# =================================================================================
# 3. DATENBANKFUNKTIONEN (AUSGELAGERT IN 'database.py')
# =================================================================================

# =================================================================================
# 4. KEYBOARD-GENERATOREN (AUSGELAGERT IN 'keyboards.py')
# =================================================================================


# =================================================================================
# 5. AUTOMATISIERTE JOBS & API-FUNKTIONEN
# =================================================================================


# =================================================================================
# 6. HANDLER-FUNKTIONEN
# =================================================================================

# --- 6.1 Allgemeine Handler ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        add_user_to_db(user.id, user.username, user.first_name, user.last_name) 
        lang = get_user_language_from_db(user.id)
        context.user_data['lang'] = lang
        await update.message.reply_text(
            await T("welcome", context, name=user.first_name),
            reply_markup=await get_main_menu_keyboard(context)
        )
    except Exception as e:
        logger.error(f"Error in start_command: {e}")
        await update.message.reply_text("Ein Fehler ist aufgetreten. Bitte versuche es später erneut.")
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        help_text = (f"**{await T('help_title', context)}**\n\n{await T('help_body', context)}\n\n"
                     f"- **{await T('menu_earn_money', context)}:** Krypto-Tools, Bilder-Verkauf (WIP).\n"
                     f"- **{await T('menu_ai_chat', context)}:** Direkter Chat mit einer simulierten KI.\n"
                     f"- **{await T('menu_tools', context)}:** Wetter, Rechner und das Crypto-Spiel.\n"
                     f"- **{await T('menu_dashboard', context)}:** Verwalte deine Wallets und Mining-Pools.\n"
                     f"- **{await T('menu_marketplace', context)}:** Kaufe und verkaufe digitale Güter.\n\n" # NEU
                     "Benutze `/feedback`, um eine Nachricht an den Admin zu senden oder `/cancel`, um Aktionen abzubrechen.")
        
        if update.callback_query:
            await update.callback_query.edit_message_text(help_text, parse_mode=ParseMode.MARKDOWN, reply_markup=await get_main_menu_keyboard(context))
        else:
            await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN, reply_markup=await get_main_menu_keyboard(context))
    except Exception as e:
        logger.error(f"Error in help_command: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("Ein Fehler ist aufgetreten.", reply_markup=await get_main_menu_keyboard(context))
        else:
            await update.message.reply_text("Ein Fehler ist aufgetreten.")
    
async def language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Deutsch 🇩🇪", callback_data='set_lang_de')],
            [InlineKeyboardButton("English 🇬🇧", callback_data='set_lang_en')],
        ])
        await query.edit_message_text(await T("select_language", context), reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in language_menu: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("Ein Fehler ist aufgetreten.", reply_markup=await get_main_menu_keyboard(context))

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        lang_code = query.data.split('_')[-1]
        context.user_data['lang'] = lang_code
        set_user_language(query.from_user.id, lang_code)
        await query.answer(await T("language_set", context))
        await query.edit_message_text(
            await T("welcome", context, name=query.from_user.first_name),
            reply_markup=await get_main_menu_keyboard(context)
        )
    except Exception as e:
        logger.error(f"Error in set_language: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("Ein Fehler ist aufgetreten.", reply_markup=await get_main_menu_keyboard(context))

async def feedback_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(await T("feedback_prompt", context))
    except Exception as e:
        logger.error(f"Error in feedback_start: {e}")
        await update.message.reply_text("Ein Fehler ist aufgetreten. Bitte versuche es später erneut.")
    return States.FEEDBACK_MESSAGE

async def feedback_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    feedback_text = update.message.text
    try:
        add_feedback(user.id, user.username or user.first_name, feedback_text)
        await update.message.reply_text(await T("feedback_thanks", context))
        admin_notification = await T("admin_feedback_notification", context, user=user.full_name, text=feedback_text)
        try:
            await context.bot.send_message(chat_id=ADMIN_USER_ID, text=admin_notification, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Could not send feedback notification to admin: {e}")
    except Exception as e:
        logger.error(f"Error in feedback_message_handler: {e}")
        await update.message.reply_text("Ein Fehler ist aufgetreten. Bitte versuche es später erneut.")
    return ConversationHandler.END

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.info(f"User {update.effective_user.id} cancelled a conversation.")
        await update.message.reply_text(
            "Aktion abgebrochen.",
            reply_markup=await get_main_menu_keyboard(context)
        )
        # Clear any conversation-related user_data
        for key in list(context.user_data.keys()):
            if key.startswith(('game_', 'calc_', 'wallet_', 'pool_', 'xrpl_', 'marketplace_')): # NEU: 'marketplace_'
                del context.user_data[key]
    except Exception as e:
        logger.error(f"Error in cancel_command: {e}")
    return ConversationHandler.END

# --- 6.2 KI Chat Handler ---

from affiliate_tracking import log_affiliate_click, get_affiliate_stats

async def ai_chat_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🤖 **KI-Chat-Modus**\n\nDu sprichst jetzt mit der KI. Stelle eine Frage oder schreibe eine Nachricht.\nBenutze `/cancel`, um den Chat zu beenden."
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    return States.AI_CHAT_ACTIVE

async def ai_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    if "wie geht es" in user_message: response = "Mir geht es als Bot immer ausgezeichnet! Wie kann ich dir helfen?"
    elif "wer bist du" in user_message: response = "Ich bin der ScamlingBot, eine Kreation, die dir bei vielen Aufgaben helfen soll."
    else: response = f"Ich verarbeite deine Nachricht: '{update.message.text}'.\n(Dies ist eine Simulation.)"
    await update.message.reply_text(f"🤖 {response}")
    return States.AI_CHAT_ACTIVE

# --- 6.3 Tools & Spiel Handler ---

async def weather_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("Für welchen Ort möchtest du das Wetter wissen?")
    return States.WEATHER_LOCATION

async def weather_location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.text
    message = await get_weather_info(location)
    
    if "nicht konfiguriert" in message or "Fehler" in message:
        await update.message.reply_text(message, reply_markup=await get_tools_menu_keyboard(context))
    else:
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN, reply_markup=await get_tools_menu_keyboard(context))
    return ConversationHandler.END

async def calculator_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("Taschenrechner gestartet. Gib die erste Zahl ein:")
    return States.CALCULATOR_FIRST_NUMBER

async def calculator_first_number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['calc_num1'] = float(update.message.text.replace(',', '.'))
        await update.message.reply_text("Gib den Operator ein (+, -, *, /):")
        return States.CALCULATOR_OPERATOR
    except ValueError:
        await update.message.reply_text("Ungültige Zahl. Bitte erneut versuchen.")
        return States.CALCULATOR_FIRST_NUMBER

async def calculator_operator_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    op = update.message.text
    if op not in ['+', '-', '*', '/']:
        await update.message.reply_text("Ungültiger Operator. Bitte +, -, * oder / verwenden.")
        return States.CALCULATOR_OPERATOR
    context.user_data['calc_op'] = op
    await update.message.reply_text("Gib die zweite Zahl ein:")
    return States.CALCULATOR_SECOND_NUMBER

async def calculator_second_number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num2 = float(update.message.text.replace(',', '.'))
        num1 = context.user_data.pop('calc_num1')
        op = context.user_data.pop('calc_op')
        if op == '+': result = num1 + num2
        elif op == '-': result = num1 - num2
        elif op == '*': result = num1 * num2
        elif op == '/':
            if num2 == 0:
                await update.message.reply_text("Division durch Null ist nicht erlaubt.", reply_markup=await get_tools_menu_keyboard(context))
                return ConversationHandler.END
            result = num1 / num2
        await update.message.reply_text(f"Das Ergebnis ist: `{result}`", parse_mode=ParseMode.MARKDOWN, reply_markup=await get_tools_menu_keyboard(context))
    except (ValueError, KeyError):
        await update.message.reply_text("Fehler bei der Berechnung. Bitte neu starten.", reply_markup=await get_tools_menu_keyboard(context))
    return ConversationHandler.END

async def crypto_game_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    context.user_data['game_balance'] = 10000.0
    await query.answer()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(await T("game_hold", context), callback_data='game_hold')],
        [InlineKeyboardButton(await T("game_quit", context), callback_data='game_quit')]
    ])
    await query.edit_message_text(
        await T("game_welcome", context) + "\n\n" + await T("game_status", context, balance=10000.0),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )
    return States.CRYPTO_GAME_ACTION

async def crypto_game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    balance = context.user_data.get('game_balance', 0)

    if query.data == 'game_quit':
        await query.edit_message_text(await T("game_cash_out", context, balance=balance), parse_mode=ParseMode.MARKDOWN, reply_markup=await get_tools_menu_keyboard(context))
        context.user_data.pop('game_balance', None)
        return ConversationHandler.END

    coins = ["Bitcoin", "Ethereum", "DogeCoin", "ScamCoin"]
    coin = random.choice(coins)
    percent = random.randint(5, 50)
    if random.random() > 0.45:
        event_text = await T("game_event_up", context, coin=coin, percent=percent)
        balance *= (1 + percent / 100)
    else:
        event_text = await T("game_event_down", context, coin=coin, percent=percent)
        balance *= (1 - percent / 100)
    
    context.user_data['game_balance'] = balance
    
    if balance <= 0:
        await query.edit_message_text(f"{event_text}\n\n**REKT!** Du hast alles verloren. Spiel vorbei.", parse_mode=ParseMode.MARKDOWN, reply_markup=await get_tools_menu_keyboard(context))
        context.user_data.pop('game_balance', None)
        return ConversationHandler.END

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(await T("game_hold", context), callback_data='game_hold')],
        [InlineKeyboardButton(await T("game_quit", context), callback_data='game_quit')]
    ])
    status_text = await T("game_status", context, balance=balance)
    await query.edit_message_text(f"{event_text}\n\n{status_text}", parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
    return States.CRYPTO_GAME_ACTION

# --- 6.4 Geld verdienen Handler ---

async def image_upload_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("Bitte sende mir das Bild, das du hochladen möchtest.")
    return States.IMAGE_UPLOAD_RECEIVE

async def image_upload_receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file_id = update.message.photo[-1].file_id
    context.user_data['marketplace_product_file_id'] = photo_file_id
    await update.message.reply_text("Bild empfangen. Bitte gib den Namen des Produkts ein:")
    return States.MARKETPLACE_ADD_PRODUCT_NAME

# Reuse marketplace add product states for name, description, price, file upload, and confirmation
async def image_upload_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This handler is no longer used for description input, so we can remove or repurpose it
    pass

async def affiliate_generate_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("Bitte gib den Namen des Produkts ein, für das du einen Link generieren möchtest:")
    return States.AFFILIATE_PRODUCT_NAME

async def affiliate_generate_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_name = update.message.text
    base_url = "https://beispiel-partner.com/track?"
    affiliate_id = "dein_affiliate_id"
    encoded_product = urllib.parse.quote_plus(product_name)
    link = f"{base_url}id={affiliate_id}&product={encoded_product}&ref={update.effective_user.id}"
    # Log affiliate click for tracking
    log_affiliate_click(update.effective_user.id, product_name)
    await update.message.reply_text(
        f"Dein Affiliate-Link für '{product_name}':\n`{link}`",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_affiliate_links_menu_keyboard()
    )
    return ConversationHandler.END

# New handler for affiliate statistics (placeholder implementation)
from affiliate_tracking import get_affiliate_stats

async def affiliate_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = get_affiliate_stats(user_id)
    stats_text = (
        f"📈 Affiliate Statistiken:\n\n"
        f"- Klicks: {stats['clicks']}\n"
        f"- Verkäufe: {stats['sales_count']}\n"
        f"- Einnahmen: {stats['total_revenue']:.2f} SCAMCOIN"
    )
    if update.callback_query:
        await update.callback_query.edit_message_text(stats_text, reply_markup=get_affiliate_links_menu_keyboard())
    else:
        await update.message.reply_text(stats_text, reply_markup=get_affiliate_links_menu_keyboard())
    return ConversationHandler.END

# --- NEU: 6.5 Marktplatz Handler ---

async def marketplace_menu_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        await T("marketplace_title", context),
        reply_markup=await get_marketplace_menu_keyboard(context)
    )

# New handler for category filter callbacks
async def marketplace_filter_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.split('_', 2)[-1]
    if category == 'All':
        context.user_data.pop('marketplace_filter_category', None)
    else:
        context.user_data['marketplace_filter_category'] = category
    # Refresh product list with new filter
    await list_products(update, context)

# New handler for category selection during product addition (already handled in add_product_description)

# Add handler registration in main() function (at the end of main.py)
def main():
    # ... existing code ...
    application = Application.builder().token(BOT_TOKEN).build()
    # ... existing handlers ...
    application.add_handler(CallbackQueryHandler(marketplace_filter_category_handler, pattern='^filter_category_'))
    application.add_handler(CallbackQueryHandler(delete_product_handler, pattern='^delete_product_'))
    application.add_handler(CallbackQueryHandler(affiliate_stats_handler, pattern='^affiliate_stats$'))
    # ... existing handlers ...
    application.run_polling(allowed_updates=Update.ALL_TYPES)

async def view_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = int(query.data.split('_')[-1])
    product = get_product_by_id(product_id)

    if not product:
        await query.edit_message_text(await T("marketplace_product_not_found", context), reply_markup=await get_marketplace_menu_keyboard(context))
        return

    p_id, seller_id, name, description, price, currency, file_path, status = product
    
    # Gebühr berechnen und anzeigen
    fee_amount = price * MARKETPLACE_FEE_PERCENTAGE
    total_price = price + fee_amount
    
    product_text = (
        f"**{name}**\n\n"
        f"**{await T("marketplace_description", context)}:** {description}\n"
        f"**{await T("marketplace_price", context)}:** {price:.2f} {currency}\n"
        f"**Category:** {product[7] if len(product) > 7 else 'General'}\n"
        f"**{await T("marketplace_fee", context)}:** {fee_amount:.2f} {currency} (1%)\n"
        f"**{await T("marketplace_total_price", context)}:** {total_price:.2f} {currency}\n\n"
        f"**{await T("marketplace_seller", context)}:** <a href='tg://user?id={seller_id}'>Nutzer {seller_id}</a>\n" # Link zum Verkäuferprofil
    )

    if query.from_user.id == seller_id:
        # Wenn der Nutzer der Verkäufer ist, kein Kauf-Button
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(await T("marketplace_your_product", context), callback_data='ignore')],
            [InlineKeyboardButton(await T("back_to_products", context), callback_data='list_products')]
        ])
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(await T("marketplace_buy_button", context, price=total_price, currency=currency), callback_data=f"buy_product_confirm_{p_id}")],
            [InlineKeyboardButton(await T("back_to_products", context), callback_data='list_products')]
        ])
    
    context.user_data['marketplace_selected_product_id'] = p_id
    await query.edit_message_text(product_text, parse_mode=ParseMode.HTML, reply_markup=keyboard) # ParseMode.HTML für tg://user Link
    return States.MARKETPLACE_VIEW_PRODUCT # Bleibt in diesem Zustand, bis Kauf oder Zurück

async def confirm_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = int(query.data.split('_')[-1])
    
    # Erneut Produkt und Balances holen, um die aktuellsten Daten zu haben
    product = get_product_by_id(product_id)
    if not product:
        await query.edit_message_text(await T("marketplace_product_not_found", context), reply_markup=await get_marketplace_menu_keyboard(context))
        return ConversationHandler.END

    p_id, seller_id, name, description, price, currency, file_path, status = product
    
    if query.from_user.id == seller_id:
        await query.edit_message_text(await T("marketplace_cannot_buy_own", context), reply_markup=await get_marketplace_menu_keyboard(context))
        return ConversationHandler.END

    buyer_id = query.from_user.id
    buyer_balance = get_user_internal_balance(buyer_id)
    fee_amount = price * MARKETPLACE_FEE_PERCENTAGE
    total_price = price + fee_amount
    
    if buyer_balance < total_price:
        await query.edit_message_text(await T("marketplace_insufficient_funds", context, balance=buyer_balance, needed=total_price), reply_markup=await get_marketplace_menu_keyboard(context))
        return ConversationHandler.END

    # Transaktion durchführen und Balances aktualisieren
    success = process_transaction(
        product_id=p_id,
        buyer_id=buyer_id,
        seller_id=seller_id,
        price=price,
        fee_percentage=MARKETPLACE_FEE_PERCENTAGE
    )

    if success:
        # Sende Datei an Käufer
        try:
            # Annahme: file_path ist ein String, der direkt gesendet werden kann (z.B. eine Telegram file_id)
            # Oder du musst die Datei aus dem Dateisystem laden und senden
            await context.bot.send_document(chat_id=buyer_id, document=file_path, caption=await T("marketplace_your_purchase", context, name=name))
            await query.edit_message_text(await T("marketplace_purchase_success", context, name=name, price=total_price, currency=currency), reply_markup=await get_marketplace_menu_keyboard(context))
            # Benachrichtige den Verkäufer
            await context.bot.send_message(chat_id=seller_id, text=await T("marketplace_seller_notification", context, name=name, price=price * (1 - MARKETPLACE_FEE_PERCENTAGE), currency=currency), parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Error sending product file to user {buyer_id}: {e}")
            await query.edit_message_text(await T("marketplace_purchase_success_no_delivery", context, name=name), reply_markup=await get_marketplace_menu_keyboard(context))
    else:
        await query.edit_message_text(await T("marketplace_purchase_failed", context), reply_markup=await get_marketplace_menu_keyboard(context))
    
    return ConversationHandler.END # Kauf abgeschlossen, Konversation beendet

async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(await T("marketplace_add_name_prompt", context))
    return States.MARKETPLACE_ADD_PRODUCT_NAME

async def add_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['marketplace_product_name'] = update.message.text
    # Ask for category after name
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("General", callback_data='category_General')],
        [InlineKeyboardButton("E-Books", callback_data='category_EBooks')],
        [InlineKeyboardButton("Software", callback_data='category_Software')],
        [InlineKeyboardButton("Art", callback_data='category_Art')],
        [InlineKeyboardButton("Music", callback_data='category_Music')],
        [InlineKeyboardButton("Other", callback_data='category_Other')],
    ])
    await update.message.reply_text("Please select a category for your product:", reply_markup=keyboard)
    return States.MARKETPLACE_ADD_PRODUCT_DESCRIPTION # Reuse this state for category selection

async def add_product_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if this is a category selection callback
    if update.callback_query and update.callback_query.data.startswith('category_'):
        category = update.callback_query.data.split('_')[1]
        context.user_data['marketplace_product_category'] = category
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(await T("marketplace_add_description_prompt", context))
        return States.MARKETPLACE_ADD_PRODUCT_DESCRIPTION
    else:
        context.user_data['marketplace_product_description'] = update.message.text
        await update.message.reply_text(await T("marketplace_add_price_prompt", context))
        return States.MARKETPLACE_ADD_PRODUCT_PRICE

async def add_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(update.message.text.replace(',', '.'))
        if price <= 0:
            raise ValueError
        context.user_data['marketplace_product_price'] = price
        context.user_data['marketplace_product_currency'] = "SCAMCOIN" # Standardisierte interne Währung
        await update.message.reply_text(await T("marketplace_add_file_prompt", context))
        return States.MARKETPLACE_ADD_PRODUCT_FILE
    except ValueError:
        await update.message.reply_text(await T("marketplace_invalid_price", context))
        return States.MARKETPLACE_ADD_PRODUCT_PRICE

async def add_product_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Hier nehmen wir an, dass es sich um ein Dokument oder Foto handelt.
    # Für komplexere Dateien müsste man den Dateityp prüfen.
    if update.message.document:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id # Größtes Foto
        file_name = f"photo_{file_id}.jpg" # Einfacher Dateiname
    else:
        await update.message.reply_text(await T("marketplace_add_file_error", context))
        return States.MARKETPLACE_ADD_PRODUCT_FILE
    
    context.user_data['marketplace_product_file_id'] = file_id

    name = context.user_data['marketplace_product_name']
    description = context.user_data['marketplace_product_description']
    price = context.user_data['marketplace_product_price']
    currency = context.user_data['marketplace_product_currency']
    category = context.user_data.get('marketplace_product_category', 'General')

    preview_text = (
        f"**{await T("marketplace_preview_title", context)}**\n\n"
        f"**{await T("marketplace_product_name", context)}:** {name}\n"
        f"**{await T("marketplace_description", context)}:** {description}\n"
        f"**{await T("marketplace_price", context)}:** {price:.2f} {currency}\n"
        f"**{await T("marketplace_file", context)}:** {file_name}\n"
        f"**Category:** {category}\n\n"
        f"{await T("marketplace_confirm_add_prompt", context)}"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(await T("yes_confirm", context), callback_data='confirm_add_product')],
        [InlineKeyboardButton(await T("no_cancel", context), callback_data='cancel_action')]
    ])
    await update.message.reply_text(preview_text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
    return States.MARKETPLACE_ADD_PRODUCT_CONFIRM

async def add_product_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'confirm_add_product':
        user_id = query.from_user.id
        name = context.user_data.pop('marketplace_product_name')
        description = context.user_data.pop('marketplace_product_description')
        price = context.user_data.pop('marketplace_product_price')
        currency = context.user_data.pop('marketplace_product_currency')
        file_id = context.user_data.pop('marketplace_product_file_id')
        category = context.user_data.pop('marketplace_product_category', 'General')

        product_id = add_product(user_id, name, description, price, currency, file_id, category)
        if product_id:
            await query.edit_message_text(await T("marketplace_product_added_success", context, name=name), reply_markup=await get_marketplace_menu_keyboard(context))
        else:
            await query.edit_message_text(await T("marketplace_product_add_failed", context), reply_markup=await get_marketplace_menu_keyboard(context))
    else: # cancel_action
        await query.edit_message_text(await T("marketplace_add_product_cancelled", context), reply_markup=await get_marketplace_menu_keyboard(context))
    
    return ConversationHandler.END

async def my_selling_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_products = get_user_products(query.from_user.id)

    if not user_products:
        await query.edit_message_text(await T("marketplace_no_selling_products", context), reply_markup=await get_marketplace_menu_keyboard(context))
        return ConversationHandler.END

    text = await T("marketplace_your_products_title", context) + "\n\n"
    keyboard_buttons = []
    for p_id, seller_id, name, description, price, currency, file_path, status in user_products:
        text += f"▪️ **{name}** ({price:.2f} {currency}) - Status: {status}\n"
        keyboard_buttons.append([InlineKeyboardButton(f"Löschen {name}", callback_data=f"delete_product_{p_id}")])
    
    keyboard_buttons.append([InlineKeyboardButton(await T("back_to_main", context), callback_data="marketplace_menu")])
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard_buttons))
    return ConversationHandler.END

# Handler to delete a product
async def delete_product_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = int(query.data.replace("delete_product_", ""))
    user_id = query.from_user.id

    product = get_product_by_id(product_id)
    if not product or product[1] != user_id:
        await query.edit_message_text("❌ Produkt nicht gefunden oder du bist nicht der Verkäufer.", reply_markup=await get_marketplace_menu_keyboard(context))
        return ConversationHandler.END

    # Mark product as deleted
    conn = None
    try:
        import sqlite3
        conn = sqlite3.connect('scamlingbot.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE products SET status = "deleted" WHERE id = ?', (product_id,))
        conn.commit()
    except Exception as e:
        await query.edit_message_text(f"❌ Fehler beim Löschen des Produkts: {e}", reply_markup=await get_marketplace_menu_keyboard(context))
        return ConversationHandler.END
    finally:
        if conn:
            conn.close()

    await query.edit_message_text("✅ Produkt wurde gelöscht.", reply_markup=await get_marketplace_menu_keyboard(context))
    return ConversationHandler.END


# --- NEU: 6.6 Interne Wallet-Verwaltung (Aufladen/Abheben) ---
# Diese Funktionen simulieren Ein- und Auszahlungen. Für echte Krypto wären hier
# API-Aufrufe an Wallets/Börsen nötig (siehe services.py Kommentare).

async def internal_wallet_deposit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Für echte Krypto: Hier würde eine Adresse angezeigt, an die der Nutzer senden soll.
    # Für Simulation: Direkt den Betrag abfragen
    await query.edit_message_text(await T("internal_wallet_deposit_prompt", context))
    return States.INTERNAL_WALLET_DEPOSIT_AMOUNT

async def internal_wallet_deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError
        
        user_id = update.effective_user.id
        # Simulation der Krypto-Einzahlung (in services.py)
        # In einer echten Anwendung: Hier würde der Bot auf eine Bestätigung der Blockchain warten
        # und dann die interne Balance aktualisieren.
        deposit_successful = await simulate_crypto_deposit(user_id, amount) 
        
        if deposit_successful:
            update_user_internal_balance(user_id, amount)
            current_balance = get_user_internal_balance(user_id)
            await update.message.reply_text(await T("internal_wallet_deposit_success", context, amount=amount, balance=current_balance), reply_markup=await get_personal_area_menu_keyboard(context))
        else:
            await update.message.reply_text(await T("internal_wallet_deposit_failed", context), reply_markup=await get_personal_area_menu_keyboard(context))
    except ValueError:
        await update.message.reply_text(await T("internal_wallet_invalid_amount", context))
        return States.INTERNAL_WALLET_DEPOSIT_AMOUNT
    return ConversationHandler.END

async def internal_wallet_withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    current_balance = get_user_internal_balance(query.from_user.id)
    await query.edit_message_text(await T("internal_wallet_withdraw_prompt", context, balance=current_balance))
    return States.INTERNAL_WALLET_WITHDRAW_AMOUNT

async def internal_wallet_withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(update.message.text.replace(',', '.'))
        user_id = update.effective_user.id
        current_balance = get_user_internal_balance(user_id)

        if amount <= 0 or amount > current_balance:
            await update.message.reply_text(await T("internal_wallet_invalid_withdraw_amount", context))
            return States.INTERNAL_WALLET_WITHDRAW_AMOUNT # Bleibe im Zustand
        
        # In einer echten Anwendung: Hier würde der Bot eine Krypto-Auszahlung an die vom User angegebene
        # externe Adresse veranlassen und die Transaktionsgebühren berücksichtigen.
        # simulate_crypto_withdrawal würde die eigentliche Krypto-Transaktion initiieren.
        withdrawal_successful = await simulate_crypto_withdrawal(user_id, amount)

        if withdrawal_successful:
            update_user_internal_balance(user_id, -amount)
            current_balance_after_withdraw = get_user_internal_balance(user_id)
            await update.message.reply_text(await T("internal_wallet_withdraw_success", context, amount=amount, balance=current_balance_after_withdraw), reply_markup=await get_personal_area_menu_keyboard(context))
        else:
            await update.message.reply_text(await T("internal_wallet_withdraw_failed", context), reply_markup=await get_personal_area_menu_keyboard(context))

    except ValueError:
        await update.message.reply_text(await T("internal_wallet_invalid_withdraw_amount", context))
        return States.INTERNAL_WALLET_WITHDRAW_AMOUNT
    return ConversationHandler.END

# --- 6.7 Persönlicher Bereich Handler ---

async def my_wallets_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    wallets = get_user_wallets(query.from_user.id)
    internal_balance = get_user_internal_balance(query.from_user.id) # Hole interne Balance
    
    text = await T("my_wallets_title", context) + "\n\n"
    text += f"▪️ **{await T("internal_balance_label", context)}:** `{internal_balance:.2f} SCAMCOIN`\n" # Zeige interne Balance
    
    if wallets:
        text += "\n" + await T("external_wallets_label", context) + "\n"
        text += "\n".join([f"▪️ **{c}:** `{a}`" for _, c, a in wallets])
    else:
        text += await T("no_external_wallets", context)
        
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=await get_my_wallets_menu_keyboard(context)) # Kontext an Keyboard übergeben

async def add_wallet_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("Gib die Währung der Wallet ein (z.B. BTC, ETH):")
    return States.ADD_WALLET_CURRENCY

async def add_wallet_currency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['wallet_currency'] = update.message.text.strip().upper()
    await update.message.reply_text(f"Gib nun die Wallet-Adresse für **{context.user_data['wallet_currency']}** ein:")
    return States.ADD_WALLET_ADDRESS

async def add_wallet_address_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text.strip()
    currency = context.user_data.pop('wallet_currency')
    if add_user_wallet(update.effective_user.id, currency, address):
        await update.message.reply_text(f"✅ Wallet für **{currency}** wurde hinzugefügt!", parse_mode=ParseMode.MARKDOWN)
    else:
        await update.message.reply_text("❌ Fehler: Diese Wallet existiert bereits.")
    await my_wallets_menu(update, context)
    return ConversationHandler.END

async def remove_wallet_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    wallets = get_user_wallets(query.from_user.id)
    if not wallets:
        await query.answer("Du hast keine Wallets zum Entfernen.", show_alert=True)
        return ConversationHandler.END
    keyboard = [[InlineKeyboardButton(f"{c}: {a[:10]}...", callback_data=f"del_wallet_{wid}")] for wid, c, a in wallets]
    keyboard.append([InlineKeyboardButton(await T("no_cancel", context), callback_data="cancel_action")]) # Verwende lokalisierte Taste
    await query.edit_message_text("Wähle die Wallet zum Entfernen:", reply_markup=InlineKeyboardMarkup(keyboard))
    return States.REMOVE_WALLET_SELECT

async def remove_wallet_select_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "cancel_action":
        await my_wallets_menu(query, context)
        return ConversationHandler.END
    wallet_id = int(query.data.replace("del_wallet_", ""))
    if remove_user_wallet(wallet_id, query.from_user.id): await query.answer("Wallet entfernt.", show_alert=True)
    else: await query.answer("Fehler beim Entfernen.", show_alert=True)
    await my_wallets_menu(query, context)
    return ConversationHandler.END

async def check_balances(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.edit_message_text(" Lade Guthaben...", reply_markup=await get_my_wallets_menu_keyboard(context)) # Kontext an Keyboard übergeben
    wallets = get_user_wallets(query.from_user.id)
    if not wallets:
        await query.edit_message_text("Keine Wallets hinterlegt.", reply_markup=await get_my_wallets_menu_keyboard(context)) # Kontext an Keyboard übergeben
        return

    report = "**Guthaben-Übersicht (Externe Wallets):**\n\n"
    for _, currency, address in wallets:
        # Hier verwenden wir die neue Funktion aus services.py
        balance_text = await fetch_wallet_balance_blockchair(currency, address)
        report += f"▪️ **{currency}** `{address[:8]}...`:\n  {balance_text}\n"
    await query.edit_message_text(report, parse_mode=ParseMode.MARKDOWN, reply_markup=await get_my_wallets_menu_keyboard(context)) # Kontext an Keyboard übergeben

async def my_pools_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    pools = get_user_pools(query.from_user.id)
    text = await T("my_pools_title", context) + ("\n".join([f"▪️ **{ptype}:** `{paddr}`" for _, ptype, paddr in pools]) if pools else await T("no_pools", context))
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=await get_my_pools_menu_keyboard(context)) # Kontext an Keyboard übergeben

# --- NEUE FUNKTIONEN FÜR ADD_POOL_FLOW ---
async def add_pool_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Startet die Konversation zur Pool-Hinzufügung mit Krypto-Auswahl."""
    query = update.callback_query
    if query:
        await query.answer()
        # Erstelle Inline-Tastatur für Krypto-Auswahl
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ETH", callback_data='add_pool_crypto_ETH')],
            [InlineKeyboardButton("ETC", callback_data='add_pool_crypto_ETC')],
            [InlineKeyboardButton("KAS", callback_data='add_pool_crypto_KAS')],
            [InlineKeyboardButton("BTC", callback_data='add_pool_crypto_BTC')], # Hinzugefügt für zukünftige BTC-Unterstützung
            [InlineKeyboardButton(await T("back_to_dashboard", context), callback_data='menu_personal_area')] # Zurück zum Dashboard
        ])
        await query.edit_message_text("Für welche Kryptowährung möchtest du einen Mining-Pool hinzufügen?", reply_markup=keyboard)
        return States.ADD_POOL_CRYPTO
    return ConversationHandler.END # Sollte nur über Callback erreicht werden

async def add_pool_crypto_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Verarbeitet die ausgewählte Kryptowährung für den Pool."""
    query = update.callback_query
    await query.answer()
    crypto_type = query.data.split('_')[-1] # Extrahiert z.B. 'ETH'
    context.user_data['pool_crypto_type'] = crypto_type # Speichert Krypto-Typ temporär

    await query.edit_message_text(f"Okay, du hast **{crypto_type}** gewählt. Bitte gib jetzt die Pool-Adresse oder Worker-ID für **{crypto_type}** ein.")
    return States.ADD_POOL_ADDRESS

async def add_pool_address_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Verarbeitet die eingegebene Pool-Adresse und speichert den Pool."""
    pool_address = update.message.text.strip()
    pool_crypto_type = context.user_data.pop('pool_crypto_type', None) # Holt den gespeicherten Krypto-Typ

    if not pool_crypto_type: # Fallback, falls Konversation unterbrochen wurde
        await update.message.reply_text("Fehler: Krypto-Typ nicht gefunden. Bitte starte den Vorgang erneut.",
                                        reply_markup=await get_personal_area_menu_keyboard(context))
        return ConversationHandler.END

    if add_user_pool(update.effective_user.id, pool_crypto_type, pool_address):
        await update.message.reply_text(f"✅ Pool für **{pool_crypto_type}** mit Adresse `{pool_address}` wurde hinzugefügt!", parse_mode=ParseMode.MARKDOWN,
                                        reply_markup=await get_personal_area_menu_keyboard(context))
    else:
        await update.message.reply_text("❌ Fehler: Dieser Pool existiert bereits oder konnte nicht hinzugefügt werden.",
                                        reply_markup=await get_personal_area_menu_keyboard(context))
    return ConversationHandler.END

async def remove_pool_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    pools = get_user_pools(query.from_user.id)
    if not pools:
        await query.answer("Du hast keine Pools zum Entfernen.", show_alert=True)
        return ConversationHandler.END
    keyboard = [[InlineKeyboardButton(f"{ptype}: {paddr[:20]}...", callback_data=f"del_pool_{pid}")] for pid, ptype, paddr in pools]
    keyboard.append([InlineKeyboardButton(await T("back_to_dashboard", context), callback_data="menu_personal_area")]) # Verwende lokalisierte Taste
    await query.edit_message_text("Wähle den Pool zum Entfernen:", reply_markup=InlineKeyboardMarkup(keyboard))
    return States.REMOVE_POOL_SELECT

async def remove_pool_select_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "cancel_action": # Hier auch auf 'cancel_action' reagieren, um zurückzugehen
        await my_pools_menu(query, context)
        return ConversationHandler.END
    
    pool_id = int(query.data.replace("del_pool_", ""))
    if remove_user_pool(pool_id, query.from_user.id): 
        await query.answer("Pool entfernt.", show_alert=True)
    else: 
        await query.answer("Fehler beim Entfernen.", show_alert=True)
    
    await my_pools_menu(query, context) # Zeigt aktualisierte Liste
    return ConversationHandler.END

# Startpunkt für Allgemeine Pool-Stats Konversation
async def general_pool_stats_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    # Erstelle Inline-Tastatur für die Auswahl der allgemeinen Pool-Statistiken
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("BTC (Public-Pool.io)", callback_data='general_pool_stats_publicpool_btc')],
        [InlineKeyboardButton("BTC (ViaBTC)", callback_data='general_pool_stats_viabtc_btc')],
        # [InlineKeyboardButton("ETH (Ethermine.org)", callback_data='general_pool_stats_ethermine_eth')], # Beispiel für weitere
        [InlineKeyboardButton(await T("back_to_dashboard", context), callback_data='menu_personal_area')] # Zurück zum Dashboard
    ])
    await query.edit_message_text("Welche allgemeinen Pool-Statistiken möchtest du sehen?", reply_markup=keyboard)
    return States.GENERAL_POOL_STATS_SELECTION

# Handler für die Auswahl der allgemeinen Pool-Statistik
async def handle_general_pool_stats_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    selected_pool = query.data.replace('general_pool_stats_', '') # Extrahiert z.B. 'publicpool_btc'

    await query.edit_message_text(await T("fetching_xrpl_info", context)) # Wiederverwendung des Lade-Textes
    
    stats_text = "Fehler: Unbekannter Pool oder Abfragefehler."
    if selected_pool == "publicpool_btc":
        stats_text = await fetch_publicpool_btc_stats()
    elif selected_pool == "viabtc_btc":
        stats_text = await fetch_viabtc_btc_stats()
    # elif selected_pool == "ethermine_eth": # Beispiel für weitere Abfragen
    #     stats_text = "Ethermine ETH Gesamtstats hier einfügen"
        
    await query.edit_message_text(
        stats_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=await get_my_pools_menu_keyboard(context) # Zurück zum "Meine Mining Pools" Menü
    )
    return ConversationHandler.END

async def check_pools_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    pools = get_user_pools(query.from_user.id)
    supported_pools = [p for p in pools if p[1].upper() in ["ETH", "ETC"]] # Hier noch auf Ethermine beschränkt
    
    if not supported_pools:
        await query.answer("Du hast keine unterstützten Pools (ETH, ETC) zum Abfragen.", show_alert=True)
        return ConversationHandler.END
        
    keyboard = [[InlineKeyboardButton(f"{ptype}: {paddr[:20]}...", callback_data=f"check_pool_{pid}")] for pid, ptype, paddr in supported_pools]
    keyboard.append([InlineKeyboardButton(await T("back_to_dashboard", context), callback_data="menu_personal_area")]) # Verwende lokalisierte Taste
    
    await query.edit_message_text("Wähle den Pool, dessen Statistiken du abrufen möchtest:", reply_markup=InlineKeyboardMarkup(keyboard))
    return States.CHECK_POOL_STATS_SELECT

async def check_pool_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_action":
        await my_pools_menu(update, context)
        return ConversationHandler.END

    pool_id = int(query.data.replace("check_pool_", ""))
    pools = get_user_pools(query.from_user.id)
    target_pool = next((p for p in pools if p[0] == pool_id), None)

    if not target_pool:
        await query.edit_message_text("Fehler: Pool nicht gefunden.")
        return ConversationHandler.END

    await query.edit_message_text(" Lade Statistiken...")
    _, pool_type, pool_address = target_pool
    
    stats_text = "Nicht unterstützter Pooltyp oder fehlende Implementierung."
    if pool_type.upper() in ["ETH", "ETC"]:
        stats_text = await fetch_ethermine_stats(pool_type, pool_address)
    # HIER ERWEITERN FÜR NEUE POOL-TYPEN (z.B. KAS, BTC)
    # elif pool_type.upper() == "KAS":
    #     stats_text = await fetch_woolypooly_kas_stats(pool_address)
    # elif pool_type.upper() == "BTC":
    #     stats_text = await fetch_slushpool_btc_stats(pool_address) # Annahme: Slushpool API
    
    final_text = f"**Statistiken für {pool_type}:** `{pool_address}`\n\n{stats_text}"
    await query.edit_message_text(final_text, parse_mode=ParseMode.MARKDOWN, reply_markup=await get_my_pools_menu_keyboard(context)) # Kontext an Keyboard übergeben
    return ConversationHandler.END

# --- 6.8 Admin Handler ---

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("🚫 Du bist nicht berechtigt.")
        return ConversationHandler.END
    await update.message.reply_text("Bitte gib das Admin-Passwort ein:")
    return States.ADMIN_LOGIN_PASSWORD

async def admin_password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == ADMIN_PASSWORD:
        await update.message.reply_text("✅ Admin-Login erfolgreich!", reply_markup=get_admin_menu_keyboard())
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ Falsches Passwort.")
        return States.ADMIN_LOGIN_PASSWORD

async def admin_bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_user_stats()
    text = await T("admin_stats_title", context) + "\n\n" + await T("admin_stats_body", context, **stats)
    await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_admin_menu_keyboard())

async def admin_read_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feedbacks = get_feedback()
    if not feedbacks:
        await update.callback_query.edit_message_text(await T("admin_no_feedback", context), reply_markup=get_admin_menu_keyboard())
        return
    report = f"**{await T("admin_feedback_title", context)}**\n\n"
    for username, text, date in feedbacks[:10]:
        report += f"**Von:** {username} ({date[:10]})\n`{text}`\n---\n"
    await update.callback_query.edit_message_text(report, reply_markup=get_admin_menu_keyboard())

async def admin_check_news_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text(" Starte manuelle News-Prüfung...", reply_markup=get_admin_menu_keyboard())
    await check_and_post_news(context)
    await update.callback_query.edit_message_text("Manuelle News-Prüfung abgeschlossen.", reply_markup=get_admin_menu_keyboard())

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID: return ConversationHandler.END
    await update.callback_query.edit_message_text("Bitte sende mir die Nachricht für den Broadcast. Nutze /cancel zum Abbrechen.")
    return States.ADMIN_BROADCAST_MESSAGE

async def broadcast_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['broadcast_message'] = update.message.text
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(await T("yes_confirm", context), callback_data='yes'), InlineKeyboardButton(await T("no_cancel", context), callback_data='no')]]) # Verwende lokalisierte Tasten
    await update.message.reply_text(f"**Vorschau:**\n\n{update.message.text}\n\nSoll diese Nachricht an alle Nutzer gesendet werden?", reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)
    return States.ADMIN_BROADCAST_CONFIRM

async def broadcast_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'no':
        await query.edit_message_text("Broadcast abgebrochen.", reply_markup=get_admin_menu_keyboard())
        context.user_data.pop('broadcast_message', None)
        return ConversationHandler.END

    message = context.user_data.pop('broadcast_message', None)
    if not message:
        await query.edit_message_text("❌ Fehler: Keine Nachricht gefunden.", reply_markup=get_admin_menu_keyboard())
        return ConversationHandler.END

    await query.edit_message_text(" Sende Broadcast...")
    sent, failed = 0, 0
    for user_id in get_all_user_ids():
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            sent += 1
            await asyncio.sleep(0.1)
        except Exception: failed += 1
    await query.edit_message_text(f"✅ Broadcast abgeschlossen!\nGesendet: `{sent}`\nFehlgeschlagen: `{failed}`", parse_mode=ParseMode.MARKDOWN, reply_markup=get_admin_menu_keyboard())
    return ConversationHandler.END

# --- 6.9 Fehlerbehandlung ---

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception while handling an update:", exc_info=context.error)
    try:
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text("❌ Ein interner Fehler ist aufgetreten.", reply_markup=await get_main_menu_keyboard(context))
    except Exception as e:
        logger.error(f"Failed to send error message to user: {e}")


# --- 6.10 Menü Navigation Handler (Direkt von Callbacks) ---

async def main_menu_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        await T("welcome", context, name=query.from_user.first_name),
        reply_markup=await get_main_menu_keyboard(context)
    )

async def earn_money_menu_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        await T("earn_money_title", context),
        reply_markup=await get_geld_verdienen_menu_keyboard(context)
    )

async def tools_menu_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        await T("tools_menu_title", context),
        reply_markup=await get_tools_menu_keyboard(context)
    )

async def dashboard_menu_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        await T("dashboard_title", context),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=await get_personal_area_menu_keyboard(context)
    )

async def crypto_swap_menu_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        await T("crypto_swap_title", context),
        reply_markup=get_krypto_swap_menu_keyboard()
    )

async def image_sell_menu_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        await T("image_sell_title", context),
        reply_markup=get_bilder_verkaufen_menu_keyboard()
    )

async def affiliate_menu_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        await T("affiliate_title", context),
        reply_markup=get_affiliate_links_menu_keyboard()
    )

async def get_crypto_prices_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    final_message = await fetch_crypto_prices_coingecko() 
    await query.edit_message_text(
        text=final_message,
        reply_markup=get_krypto_swap_menu_keyboard(),
        parse_mode='Markdown'
    )

async def handle_kurs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if len(args) == 2:
        currency_from = args[0].upper()
        currency_to = args[1].upper()
        message = await get_exchange_rate(currency_from, currency_to)
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Bitte gib zwei Währungscodes an, z.B. `/kurs BTC ETH`", parse_mode="Markdown")

async def handle_preis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if len(args) == 1:
        symbol = args[0].upper()
        message = await get_single_crypto_price(symbol)
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Bitte gib einen Kryptowährungs-Symbol an, z.B. `/preis BTC`", parse_mode="Markdown")

async def handle_wetter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if args:
        city = " ".join(args)
        message = await get_weather_info(city)
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Bitte gib eine Stadt an, z.B. `/wetter Berlin`", parse_mode="Markdown")

# Startpunkt für die XRPL-Info Konversation über Button oder Befehl
async def xrpl_info_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(await T("prompt_enter_xrpl_address", context))
    else: # Wenn es ein CommandHandler ist (/xrplinfo ohne Argumente)
        await update.message.reply_text(await T("prompt_enter_xrpl_address", context))
    return States.XRPL_ADDRESS_INPUT

# Handler für die XRPL-Adresseingabe
async def xrpl_address_received_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    address = update.message.text.strip()
    
    # Validiere die Adresse (grundlegende Prüfung)
    if not (address.startswith('r') and len(address) >= 25 and len(address) <= 35):
        await update.message.reply_text(await T("invalid_xrpl_address", context),
                                        reply_markup=await get_personal_area_menu_keyboard(context))
        return ConversationHandler.END # Beende Konversation bei ungültiger Adresse

    # Sende eine "Lade"-Nachricht
    loading_message = await update.message.reply_text(await T("fetching_xrpl_info", context))

    xrpl_info_text = await fetch_xrpl_account_info(address)

    # Bearbeite die "Lade"-Nachricht mit den Ergebnissen
    await loading_message.edit_text(
        xrpl_info_text,
        parse_mode=ParseMode.HTML, # Wichtig für Bold (<b>) und Code (<code>)
        reply_markup=await get_personal_area_menu_keyboard(context)
    )
    return ConversationHandler.END # Beende die Konversation nach erfolgreicher Abfrage


async def show_xrpl_dex_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    info_text = (
        "ℹ️ Der **XRPL DEX Swap** ist eine fortgeschrittene Funktion und erfordert direkte Interaktion mit der XRP Ledger (XRPL) dezentralen Börse. Dies ist keine Funktion, die der Bot direkt ausführt, sondern eher ein Hinweis auf die Möglichkeit.\n\n"
        "Für XRPL DEX Swaps benötigst du in der Regel:\n"
        "1. Eine XRPL-Wallet (z.B. XUMM Wallet).\n"
        "2. Vertrauenslinien (Trustlines) zu den Assets, die du handeln möchtest (z.B. `rDoge` für XRDoge).\n"
        "3. Verständnis der Funktionsweise einer dezentralen Börse.\n\n"
        "Bitte sei vorsichtig und informiere dich umfassend, bevor du Transaktionen auf einem DEX durchführst."
    )
    await query.edit_message_text(info_text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_krypto_swap_menu_keyboard())

async def show_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    await query.edit_message_text(f"⏰ Die aktuelle Uhrzeit ist: `{current_time}`", parse_mode=ParseMode.MARKDOWN, reply_markup=await get_tools_menu_keyboard(context))

async def show_wip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer(await T("wip", context), show_alert=True)
    # Edit the message to remain on the same menu, or return to relevant parent
    if query.data == 'bilder_sales':
        await query.edit_message_text(await T("image_sell_title", context), reply_markup=get_bilder_verkaufen_menu_keyboard())
    elif query.data == 'affiliate_stats':
        await query.edit_message_text(await T("affiliate_title", context), reply_markup=get_affiliate_links_menu_keyboard())


# =================================================================================
# 7. HAUPTFUNKTION ZUM STARTEN DES BOTS
# =================================================================================

def main():
    """
    Startet den Bot und registriert jeden Handler explizit, um die
    ursprüngliche Struktur und maximale Klarheit zu gewährleisten.
    """
    if not BOT_TOKEN or "YOUR_BOT_TOKEN" in BOT_TOKEN:
        logger.critical("BOT_TOKEN ist nicht gesetzt. Der Bot kann nicht starten.")
        return

    init_db() # Stellt sicher, dass alle Tabellen (auch neue) initialisiert werden
    application = Application.builder().token(BOT_TOKEN).build()

    # Import handlers from modular files
    from admin import (
        admin_command, admin_password_handler, admin_bot_status,
        admin_read_feedback, admin_check_news_manual,
        broadcast_start, broadcast_message_handler, broadcast_confirm_handler
    )
    from wallet import (
        my_wallets_menu, add_wallet_start, add_wallet_currency_handler,
        add_wallet_address_handler, remove_wallet_start, remove_wallet_select_handler,
        wallet_transaction_history
    )
    from marketplace import (
        marketplace_menu_view, marketplace_filter_category_handler, list_products,
        view_product, confirm_buy, add_product_start, add_product_name,
        add_product_description, add_product_price, add_product_file,
        add_product_confirm, my_selling_products, delete_product_handler
    )
    from tools import (
        weather_start, weather_location_handler,
        calculator_start, calculator_first_number_handler, calculator_operator_handler, calculator_second_number_handler,
        crypto_game_start, crypto_game_handler
    )
    from profile import (
        profile_view, profile_edit_start, profile_edit_handler, profile_cancel
    )
    from referral_leaderboard import referral_leaderboard_handler
    from summary import send_daily_summary
    from moderation import spam_filter
    from analytics_dashboard import analytics_dashboard_handler
    from ai_chat import ai_chat_start, ai_chat_handler, ai_chat_cancel
    from ai_media import bild_command, video_command

    # --- Conversation Handlers (müssen zuerst registriert werden) ---
    
    admin_conv = ConversationHandler(
        entry_points=[CommandHandler('admin', admin_command), CallbackQueryHandler(broadcast_start, pattern='^admin_broadcast_start$')],
        states={
            States.ADMIN_LOGIN_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_password_handler)],
            States.ADMIN_BROADCAST_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message_handler)],
            States.ADMIN_BROADCAST_CONFIRM: [CallbackQueryHandler(broadcast_confirm_handler, pattern='^(yes|no)$')]
        },
        fallbacks=[CommandHandler('cancel', cancel_command)]
    )
    
    feedback_conv = ConversationHandler(
        entry_points=[CommandHandler('feedback', feedback_start)],
        states={States.FEEDBACK_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, feedback_message_handler)]},
        fallbacks=[CommandHandler('cancel', cancel_command)]
    )

    game_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(crypto_game_start, pattern='^tool_game_start$')],
        states={States.CRYPTO_GAME_ACTION: [CallbackQueryHandler(crypto_game_handler, pattern='^game_')]},
        fallbacks=[CommandHandler('cancel', cancel_command)]
    )

    pool_stats_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_pool_start, pattern='^personal_area_add_pool_start$'),
            CallbackQueryHandler(remove_pool_start, pattern='^personal_area_remove_pool_start$'),
            CallbackQueryHandler(check_pools_start, pattern='^personal_area_check_all_pools$'),
            CallbackQueryHandler(general_pool_stats_start, pattern='^personal_area_general_pool_stats_start$')
        ],
        states={
            States.ADD_POOL_CRYPTO: [CallbackQueryHandler(add_pool_crypto_selected, pattern='^add_pool_crypto_')],
            States.ADD_POOL_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_pool_address_handler)],
            States.REMOVE_POOL_SELECT: [CallbackQueryHandler(remove_pool_select_handler, pattern='^del_pool_|^cancel_action$')],
            States.CHECK_POOL_STATS_SELECT: [CallbackQueryHandler(check_pool_stats_handler, pattern='^check_pool_|^cancel_action$')],
            States.GENERAL_POOL_STATS_SELECTION: [CallbackQueryHandler(handle_general_pool_stats_selection, pattern='^general_pool_stats_')]
        },
        fallbacks=[CommandHandler('cancel', cancel_command), CallbackQueryHandler(main_menu_view, pattern='^back_to_main_menu$')]
    )

    image_upload_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(image_upload_start, pattern='^bilder_upload_start$')],
        states={
            States.IMAGE_UPLOAD_RECEIVE: [MessageHandler(filters.PHOTO, image_upload_receive_photo)],
            States.MARKETPLACE_ADD_PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_name)],
            States.MARKETPLACE_ADD_PRODUCT_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_description)],
            States.MARKETPLACE_ADD_PRODUCT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_price)],
            States.MARKETPLACE_ADD_PRODUCT_FILE: [MessageHandler(filters.PHOTO | filters.Document.ALL, add_product_file)],
            States.MARKETPLACE_ADD_PRODUCT_CONFIRM: [CallbackQueryHandler(add_product_confirm, pattern='^(confirm_add_product|cancel_action)$')]
        },
        fallbacks=[CommandHandler('cancel', cancel_command)]
    )
    profile_conv = ConversationHandler(
        entry_points=[CommandHandler('profile', profile_view)],
        states={
            profile_view: [CallbackQueryHandler(profile_edit_start, pattern='^edit_')],
            profile_edit_start: [MessageHandler(filters.TEXT & ~filters.COMMAND, profile_edit_handler)],
        },
        fallbacks=[CommandHandler('cancel', profile_cancel)]
    )

    affiliate_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(affiliate_generate_start, pattern='^affiliate_generate_start$')],
        states={
            States.AFFILIATE_PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, affiliate_generate_product_name)]
        },
        fallbacks=[CommandHandler('cancel', cancel_command)]
    )
    application.add_handler(CommandHandler('analytics_dashboard', analytics_dashboard_handler))
    application.add_handler(CommandHandler('referral_leaderboard', referral_leaderboard_handler))

    xrpl_info_conv = ConversationHandler(
        entry_points=[
            CommandHandler('xrplinfo', xrpl_info_start),
            CallbackQueryHandler(xrpl_info_start, pattern='^personal_area_xrpl_info_start$')
        ],
        states={
            States.XRPL_ADDRESS_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, xrpl_address_received_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel_command)]
    )

    calculator_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(calculator_start, pattern='^tool_calculator_start$')],
        states={
            States.CALCULATOR_FIRST_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculator_first_number_handler)],
            States.CALCULATOR_OPERATOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculator_operator_handler)],
            States.CALCULATOR_SECOND_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculator_second_number_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel_command)]
    )

    weather_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(weather_start, pattern='^tool_weather_start$')],
        states={
            States.WEATHER_LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, weather_location_handler)],
        },
        fallbacks=[CommandHandler('cancel', cancel_command)]
    )
    
    ai_chat_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(ai_chat_start, pattern='^menu_ai_chat$')],
        states={
            States.AI_CHAT_ACTIVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat_handler)],
        },
        fallbacks=[CommandHandler('cancel', ai_chat_cancel)]
    )
    application.add_handler(CommandHandler('bild', bild_command))
    application.add_handler(CommandHandler('video', video_command))

    wallet_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_wallet_start, pattern='^personal_area_add_wallet_start$'),
            CallbackQueryHandler(remove_wallet_start, pattern='^personal_area_remove_wallet_start$'),
            CallbackQueryHandler(wallet_transaction_history, pattern='^personal_area_wallet_transaction_history$'),
            CallbackQueryHandler(internal_transfer_start, pattern='^personal_area_internal_transfer_start$'),
            # NEU: Entry Points für interne Wallet-Funktionen
            CallbackQueryHandler(internal_wallet_deposit_start, pattern='^personal_area_internal_deposit$'),
            CallbackQueryHandler(internal_wallet_withdraw_start, pattern='^personal_area_internal_withdraw$')
        ],
        states={
            States.ADD_WALLET_CURRENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_wallet_currency_handler)],
            States.ADD_WALLET_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_wallet_address_handler)],
            States.REMOVE_WALLET_SELECT: [CallbackQueryHandler(remove_wallet_select_handler, pattern='^del_wallet_|^cancel_action$')],
            States.INTERNAL_TRANSFER_RECEIVER: [MessageHandler(filters.TEXT & ~filters.COMMAND, internal_transfer_receiver_handler)],
            States.INTERNAL_TRANSFER_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, internal_transfer_amount_handler)],
            # NEU: States für interne Wallet-Funktionen
            States.INTERNAL_WALLET_DEPOSIT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, internal_wallet_deposit_amount)],
            States.INTERNAL_WALLET_WITHDRAW_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, internal_wallet_withdraw_amount)]
        },
        fallbacks=[CommandHandler('cancel', cancel_command), CallbackQueryHandler(main_menu_view, pattern='^back_to_main_menu$')]
    )

    # NEU: Marktplatz Conversation Handler
    marketplace_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_product_start, pattern='^marketplace_add_product_start$'),
            CallbackQueryHandler(view_product, pattern='^view_product_'), # Für das direkte Anzeigen eines Produkts
            CallbackQueryHandler(confirm_buy, pattern='^buy_product_confirm_') # Für die Kaufbestätigung
        ],
        states={
            States.MARKETPLACE_ADD_PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_name)],
            States.MARKETPLACE_ADD_PRODUCT_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_description)],
            States.MARKETPLACE_ADD_PRODUCT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_price)],
            # Korrektur: filters.DOCUMENT zu filters.Document.ALL geändert
            States.MARKETPLACE_ADD_PRODUCT_FILE: [MessageHandler(filters.PHOTO | filters.Document.ALL, add_product_file)],
            States.MARKETPLACE_ADD_PRODUCT_CONFIRM: [CallbackQueryHandler(add_product_confirm, pattern='^(confirm_add_product|cancel_action)$')],
            States.MARKETPLACE_VIEW_PRODUCT: [CallbackQueryHandler(view_product, pattern='^view_product_|^list_products$'), CallbackQueryHandler(confirm_buy, pattern='^buy_product_confirm_')], 
            States.MARKETPLACE_CONFIRM_BUY: [CallbackQueryHandler(confirm_buy, pattern='^buy_product_confirm_')]
        },
        fallbacks=[CommandHandler('cancel', cancel_command), CallbackQueryHandler(marketplace_menu_view, pattern='^marketplace_menu$')]
    )


    application.add_handler(admin_conv)
    application.add_handler(feedback_conv)
    application.add_handler(game_conv)
    application.add_handler(pool_stats_conv)
    application.add_handler(calculator_conv)
    application.add_handler(weather_conv)
    application.add_handler(ai_chat_conv)
    application.add_handler(wallet_conv)
    application.add_handler(image_upload_conv)
    application.add_handler(affiliate_conv)
    application.add_handler(xrpl_info_conv)
    application.add_handler(marketplace_conv) # NEU: Marktplatz Conversation Handler hinzufügen


    # --- Command Handlers ---
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("language", language_menu))
    application.add_handler(CommandHandler("cancel", cancel_command))
    
    application.add_handler(CommandHandler("kurs", handle_kurs))
    application.add_handler(CommandHandler("preis", handle_preis))
    application.add_handler(CommandHandler("wetter", handle_wetter))
    # CommandHandler für /xrplinfo ist jetzt im ConversationHandler entry_points

    # --- Explizite CallbackQuery Handlers ---
    application.add_handler(CallbackQueryHandler(main_menu_view, pattern='^back_to_main_menu$'))
    application.add_handler(CallbackQueryHandler(earn_money_menu_view, pattern='^menu_geld_verdienen$'))
    application.add_handler(CallbackQueryHandler(tools_menu_view, pattern='^menu_tools$'))
    application.add_handler(CallbackQueryHandler(dashboard_menu_view, pattern='^menu_dashboard$'))
    application.add_handler(CallbackQueryHandler(dashboard_menu_view, pattern='^menu_personal_area$')) # Alias
    application.add_handler(CallbackQueryHandler(help_command, pattern='^menu_help$'))
    application.add_handler(CallbackQueryHandler(language_menu, pattern='^menu_language$'))
    application.add_handler(CallbackQueryHandler(set_language, pattern='^set_lang_'))
    application.add_handler(CallbackQueryHandler(crypto_swap_menu_view, pattern='^sub_geld_krypto_swap_menu$'))
    application.add_handler(CallbackQueryHandler(image_sell_menu_view, pattern='^sub_geld_bilder_menu$'))
    application.add_handler(CallbackQueryHandler(affiliate_menu_view, pattern='^sub_geld_affiliate_menu$'))
    
    application.add_handler(CallbackQueryHandler(get_crypto_prices_handler, pattern='^krypto_kurse$'))
    
    application.add_handler(CallbackQueryHandler(show_xrpl_dex_info, pattern='^xrpl_dex_swap_info$'))
    application.add_handler(CallbackQueryHandler(show_time, pattern='^tool_time$'))
    application.add_handler(CallbackQueryHandler(show_wip, pattern='^bilder_sales$'))
    application.add_handler(CallbackQueryHandler(show_wip, pattern='^affiliate_stats$'))
    application.add_handler(CallbackQueryHandler(my_wallets_menu, pattern='^personal_area_my_wallets$'))
    application.add_handler(CallbackQueryHandler(wallet_transaction_history, pattern='^personal_area_wallet_transaction_history$'))
    application.add_handler(CallbackQueryHandler(my_pools_menu, pattern='^personal_area_my_pools$'))
    application.add_handler(CallbackQueryHandler(check_balances, pattern='^personal_area_check_balances$'))
    application.add_handler(CallbackQueryHandler(admin_bot_status, pattern='^admin_bot_status$'))
    application.add_handler(CallbackQueryHandler(admin_read_feedback, pattern='^admin_read_feedback$'))
    application.add_handler(CallbackQueryHandler(admin_check_news_manual, pattern='^admin_check_news_feed_manual$'))
    
    # NEU: Marktplatz-Menüpunkte und Aktionen
    application.add_handler(CallbackQueryHandler(marketplace_menu_view, pattern='^menu_marketplace$')) # Haupteinstieg
    application.add_handler(CallbackQueryHandler(list_products, pattern='^marketplace_view_products$'))
    application.add_handler(CallbackQueryHandler(my_selling_products, pattern='^marketplace_my_products$')) # Eigene Produkte anzeigen
    application.add_handler(CallbackQueryHandler(marketplace_menu_view, pattern='^marketplace_menu$')) # Rückkehr zum Marktplatz-Menü



    # --- Error Handler ---
    application.add_error_handler(error_handler)

    # --- Jobs & Start ---
    application.job_queue.run_repeating(check_and_post_news, interval=NEWS_CHECK_INTERVAL_SECONDS)
    # Schedule daily summary at 8 AM every day
    application.job_queue.run_daily(send_daily_summary, time=datetime.time(hour=8, minute=0, second=0))
    logger.info("Bot startet Polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
