import os
import telebot
import logging

logger = logging.getLogger(__name__)

# Get bot token from environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Initialize bot
try:
    bot = telebot.TeleBot(BOT_TOKEN)
except Exception as e:
    logger.error(f"Failed to initialize Telegram bot: {str(e)}")
    bot = None
