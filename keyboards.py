from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from localization import T # Stellen Sie sicher, dass T importiert ist

# =================================================================================
# 4. KEYBOARD-GENERATOREN
# =================================================================================

async def get_main_menu_keyboard(context):
    keyboard = [
        [InlineKeyboardButton(await T("menu_earn_money", context), callback_data='menu_geld_verdienen')],
        [InlineKeyboardButton(await T("menu_ai_chat", context), callback_data='menu_ai_chat')],
        [InlineKeyboardButton(await T("menu_tools", context), callback_data='menu_tools')],
        [InlineKeyboardButton(await T("menu_dashboard", context), callback_data='menu_personal_area')],
        # NEU: Marktplatz im Hauptmenü
        [InlineKeyboardButton(await T("menu_marketplace", context), callback_data='menu_marketplace')], 
        [InlineKeyboardButton(await T("menu_help", context), callback_data='menu_help'),
         InlineKeyboardButton(await T("menu_language", context), callback_data='menu_language')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_geld_verdienen_menu_keyboard(context):
    keyboard = [
        [InlineKeyboardButton(await T("sub_geld_crypto_swap", context), callback_data='sub_geld_krypto_swap_menu')],
        [InlineKeyboardButton(await T("sub_geld_sell_pictures", context), callback_data='sub_geld_bilder_menu')],
        [InlineKeyboardButton(await T("sub_geld_affiliate_links", context), callback_data='sub_geld_affiliate_menu')],
        [InlineKeyboardButton(await T("back_to_main", context), callback_data='back_to_main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_krypto_swap_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("💰 Krypto Kurse", callback_data='krypto_kurse')],
        [InlineKeyboardButton("🔄 XRPL DEX Swap Info", callback_data='xrpl_dex_swap_info')],
        [InlineKeyboardButton("⬅️ Zurück", callback_data='sub_geld_verdienen_menu')] # Anpassen, falls zurück zum Geld verdienen Menü
    ]
    return InlineKeyboardMarkup(keyboard)

def get_bilder_verkaufen_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("⬆️ Bild hochladen", callback_data='bilder_upload_start')],
        [InlineKeyboardButton("📊 Meine Verkäufe", callback_data='marketplace_my_products')],
        [InlineKeyboardButton("⬅️ Zurück", callback_data='menu_geld_verdienen')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_affiliate_links_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🔗 Link generieren", callback_data='affiliate_generate_start')],
        [InlineKeyboardButton("📈 Meine Statistiken", callback_data='affiliate_stats')],
        [InlineKeyboardButton("⬅️ Zurück", callback_data='menu_geld_verdienen')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_tools_menu_keyboard(context):
    keyboard = [
        [InlineKeyboardButton(await T("tool_weather", context), callback_data='tool_weather_start')],
        [InlineKeyboardButton(await T("tool_calculator", context), callback_data='tool_calculator_start')],
        [InlineKeyboardButton(await T("tool_crypto_game", context), callback_data='tool_game_start')],
        [InlineKeyboardButton(await T("tool_time", context), callback_data='tool_time')],
        [InlineKeyboardButton(await T("back_to_main", context), callback_data='back_to_main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_personal_area_menu_keyboard(context):
    keyboard = [
        [InlineKeyboardButton(await T("personal_area_my_wallets", context), callback_data='personal_area_my_wallets')],
        [InlineKeyboardButton(await T("personal_area_my_pools", context), callback_data='personal_area_my_pools')],
        [InlineKeyboardButton(await T("personal_area_xrpl_info", context), callback_data='personal_area_xrpl_info_start')],
        [InlineKeyboardButton(await T("back_to_main", context), callback_data='back_to_main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_my_wallets_menu_keyboard(context):
    keyboard = [
        [InlineKeyboardButton(await T("wallet_add", context), callback_data='personal_area_add_wallet_start')],
        [InlineKeyboardButton(await T("wallet_remove", context), callback_data='personal_area_remove_wallet_start')],
        [InlineKeyboardButton(await T("wallet_check_balances", context), callback_data='personal_area_check_balances')],
        # NEU: Buttons für interne Wallet-Aktionen
        [InlineKeyboardButton(await T("internal_wallet_deposit", context), callback_data='personal_area_internal_deposit')],
        [InlineKeyboardButton(await T("internal_wallet_withdraw", context), callback_data='personal_area_internal_withdraw')],
        [InlineKeyboardButton("Transaktionsverlauf", callback_data='personal_area_wallet_transaction_history')],
        [InlineKeyboardButton(await T("back_to_dashboard", context), callback_data='menu_personal_area')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_my_pools_menu_keyboard(context):
    keyboard = [
        [InlineKeyboardButton(await T("pool_add", context), callback_data='personal_area_add_pool_start')],
        [InlineKeyboardButton(await T("pool_remove", context), callback_data='personal_area_remove_pool_start')],
        [InlineKeyboardButton(await T("pool_check_all", context), callback_data='personal_area_check_all_pools')],
        [InlineKeyboardButton(await T("pool_general_stats", context), callback_data='personal_area_general_pool_stats_start')], # Allgemein
        [InlineKeyboardButton(await T("back_to_dashboard", context), callback_data='menu_personal_area')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_admin_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 Bot Status", callback_data='admin_bot_status')],
        [InlineKeyboardButton("📢 Broadcast senden", callback_data='admin_broadcast_start')],
        [InlineKeyboardButton("✉️ Feedback lesen", callback_data='admin_read_feedback')],
        [InlineKeyboardButton("📰 News manuell prüfen", callback_data='admin_check_news_feed_manual')],
        [InlineKeyboardButton("⬅️ Zurück zum Hauptmenü", callback_data='back_to_main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# NEU: Marktplatz-Keyboards

async def get_marketplace_menu_keyboard(context):
    keyboard = [
        [InlineKeyboardButton(await T("marketplace_view_products", context), callback_data='marketplace_view_products')],
        [InlineKeyboardButton(await T("marketplace_add_product", context), callback_data='marketplace_add_product_start')],
        [InlineKeyboardButton(await T("marketplace_my_products", context), callback_data='marketplace_my_products')], # Eigene Produkte verwalten
        [InlineKeyboardButton(await T("back_to_main", context), callback_data='back_to_main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_marketplace_category_keyboard():
    keyboard = [
        [InlineKeyboardButton("General", callback_data='category_General')],
        [InlineKeyboardButton("E-Books", callback_data='category_EBooks')],
        [InlineKeyboardButton("Software", callback_data='category_Software')],
        [InlineKeyboardButton("Art", callback_data='category_Art')],
        [InlineKeyboardButton("Music", callback_data='category_Music')],
        [InlineKeyboardButton("Other", callback_data='category_Other')],
        [InlineKeyboardButton("Cancel", callback_data='cancel_action')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_marketplace_filter_keyboard():
    keyboard = [
        [InlineKeyboardButton("All", callback_data='filter_category_All')],
        [InlineKeyboardButton("General", callback_data='filter_category_General')],
        [InlineKeyboardButton("E-Books", callback_data='filter_category_EBooks')],
        [InlineKeyboardButton("Software", callback_data='filter_category_Software')],
        [InlineKeyboardButton("Art", callback_data='filter_category_Art')],
        [InlineKeyboardButton("Music", callback_data='filter_category_Music')],
        [InlineKeyboardButton("Other", callback_data='filter_category_Other')],
        [InlineKeyboardButton("Back", callback_data='marketplace_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Dieses Keyboard könnte verwendet werden, um ein spezifisches Produkt anzuzeigen
# Wird aber dynamisch im Handler generiert.
async def get_product_keyboard(context, product_id, is_seller=False, price=0.0, currency="SCAMCOIN"):
    if is_seller:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(await T("marketplace_your_product", context), callback_data='ignore')], # Placeholder
            [InlineKeyboardButton(await T("back_to_products", context), callback_data='marketplace_view_products')]
        ])
    else:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(await T("marketplace_buy_button", context, price=price, currency=currency), callback_data=f"buy_product_confirm_{product_id}")],
            [InlineKeyboardButton(await T("back_to_products", context), callback_data='marketplace_view_products')]
        ])

