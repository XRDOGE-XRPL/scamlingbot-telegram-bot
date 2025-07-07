import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Update, Message, CallbackQuery, User
import asyncio

# Since the bot uses python-telegram-bot, we will mock Update and Context

@pytest.mark.asyncio
async def test_start_command(monkeypatch):
    from main import start_command
    update = MagicMock()
    context = MagicMock()
    update.effective_user.id = 123
    update.effective_user.first_name = "TestUser"
    update.message.reply_text = AsyncMock()
    context.user_data = {}

    await start_command(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
async def test_help_command(monkeypatch):
    from main import help_command
    update = MagicMock()
    context = MagicMock()
    update.message.reply_text = AsyncMock()
    update.callback_query = None

    await help_command(update, context)
    update.message.reply_text.assert_called()

# Add more tests for other handlers similarly

# This is a starting point for the test suite.
