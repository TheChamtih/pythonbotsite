import logging
from flask import current_app
from bot_instance import bot

logger = logging.getLogger(__name__)

def notify_admin_action(admin, action_type, details=None):
    """Отправляет уведомление в Telegram о действиях администратора"""
    try:
        if not bot:
            logger.warning("Telegram bot not initialized, skipping notification")
            return

        emoji_map = {
            'login': '🔐',
            'course_add': '📚',
            'course_edit': '✏️',
            'course_delete': '🗑️',
            'application_approve': '✅',
            'application_reject': '❌',
            'location_add': '📍',
            'location_edit': '📝',
            'location_delete': '🗑️',
            'district_add': '🏢',
            'district_edit': '✏️',
            'district_delete': '🗑️',
            'review_delete': '🗑️'
        }
        emoji = emoji_map.get(action_type, 'ℹ️')

        if details:
            message = f"{emoji} {action_type.replace('_', ' ').title()}\n{details}"
        else:
            message = f"{emoji} {action_type.replace('_', ' ').title()}"

        message += f"\nАдминистратор: {admin.username or admin.first_name}"
        bot.send_message(admin.telegram_id, message)
    except Exception as e:
        logger.error(f"Error sending Telegram notification: {str(e)}")

def notify_admin_login(admin):
    """Отправляет уведомление в Telegram при входе администратора"""
    try:
        if not bot:
            logger.warning("Telegram bot not initialized, skipping notification")
            return

        message = f"🔐 Выполнен вход в админ-панель\nАдминистратор: {admin.username or admin.first_name}"
        bot.send_message(admin.telegram_id, message)
    except Exception as e:
        logger.error(f"Error sending Telegram notification: {str(e)}")