import logging
from functools import wraps
from database import get_admin_ids
from constants import ERROR_NO_ADMIN_RIGHTS
from flask import request
from flask_login import current_user
from extensions import db
from models import UserActivity, User

logger = logging.getLogger(__name__)

def admin_required(func):
    """
    Декоратор для проверки прав администратора.
    Использование:
    @admin_required
    def admin_command(update, context):
        # код команды
    """
    @wraps(func)
    def wrapper(update, context, *args, **kwargs):
        user_id = update.effective_user.id

        if not user_id:
            logger.warning("User ID not found in update")
            return

        if user_id not in get_admin_ids():
            logger.warning(f"Unauthorized access attempt by user {user_id}")
            update.message.reply_text(ERROR_NO_ADMIN_RIGHTS)
            return

        return func(update, context, *args, **kwargs)

    return wrapper

def track_user_activity(activity_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                try:
                    # Проверяем существование пользователя
                    user = User.query.get(current_user.id)
                    if not user:
                        logger.warning(f"Attempt to track activity for non-existent user ID: {current_user.id}")
                        return f(*args, **kwargs)

                    # Собираем информацию о действии
                    details = {
                        'platform': 'web',
                        'url': request.url,
                        'method': request.method,
                        'user_agent': request.user_agent.string
                    }

                    # Создаем запись об активности
                    activity = UserActivity(
                        user_id=current_user.id,
                        activity_type=activity_type,
                        details=details
                    )

                    db.session.add(activity)
                    db.session.commit()
                    logger.debug(f"Activity tracked for user {current_user.id}: {activity_type}")

                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error tracking user activity: {str(e)}")
                    logger.debug(f"Current user ID: {current_user.id}, Activity type: {activity_type}")

            return f(*args, **kwargs)
        return decorated_function
    return decorator