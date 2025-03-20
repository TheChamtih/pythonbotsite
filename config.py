import os

# Токен вашего бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

# ID главного администратора (ваш ID)
MAIN_ADMIN_ID = 963048430  # Не меняем, так как это ID реального администратора

# Bot username
BOT_USERNAME = "algotestmebot"

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL")

# Webhook settings for bot
WEBHOOK_HOST = f"https://{os.environ.get('REPLIT_DEV_DOMAIN', 'codecreate.tech:5000')}"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Flask app settings
FLASK_DEBUG = True
SECRET_KEY = os.environ.get("SESSION_SECRET", "your-secret-key-here")