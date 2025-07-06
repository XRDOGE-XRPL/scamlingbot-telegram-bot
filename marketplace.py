import sqlite3
import urllib.parse
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters
from telegram.constants import ParseMode

from database import (
    add_product, get_all_active_products, get_product_by_id,
    process_transaction, get_user_products
)
from keyboards import (
    get_marketplace_menu_keyboard, get_affiliate_links_menu_keyboard,
    get_bilder_verkaufen_menu_keyboard
)

logger = logging.getLogger(__name__)

# Conversation states should be imported from main.py or defined here if needed
# For simplicity, assume they are imported from main.py
from main import States

async def marketplace_menu_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        await context.bot_data['T']("marketplace_title", context),
        reply_markup=await get_marketplace_menu_keyboard(context)
    )

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

async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = context.user_data.get('marketplace_filter_category')
    products = get_all_active_products(category)
    if not products:
        await query.edit_message_text("Keine Produkte gefunden.", reply_markup=await get_marketplace_menu_keyboard(context))
        return
    text = "Verfügbare Produkte:\n\n"
    keyboard_buttons = []
    for p_id, seller_id, name, description, price, currency, file_path, status in products:
        text += f"▪️ {name} ({price:.2f} {currency})\n"
        keyboard_buttons.append([InlineKeyboardButton(name, callback_data=f"view_product_{p_id}")])
    keyboard_buttons.append([InlineKeyboardButton("Zurück", callback_data="marketplace_menu")])
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard_buttons))

async def view_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = int(query.data.split('_')[-1])
    product = get_product_by_id(product_id)

    if not product:
        await query.edit_message_text("Produkt nicht gefunden oder nicht verfügbar.", reply_markup=await get_marketplace_menu_keyboard(context))
        return

    p_id, seller_id, name, description, price, currency, file_path, status = product

    fee_amount = price * 0.01
    total_price = price + fee_amount

    product_text = (
        f"**{name}**\n\n"
        f"Beschreibung: {description}\n"
        f"Preis: {price:.2f} {currency}\n"
        f"Gebühr: {fee_amount:.2f} {currency} (1%)\n"
        f"Gesamtpreis: {total_price:.2f} {currency}\n\n"
        f"Verkäufer: Nutzer {seller_id}\n"
    )

    if query.from_user.id == seller_id:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Dein Produkt", callback_data='ignore')],
            [InlineKeyboardButton("Zurück", callback_data='marketplace_view_products')]
        ])
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Kaufen für {total_price:.2f} {currency}", callback_data=f"buy_product_confirm_{p_id}")],
            [InlineKeyboardButton("Zurück", callback_data='marketplace_view_products')]
        ])

    context.user_data['marketplace_selected_product_id'] = p_id
    await query.edit_message_text(product_text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

async def confirm_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = int(query.data.split('_')[-1])

    product = get_product_by_id(product_id)
    if not product:
        await query.edit_message_text("Produkt nicht gefunden oder nicht verfügbar.", reply_markup=await get_marketplace_menu_keyboard(context))
        return ConversationHandler.END

    p_id, seller_id, name, description, price, currency, file_path, status = product

    if query.from_user.id == seller_id:
        await query.edit_message_text("Du kannst dein eigenes Produkt nicht kaufen.", reply_markup=await get_marketplace_menu_keyboard(context))
        return ConversationHandler.END

    buyer_id = query.from_user.id
    buyer_balance = get_user_internal_balance(buyer_id)
    fee_amount = price * 0.01
    total_price = price + fee_amount

    if buyer_balance < total_price:
        await query.edit_message_text(f"Unzureichendes Guthaben! Dein Guthaben: {buyer_balance:.2f} SCAMCOIN. Benötigt: {total_price:.2f} SCAMCOIN.", reply_markup=await get_marketplace_menu_keyboard(context))
        return ConversationHandler.END

    success = process_transaction(
        product_id=p_id,
        buyer_id=buyer_id,
        seller_id=seller_id,
        price=price,
        fee_percentage=0.01
    )

    if success:
        try:
            await context.bot.send_document(chat_id=buyer_id, document=file_path, caption=f"Dein Kauf: {name}")
            await query.edit_message_text(f"✅ Du hast '{name}' erfolgreich gekauft für {total_price:.2f} {currency}.", reply_markup=await get_marketplace_menu_keyboard(context))
            # Notify seller about the sale
            await context.bot.send_message(chat_id=seller_id, text=f"🎉 Dein Produkt '{name}' wurde verkauft! Du hast {price * 0.99:.2f} {currency} erhalten.")
            # Log affiliate sale if affiliate referrer exists
            affiliate_referrer = context.user_data.get('affiliate_referrer')
            if affiliate_referrer:
                from affiliate_tracking import log_affiliate_sale
                log_affiliate_sale(affiliate_referrer, name, price)
        except Exception as e:
            logger.error(f"Fehler beim Senden der Datei an Nutzer {buyer_id}: {e}")
            await query.edit_message_text(f"✅ Du hast '{name}' gekauft, aber es gab ein Problem bei der Zustellung der Datei.", reply_markup=await get_marketplace_menu_keyboard(context))
    else:
        await query.edit_message_text("Kauf fehlgeschlagen. Bitte versuche es später erneut.", reply_markup=await get_marketplace_menu_keyboard(context))

    return ConversationHandler.END

async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Bitte gib den Namen deines Produkts ein:")
    return States.MARKETPLACE_ADD_PRODUCT_NAME

async def add_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['marketplace_product_name'] = update.message.text
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("General", callback_data='category_General')],
        [InlineKeyboardButton("E-Books", callback_data='category_EBooks')],
        [InlineKeyboardButton("Software", callback_data='category_Software')],
        [InlineKeyboardButton("Art", callback_data='category_Art')],
        [InlineKeyboardButton("Music", callback_data='category_Music')],
        [InlineKeyboardButton("Other", callback_data='category_Other')],
    ])
    await update.message.reply_text("Bitte wähle eine Kategorie für dein Produkt:", reply_markup=keyboard)
    return States.MARKETPLACE_ADD_PRODUCT_DESCRIPTION

