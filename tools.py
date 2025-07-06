import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, CommandHandler, filters
from telegram.constants import ParseMode

from localization import T
from keyboards import get_tools_menu_keyboard
from main import States

logger = logging.getLogger(__name__)

async def weather_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.edit_message_text("Für welchen Ort möchtest du das Wetter wissen?")
    return States.WEATHER_LOCATION

async def weather_location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.text
    get_weather_info = context.bot_data.get('get_weather_info')
    if get_weather_info:
        message = await get_weather_info(location)
    else:
        message = "Wetterdienst nicht verfügbar."
    if "Fehler" in message:
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
    await update.callback_query.edit_message_text(
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
</create_file>
