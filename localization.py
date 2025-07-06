# =================================================================================
# 2. LOKALISIERUNG & TEXTE
# =================================================================================

LOCALIZATION_DATA = {
    "en": {
        "welcome": "Welcome {name}! How can I help you today?",
        "help_title": "Help & Information",
        "help_body": "Here you can find information about the bot's features:",
        "menu_earn_money": "💰 Earn Money",
        "menu_ai_chat": "🤖 AI Chat",
        "menu_tools": "🛠️ Tools",
        "menu_dashboard": "🗄️ Dashboard",
        "menu_help": "❓ Help",
        "menu_language": "🌐 Language",
        "menu_marketplace": "🛒 Marketplace", # NEU
        "sub_geld_crypto_swap": "🔄 Crypto Swap",
        "sub_geld_sell_pictures": "🖼️ Sell Pictures",
        "sub_geld_affiliate_links": "🔗 Affiliate Links",
        "back_to_main": "⬅️ Back to Main Menu",
        "back_to_dashboard": "⬅️ Back to Dashboard",
        "select_language": "Please choose your language:",
        "language_set": "Language set successfully!",
        "feedback_prompt": "Please send your feedback. It helps us improve!",
        "feedback_thanks": "Thank you for your feedback!",
        "admin_feedback_notification": "New Feedback from {user}:\n\n{text}",
        "admin_stats_title": "📊 Bot Status",
        "admin_stats_body": "Total users: {total_users}\nUsers with feedback: {users_with_feedback}\nTotal products: {total_products}\nTotal transactions: {total_transactions}", # NEU: Stats
        "admin_no_feedback": "No feedback available.",
        "tool_weather": "☀️ Weather",
        "tool_calculator": "🧮 Calculator",
        "tool_crypto_game": "🎮 Crypto Game",
        "tool_time": "⏰ Current Time",
        "earn_money_title": "How would you like to earn money?",
        "tools_menu_title": "Select a tool:",
        "dashboard_title": "Your Personal Dashboard",
        "crypto_swap_title": "Crypto Swap & Info",
        "image_sell_title": "Sell your digital art/photos!",
        "affiliate_title": "Generate and manage affiliate links!",
        "wip": "Work in progress! This feature is not yet available.",
        "personal_area_my_wallets": "💳 My Wallets",
        "personal_area_my_pools": "⛏️ My Mining Pools",
        "personal_area_xrpl_info": "📊 XRPL Account Info",
        "wallet_add": "➕ Add Wallet",
        "wallet_remove": "➖ Remove Wallet",
        "wallet_check_balances": "💰 Check Balances",
        "my_wallets_title": "Your Registered Wallets:",
        "no_wallets": "No wallets registered yet.",
        "no_external_wallets": "No external wallets registered yet.", # NEU
        "internal_balance_label": "Internal Balance", # NEU
        "internal_wallet_deposit": "⬆️ Deposit SCAMCOIN", # NEU
        "internal_wallet_withdraw": "⬇️ Withdraw SCAMCOIN", # NEU
        "internal_wallet_deposit_prompt": "Enter the amount of SCAMCOIN you want to deposit (e.g., 100).", # NEU
        "internal_wallet_deposit_success": "✅ Successfully deposited {amount:.2f} SCAMCOIN. Your new balance is {balance:.2f} SCAMCOIN.", # NEU
        "internal_wallet_deposit_failed": "❌ Deposit failed. Please try again later.", # NEU
        "internal_wallet_withdraw_prompt": "Enter the amount of SCAMCOIN you want to withdraw. Your current balance: {balance:.2f} SCAMCOIN.", # NEU
        "internal_wallet_withdraw_success": "✅ Successfully withdrew {amount:.2f} SCAMCOIN. Your new balance is {balance:.2f} SCAMCOIN.", # NEU
        "internal_wallet_withdraw_failed": "❌ Withdrawal failed. Please try again later.", # NEU
        "internal_wallet_invalid_amount": "Invalid amount. Please enter a positive number.", # NEU
        "internal_wallet_invalid_withdraw_amount": "Invalid amount. Please enter a positive number less than or equal to your balance.", # NEU
        "my_pools_title": "Your Registered Mining Pools:",
        "no_pools": "No mining pools registered yet.",
        "pool_add": "➕ Add Pool",
        "pool_remove": "➖ Remove Pool",
        "pool_check_all": "📈 Check My Pool Stats",
        "pool_general_stats": "📊 General Pool Stats",
        "fetching_xrpl_info": "Fetching data, please wait...",
        "invalid_xrpl_address": "Invalid XRPL address. Please try again.",
        "yes_confirm": "✅ YES, CONFIRM", # NEU
        "no_cancel": "❌ NO, CANCEL", # NEU

        # NEU: Marktplatz Texte
        "marketplace_title": "🛒 Marketplace",
        "marketplace_view_products": "📦 View Products",
        "marketplace_add_product": "📝 List Product",
        "marketplace_my_products": "🛍️ My Listings & Purchases", # Könnte später geteilt werden
        "marketplace_no_products": "Currently no products available on the marketplace.",
        "marketplace_available_products": "Available Products:",
        "marketplace_product_not_found": "Product not found or no longer available.",
        "marketplace_description": "Description",
        "marketplace_price": "Price",
        "marketplace_fee": "Bot Fee (1%)",
        "marketplace_total_price": "Total Price",
        "marketplace_seller": "Seller",
        "marketplace_buy_button": "Buy for {price:.2f} {currency}",
        "marketplace_insufficient_funds": "Insufficient funds! Your balance: {balance:.2f} SCAMCOIN. Needed: {needed:.2f} SCAMCOIN.",
        "marketplace_purchase_success": "✅ You have successfully purchased '{name}' for {price:.2f} {currency}. The digital good has been sent to you.",
        "marketplace_purchase_success_no_delivery": "✅ You have successfully purchased '{name}'. However, there was an issue delivering the file. Please contact support.",
        "marketplace_purchase_failed": "❌ Purchase failed. Please try again later.",
        "marketplace_cannot_buy_own": "You cannot buy your own product.",
        "marketplace_seller_notification": "🎉 Your product '{name}' has been sold! You received {price:.2f} {currency}.",
        "marketplace_add_name_prompt": "Enter the name of your product (e.g., 'E-Book: Python Basics').",
        "marketplace_add_description_prompt": "Enter a description for your product.",
        "marketplace_add_price_prompt": "Enter the price in SCAMCOIN (e.g., 50.00).",
        "marketplace_add_file_prompt": "Now, send the digital file (PDF, image, ZIP, etc.) for your product.",
        "marketplace_add_file_error": "Please send a valid file (document or photo).",
        "marketplace_invalid_price": "Invalid price. Please enter a positive number (e.g., 10.50).",
        "marketplace_preview_title": "Product Preview:",
        "marketplace_product_name": "Product Name",
        "marketplace_file": "File",
        "marketplace_confirm_add_prompt": "Do you want to list this product?",
        "marketplace_product_added_success": "✅ Product '{name}' has been successfully listed on the marketplace!",
        "marketplace_product_add_failed": "❌ Failed to list product. Please try again.",
        "marketplace_add_product_cancelled": "Product listing cancelled.",
        "marketplace_no_selling_products": "You currently have no products listed for sale.",
        "marketplace_your_products_title": "Your Products for Sale:",
        "marketplace_your_product": "This is your product.",
        "back_to_products": "⬅️ Back to Products",
    },
    "de": {
        "welcome": "Willkommen {name}! Wie kann ich dir heute helfen?",
        "help_title": "Hilfe & Informationen",
        "help_body": "Hier findest du Informationen zu den Funktionen des Bots:",
        "menu_earn_money": "💰 Geld verdienen",
        "menu_ai_chat": "🤖 KI Chat",
        "menu_tools": "🛠️ Tools",
        "menu_dashboard": "🗄️ Dashboard",
        "menu_help": "❓ Hilfe",
        "menu_language": "🌐 Sprache",
        "menu_marketplace": "🛒 Marktplatz", # NEU
        "sub_geld_crypto_swap": "🔄 Krypto Swap",
        "sub_geld_sell_pictures": "🖼️ Bilder verkaufen",
        "sub_geld_affiliate_links": "🔗 Affiliate Links",
        "back_to_main": "⬅️ Zum Hauptmenü",
        "back_to_dashboard": "⬅️ Zum Dashboard",
        "select_language": "Bitte wähle deine Sprache:",
        "language_set": "Sprache erfolgreich eingestellt!",
        "feedback_prompt": "Bitte sende dein Feedback. Es hilft uns, uns zu verbessern!",
        "feedback_thanks": "Vielen Dank für dein Feedback!",
        "admin_feedback_notification": "Neues Feedback von {user}:\n\n{text}",
        "admin_stats_title": "📊 Bot Status",
        "admin_stats_body": "Gesamtzahl Nutzer: {total_users}\nNutzer mit Feedback: {users_with_feedback}\nGesamtzahl Produkte: {total_products}\nGesamtzahl Transaktionen: {total_transactions}", # NEU: Stats
        "admin_no_feedback": "Kein Feedback verfügbar.",
        "tool_weather": "☀️ Wetter",
        "tool_calculator": "🧮 Taschenrechner",
        "tool_crypto_game": "🎮 Krypto Spiel",
        "tool_time": "⏰ Aktuelle Uhrzeit",
        "earn_money_title": "Wie möchtest du Geld verdienen?",
        "tools_menu_title": "Wähle ein Tool:",
        "dashboard_title": "Dein persönliches Dashboard",
        "crypto_swap_title": "Krypto Swap & Info",
        "image_sell_title": "Verkaufe deine digitalen Kunstwerke/Fotos!",
        "affiliate_title": "Generiere und verwalte Affiliate-Links!",
        "wip": "In Arbeit! Diese Funktion ist noch nicht verfügbar.",
        "personal_area_my_wallets": "💳 Meine Wallets",
        "personal_area_my_pools": "⛏️ Meine Mining Pools",
        "personal_area_xrpl_info": "📊 XRPL Account Info",
        "wallet_add": "➕ Wallet hinzufügen",
        "wallet_remove": "➖ Wallet entfernen",
        "wallet_check_balances": "💰 Guthaben prüfen",
        "my_wallets_title": "Deine registrierten Wallets:",
        "no_wallets": "Noch keine Wallets registriert.",
        "no_external_wallets": "Noch keine externen Wallets registriert.", # NEU
        "internal_balance_label": "Internes Guthaben", # NEU
        "internal_wallet_deposit": "⬆️ SCAMCOIN einzahlen", # NEU
        "internal_wallet_withdraw": "⬇️ SCAMCOIN abheben", # NEU
        "internal_wallet_deposit_prompt": "Gib den Betrag an SCAMCOIN ein, den du einzahlen möchtest (z.B. 100).", # NEU
        "internal_wallet_deposit_success": "✅ Erfolgreich {amount:.2f} SCAMCOIN eingezahlt. Dein neues Guthaben beträgt {balance:.2f} SCAMCOIN.", # NEU
        "internal_wallet_deposit_failed": "❌ Einzahlung fehlgeschlagen. Bitte versuche es später erneut.", # NEU
        "internal_wallet_withdraw_prompt": "Gib den Betrag an SCAMCOIN ein, den du abheben möchtest. Dein aktuelles Guthaben: {balance:.2f} SCAMCOIN.", # NEU
        "internal_wallet_withdraw_success": "✅ Erfolgreich {amount:.2f} SCAMCOIN abgehoben. Dein neues Guthaben beträgt {balance:.2f} SCAMCOIN.", # NEU
        "internal_wallet_withdraw_failed": "❌ Abhebung fehlgeschlagen. Bitte versuche es später erneut.", # NEU
        "internal_wallet_invalid_amount": "Ungültiger Betrag. Bitte gib eine positive Zahl ein.", # NEU
        "internal_wallet_invalid_withdraw_amount": "Ungültiger Betrag. Bitte gib eine positive Zahl ein, die kleiner oder gleich deinem Guthaben ist.", # NEU
        "my_pools_title": "Deine registrierten Mining Pools:",
        "no_pools": "Noch keine Mining Pools registriert.",
        "pool_add": "➕ Pool hinzufügen",
        "pool_remove": "➖ Pool entfernen",
        "pool_check_all": "📈 Meine Pool-Statistiken prüfen",
        "pool_general_stats": "📊 Allgemeine Pool-Statistiken",
        "fetching_xrpl_info": "Daten werden abgerufen, bitte warten...",
        "invalid_xrpl_address": "Ungültige XRPL-Adresse. Bitte versuche es erneut.",
        "yes_confirm": "✅ JA, BESTÄTIGEN", # NEU
        "no_cancel": "❌ NEIN, ABBRECHEN", # NEU

        # NEU: Marktplatz Texte
        "marketplace_title": "🛒 Marktplatz",
        "marketplace_view_products": "📦 Produkte ansehen",
        "marketplace_add_product": "📝 Produkt einstellen",
        "marketplace_my_products": "🛍️ Meine Angebote & Käufe",
        "marketplace_no_products": "Aktuell keine Produkte auf dem Marktplatz verfügbar.",
        "marketplace_available_products": "Verfügbare Produkte:",
        "marketplace_product_not_found": "Produkt nicht gefunden oder nicht mehr verfügbar.",
        "marketplace_description": "Beschreibung",
        "marketplace_price": "Preis",
        "marketplace_fee": "Bot-Gebühr (1%)",
        "marketplace_total_price": "Gesamtpreis",
        "marketplace_seller": "Verkäufer",
        "marketplace_buy_button": "Kaufen für {price:.2f} {currency}",
        "marketplace_insufficient_funds": "Unzureichendes Guthaben! Dein Guthaben: {balance:.2f} SCAMCOIN. Benötigt: {needed:.2f} SCAMCOIN.",
        "marketplace_purchase_success": "✅ Du hast '{name}' erfolgreich für {price:.2f} {currency} gekauft. Das digitale Gut wurde dir zugesandt.",
        "marketplace_purchase_success_no_delivery": "✅ Du hast '{name}' erfolgreich gekauft. Es gab jedoch ein Problem bei der Zustellung der Datei. Bitte kontaktiere den Support.",
        "marketplace_purchase_failed": "❌ Kauf fehlgeschlagen. Bitte versuche es später erneut.",
        "marketplace_cannot_buy_own": "Du kannst dein eigenes Produkt nicht kaufen.",
        "marketplace_seller_notification": "🎉 Dein Produkt '{name}' wurde verkauft! Du hast {price:.2f} {currency} erhalten.",
        "marketplace_add_name_prompt": "Gib den Namen deines Produkts ein (z.B. 'E-Book: Python Grundlagen').",
        "marketplace_add_description_prompt": "Gib eine Beschreibung für dein Produkt ein.",
        "marketplace_add_price_prompt": "Gib den Preis in SCAMCOIN ein (z.B. 50.00).",
        "marketplace_add_file_prompt": "Sende nun die digitale Datei (PDF, Bild, ZIP, etc.) für dein Produkt.",
        "marketplace_add_file_error": "Bitte sende eine gültige Datei (Dokument oder Foto).",
        "marketplace_invalid_price": "Ungültiger Preis. Bitte gib eine positive Zahl ein (z.B. 10.50).",
        "marketplace_preview_title": "Produktvorschau:",
        "marketplace_product_name": "Produktname",
        "marketplace_file": "Datei",
        "marketplace_confirm_add_prompt": "Möchtest du dieses Produkt einstellen?",
        "marketplace_product_added_success": "✅ Produkt '{name}' wurde erfolgreich auf dem Marktplatz eingestellt!",
        "marketplace_product_add_failed": "❌ Produkt konnte nicht eingestellt werden. Bitte versuche es erneut.",
        "marketplace_add_product_cancelled": "Produkteinstellung abgebrochen.",
        "marketplace_no_selling_products": "Du hast aktuell keine Produkte zum Verkauf gelistet.",
        "marketplace_your_products_title": "Deine Produkte zum Verkauf:",
        "marketplace_your_product": "Dies ist dein Produkt.",
        "back_to_products": "⬅️ Zurück zu den Produkten",
    }
}

async def T(key: str, context: object, **kwargs) -> str:
    user_id = context.effective_user.id if hasattr(context, 'effective_user') else None
    
    # Versuche, die Sprache aus user_data zu holen, da sie dort für die aktuelle Session gespeichert wird
    lang = context.user_data.get('lang')
    
    # Wenn nicht in user_data, versuche aus der Datenbank zu laden
    if not lang and user_id:
        from database import get_user_language_from_db # Importiere hier, um Zirkelabhängigkeit zu vermeiden
        lang = get_user_language_from_db(user_id)

    # Fallback auf Englisch, falls keine Sprache gefunden wird
    if lang not in LOCALIZATION_DATA:
        lang = 'en'

    text = LOCALIZATION_DATA[lang].get(key, LOCALIZATION_DATA['en'].get(key, f"UNKNOWN_TEXT_KEY_{key}"))

    # Ersetze Platzhalter
    if kwargs:
        text = text.format(**kwargs)
    
    return text