async def add_product_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query and update.callback_query.data.startswith('category_'):
        category = update.callback_query.data.split('_')[1]
        context.user_data['marketplace_product_category'] = category
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Bitte gib eine Beschreibung für dein Produkt ein:")
        return States.MARKETPLACE_ADD_PRODUCT_DESCRIPTION
    else:
        context.user_data['marketplace_product_description'] = update.message.text
        await update.message.reply_text("Bitte gib den Preis für dein Produkt in SCAMCOIN ein:")
        return States.MARKETPLACE_ADD_PRODUCT_PRICE

async def add_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(update.message.text.replace(',', '.'))
        if price <= 0:
            raise ValueError
        context.user_data['marketplace_product_price'] = price
        context.user_data['marketplace_product_currency'] = "SCAMCOIN"
        await update.message.reply_text("Bitte sende nun die Datei für dein Produkt (Foto oder Dokument).")
        return States.MARKETPLACE_ADD_PRODUCT_FILE
    except ValueError:
        await update.message.reply_text("Ungültiger Preis. Bitte gib eine positive Zahl ein.")
        return States.MARKETPLACE_ADD_PRODUCT_PRICE

async def add_product_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_name = f"photo_{file_id}.jpg"
    else:
        await update.message.reply_text("Bitte sende eine gültige Datei (Dokument oder Foto).")
        return States.MARKETPLACE_ADD_PRODUCT_FILE

    context.user_data['marketplace_product_file_id'] = file_id

    name = context.user_data['marketplace_product_name']
    description = context.user_data['marketplace_product_description']
    price = context.user_data['marketplace_product_price']
    currency = context.user_data['marketplace_product_currency']
    category = context.user_data.get('marketplace_product_category', 'General')

    preview_text = (
        f"**Produktvorschau:**\n\n"
        f"Name: {name}\n"
        f"Beschreibung: {description}\n"
        f"Preis: {price:.2f} {currency}\n"
        f"Datei: {file_name}\n"
        f"Kategorie: {category}\n\n"
        f"Möchtest du dieses Produkt einstellen?"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Ja", callback_data='confirm_add_product')],
        [InlineKeyboardButton("Nein", callback_data='cancel_action')]
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
            await query.edit_message_text(f"✅ Produkt '{name}' wurde erfolgreich eingestellt!", reply_markup=await get_marketplace_menu_keyboard(context))
        else:
            await query.edit_message_text("❌ Produkt konnte nicht eingestellt werden. Bitte versuche es erneut.", reply_markup=await get_marketplace_menu_keyboard(context))
    else:
        await query.edit_message_text("Produkteinstellung abgebrochen.", reply_markup=await get_marketplace_menu_keyboard(context))

    return ConversationHandler.END

async def my_selling_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_products = get_user_products(query.from_user.id)

    if not user_products:
        await query.edit_message_text("Du hast aktuell keine Produkte zum Verkauf gelistet.", reply_markup=await get_marketplace_menu_keyboard(context))
        return ConversationHandler.END

    text = "Deine Produkte zum Verkauf:\n\n"
    keyboard_buttons = []
    for p_id, seller_id, name, description, price, currency, file_path, status in user_products:
        text += f"▪️ {name} ({price:.2f} {currency}) - Status: {status}\n"
        keyboard_buttons.append([InlineKeyboardButton(f"Löschen {name}", callback_data=f"delete_product_{p_id}")])

    keyboard_buttons.append([InlineKeyboardButton("Zurück", callback_data="marketplace_menu")])
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard_buttons))
    return ConversationHandler.END

async def delete_product_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = int(query.data.replace("delete_product_", ""))
    user_id = query.from_user.id

    product = get_product_by_id(product_id)
    if not product or product[1] != user_id:
        await query.edit_message_text("Produkt nicht gefunden oder du bist nicht der Verkäufer.", reply_markup=await get_marketplace_menu_keyboard(context))
        return ConversationHandler.END

    try:
        conn = sqlite3.connect('scamlingbot.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE products SET status = "deleted" WHERE id = ?', (product_id,))
        conn.commit()
    except Exception as e:
        await query.edit_message_text(f"Fehler beim Löschen des Produkts: {e}", reply_markup=await get_marketplace_menu_keyboard(context))
        return ConversationHandler.END
    finally:
        conn.close()

    await query.edit_message_text("Produkt wurde gelöscht.", reply_markup=await get_marketplace_menu_keyboard(context))
    return ConversationHandler.END
