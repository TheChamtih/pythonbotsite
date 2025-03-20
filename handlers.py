import logging
import json
from telegram.ext import (
    CallbackContext, ConversationHandler, CommandHandler,
    MessageHandler, Filters, CallbackQueryHandler
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from database import get_admin_ids, add_admin, get_locations, get_location_by_id, get_connection
from config import MAIN_ADMIN_ID
import os
import re
from datetime import datetime
import psycopg2
from psycopg2.extras import DictCursor
from typing import List, Dict, Optional, Union
import math
from decorators import admin_required
from constants import *

# Configure logger
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Dialog states
NAME, AGE, INTERESTS, PARENT_NAME, PHONE = range(5)
COURSE_SELECTION, LOCATION_SELECTION = range(5, 7)
CONFIRMATION = 7
COURSE_RATING_SELECTION, RATING_INPUT, COMMENT_INPUT = range(8, 11)

# Age limits
MIN_AGE = 6
MAX_AGE = 18

# Dialog text constants
DIALOG_START = "Привет! Давайте подберем курс для вашего ребенка. Как зовут вашего ребенка?"
DIALOG_GET_AGE = "Отлично, {name}! Сколько лет вашему ребенку?"
DIALOG_GET_INTERESTS = "Чем увлекается ваш ребенок? (например, программирование, дизайн, математика и т.д.)"
DIALOG_GET_PARENT_NAME = "Как вас зовут? (Имя родителя)"
DIALOG_GET_PHONE = "Укажите ваш номер телефона для связи (начинается на +7 или 8):"
ERROR_AGE_RANGE = "Возраст должен быть от {min_age} до {max_age} лет. Пожалуйста, введите корректный возраст."
ERROR_PHONE_FORMAT = "Номер телефона должен начинаться на +7 или 8. Пожалуйста, введите корректный номер."

def get_course_name(course_id: int) -> str:
    """Gets course name by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT name FROM courses WHERE id = %s', (course_id,))
        result = cursor.fetchone()
        return result[0] if result else "Неизвестный курс"
    finally:
        conn.close()

def is_valid_phone(phone: str) -> bool:
    """Phone number format validation"""
    return re.match(
        r'^(\+7|8)[\s\-]?(\d{3})[\s\-]?(\d{3})[\s\-]?(\d{2})[\s\-]?(\d{2})$',
        phone) is not None

def notify_admins(context: CallbackContext, message: str):
    """Send notification to all admins"""
    admins = get_admin_ids()
    for admin in admins:
        try:
            context.bot.send_message(chat_id=admin, text=message)
        except Exception as e:
            logger.error(f"Failed to send message to admin {admin}: {e}")

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in get_admin_ids() or user_id == MAIN_ADMIN_ID

@admin_required
def view_trials(update: Update, context: CallbackContext):
    """Shows all trial lesson registrations."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT 
                trial_lessons.id,
                users.child_name,
                users.parent_name,
                users.phone,
                courses.name as course_name,
                districts.name as district_name,
                locations.address,
                trial_lessons.date,
                trial_lessons.confirmed
            FROM trial_lessons
            JOIN users ON trial_lessons.user_id = users.id
            JOIN courses ON trial_lessons.course_id = courses.id
            JOIN locations ON trial_lessons.location_id = locations.id
            JOIN districts ON locations.district_id = districts.id
            ORDER BY trial_lessons.date DESC
        ''')
        trials = cursor.fetchall()
        if not trials:
            update.message.reply_text("На данный момент записей на пробные занятия нет.")
            return

        message = "📋 Записи на пробные занятия:\n\n"
        for trial in trials:
            trial_info = (
                f"🔖 ID записи: {trial[0]}\n"
                f"👶 Ребенок: {trial[1]}\n"
                f"👤 Родитель: {trial[2]}\n"
                f"📱 Телефон: {trial[3]}\n"
                f"📚 Курс: {trial[4]}\n"
                f"📍 Район: {trial[5]}\n"
                f"🏫 Адрес: {trial[6]}\n"
                f"📅 Дата записи: {trial[7].strftime('%d.%m.%Y %H:%M')}\n"
                f"✅ Статус: {'Подтверждено' if trial[8] else 'Не подтверждено'}\n"
                f"{'=' * 30}\n"
            )

            if len(message + trial_info) > 4096:
                update.message.reply_text(message)
                message = trial_info
            else:
                message += trial_info

        if message:
            update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error in view_trials: {e}")
        update.message.reply_text("Произошла ошибка при отображении записей.")
    finally:
        conn.close()

@admin_required
def filter_trials(update: Update, context: CallbackContext):
    """Shows unconfirmed trial lessons."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT 
                trial_lessons.id,
                users.child_name,
                users.parent_name,
                users.phone,
                courses.name as course_name,
                districts.name as district_name,
                locations.address,
                trial_lessons.date
            FROM trial_lessons
            JOIN users ON trial_lessons.user_id = users.id
            JOIN courses ON trial_lessons.course_id = courses.id
            JOIN locations ON trial_lessons.location_id = locations.id
            JOIN districts ON locations.district_id = districts.id
            WHERE trial_lessons.confirmed = FALSE
            ORDER BY trial_lessons.date DESC
        ''')
        trials = cursor.fetchall()
        if not trials:
            update.message.reply_text("Нет неподтвержденных записей на пробные занятия.")
            return

        message = "📋 Неподтвержденные записи:\n\n"
        for trial in trials:
            trial_info = (
                f"🔖 ID записи: {trial[0]}\n"
                f"👶 Ребенок: {trial[1]}\n"
                f"👤 Родитель: {trial[2]}\n"
                f"📱 Телефон: {trial[3]}\n"
                f"📚 Курс: {trial[4]}\n"
                f"📍 Район: {trial[5]}\n"
                f"🏫 Адрес: {trial[6]}\n"
                f"📅 Дата записи: {trial[7].strftime('%d.%m.%Y %H:%M')}\n"
                f"{'=' * 30}\n"
            )

            if len(message + trial_info) > 4096:
                update.message.reply_text(message)
                message = trial_info
            else:
                message += trial_info

        if message:
            update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error in filter_trials: {e}")
        update.message.reply_text("Произошла ошибка при отображении записей.")
    finally:
        conn.close()

@admin_required
def clear_trials(update: Update, context: CallbackContext):
    """Deletes all unconfirmed trial lessons."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM trial_lessons WHERE confirmed = FALSE')
        deleted_count = cursor.rowcount
        conn.commit()
        update.message.reply_text(f"Удалено {deleted_count} неподтвержденных записей.")
    except Exception as e:
        logger.error(f"Error in clear_trials: {e}")
        conn.rollback()
        update.message.reply_text("Произошла ошибка при удалении записей.")
    finally:
        conn.close()

@admin_required
def add_admin_command(update: Update, context: CallbackContext):
    """Adds new admin."""
    try:
        new_admin_id = int(context.args[0])
        add_admin(new_admin_id)
        update.message.reply_text(SUCCESS_ADMIN_ADDED.format(admin_id=new_admin_id))
    except (IndexError, ValueError):
        update.message.reply_text(ERROR_COMMAND_USAGE.format(command_usage="/add_admin <telegram_id>"))

@admin_required
def confirm_trial(update: Update, context: CallbackContext):
    """Confirms trial lesson and sends rating request to user."""
    try:
        trial_id = int(context.args[0])
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Получаем информацию о пробном уроке
            cursor.execute('''
                SELECT tl.user_id, tl.course_id, c.name as course_name, u.telegram_id
                FROM trial_lessons tl
                JOIN courses c ON tl.course_id = c.id
                JOIN users u ON tl.user_id = u.id
                WHERE tl.id = %s
            ''', (trial_id,))
            trial_info = cursor.fetchone()
            if not trial_info:
                update.message.reply_text(f"Запись #{trial_id} не найдена.")
                return

            # Проверяем, не оставлял ли уже пользователь отзыв для этого курса
            cursor.execute('''
                SELECT id FROM course_reviews 
                WHERE user_id = %s AND course_id = %s
            ''', (trial_info[0], trial_info[1]))
            existing_review = cursor.fetchone()

            if existing_review:
                # Если отзыв уже есть, просто подтверждаем урок
                cursor.execute('UPDATE trial_lessons SET confirmed = TRUE WHERE id = %s', (trial_id,))
                conn.commit()
                update.message.reply_text(f"Запись #{trial_id} подтверждена. Отзыв уже был оставлен ранее.")
                return

            # Подтверждаем пробный урок
            cursor.execute('UPDATE trial_lessons SET confirmed = TRUE WHERE id = %s', (trial_id,))
            conn.commit()

            # Отправляем сообщение администратору
            update.message.reply_text(f"Запись #{trial_id} подтверждена.")

            # Отправляем сообщение пользователю о подтверждении
            user_telegram_id = trial_info[3]
            course_name = trial_info[2]

            confirmation_message = (
                f"✅ Ваша запись на пробное занятие по курсу \"{course_name}\" подтверждена!\n\n"
                "Мы были бы благодарны, если бы вы оценили курс после занятия."
            )

            # Создаем клавиатуру для оценки
            keyboard = []
            row = []
            for i in range(10, 0, -1):
                rating = i / 2
                row.append(InlineKeyboardButton(
                    f"{'★' * int(rating)}{('½' if rating % 1 else '')}", 
                    callback_data=f"stars_{rating}_{trial_info[1]}"  # Добавляем course_id в callback_data
                ))
                if len(row) == 5:
                    keyboard.append(row)
                    row = []
            if row:
                keyboard.append(row)
            keyboard.append([InlineKeyboardButton("❌ Позже", callback_data="rate_later")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            try:
                # Отправляем сообщение пользователю
                context.bot.send_message(
                    chat_id=user_telegram_id,
                    text=confirmation_message,
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Error sending confirmation to user: {e}")
                update.message.reply_text("Запись подтверждена, но не удалось отправить уведомление пользователю.")

        except Exception as e:
            logger.error(f"Error confirming trial: {e}")
            update.message.reply_text("Произошла ошибка при подтверждении записи.")
            conn.rollback()
        finally:
            conn.close()

    except (IndexError, ValueError):
        update.message.reply_text("Использование: /confirm_trial <id_записи>")

@admin_required
def list_courses_admin(update: Update, context: CallbackContext):
    """Shows course list with IDs for admins."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT c.id, c.name, c.min_age, c.max_age, 
                   string_agg(ct.tag, ', ') as tags
            FROM courses c
            LEFT JOIN course_tags ct ON c.id = ct.course_id
            GROUP BY c.id, c.name, c.min_age, c.max_age
            ORDER BY c.id
        ''')
        courses = cursor.fetchall()
        if not courses:
            update.message.reply_text("Список курсов пуст.")
            return

        message = "📚 Список курсов:\n\n"
        for course in courses:
            course_info = (
                f"ID: {course[0]}\n"
                f"📖 Название: {course[1]}\n"
                f"🔢 Возраст: {course[2]}-{course[3]} лет\n"
                f"🏷 Теги: {course[4] or 'нет'}\n"
                f"{'=' * 30}\n"
            )

            if len(message + course_info) > 4096:
                update.message.reply_text(message)
                message = course_info
            else:
                message += course_info

        if message:
            update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error in list_courses_admin: {e}")
        update.message.reply_text("Произошла ошибка при получении списка курсов.")
    finally:
        conn.close()

@admin_required
def add_tags_command(update: Update, context: CallbackContext):
    """Adds tags to course."""
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Использование: /add_tags <id_курса> <тег1> <тег2> ...")
        return

    try:
        course_id = int(args[0])
        tags = args[1:]

        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Check course exists
            cursor.execute('SELECT id FROM courses WHERE id = %s', (course_id,))
            if not cursor.fetchone():
                update.message.reply_text(f"Курс с ID {course_id} не найден.")
                return

            # Add tags
            for tag in tags:
                cursor.execute(
                    'INSERT INTO course_tags (course_id, tag) VALUES (%s, %s) ON CONFLICT DO NOTHING',
                    (course_id, tag.lower())
                )

            conn.commit()
            update.message.reply_text(f"Теги успешно добавлены к курсу #{course_id}")
        except Exception as e:
            logger.error(f"Error adding tags: {e}")
            conn.rollback()
            update.message.reply_text("Произошла ошибка при добавлении тегов.")
        finally:
            conn.close()

    except ValueError:
        update.message.reply_text("ID курса должен быть числом.")

@admin_required
def delete_tags_command(update: Update, context: CallbackContext):
    """Deletes course tags."""
    args = context.args
    if len(args) < 2:
        update.message.reply_text("Использование: /delete_tags <id_курса> <тег1> <тег2> ...")
        return

    try:
        course_id = int(args[0])
        tags = args[1:]

        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Check course exists
            cursor.execute('SELECT id FROM courses WHERE id = %s', (course_id,))
            if not cursor.fetchone():
                update.message.reply_text(f"Курс с ID {course_id} не найден.")
                return

            # Delete tags
            for tag in tags:
                cursor.execute(
                    'DELETE FROM course_tags WHERE course_id = %s AND tag = %s',
                    (course_id, tag.lower())
                )

            conn.commit()
            update.message.reply_text(f"Теги успешно удалены у курса #{course_id}")
        except Exception as e:
            logger.error(f"Error deleting tags: {e}")
            conn.rollback()
            update.message.reply_text("Произошла ошибка при удалении тегов.")
        finally:
            conn.close()

    except ValueError:
        update.message.reply_text("ID курса должен быть числом.")

def list_courses(update: Update, context: CallbackContext):
    """Shows list of all courses for users."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT name, description, min_age, max_age
            FROM courses
            ORDER BY name
        ''')
        courses = cursor.fetchall()
        if not courses:
            update.message.reply_text("На данный момент нет доступных курсов.")
            return

        message = "📚 Наши курсы:\n\n"
        for course in courses:
            course_info = (
                f"• {course[0]}\n"
                f"  {course[1]}\n"
                f"  Возраст: {course[2]}-{course[3]} лет\n\n"
            )

            if len(message + course_info) > 4096:
                update.message.reply_text(message)
                message = course_info
            else:
                message += course_info

        if message:
            update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error in list_courses: {e}")
        update.message.reply_text("Произошла ошибка при получении списка курсов.")
    finally:
        conn.close()

def handle_clear_trials(update: Update, context: CallbackContext):
    """Handles callback for clearing trial lessons."""
    query = update.callback_query
    query.answer()

    if not is_admin(query.from_user.id):
        query.edit_message_text("У вас нет прав для выполнения этой команды.")
        return

    if query.data.startswith("clear_trials_confirm"):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM trial_lessons WHERE confirmed = FALSE')
            deleted_count = cursor.rowcount
            conn.commit()
            query.edit_message_text(f"Удалено {deleted_count} неподтвержденных записей.")
        except Exception as e:
            logger.error(f"Error clearing trials: {e}")
            query.edit_message_text("Произошла ошибка при очистке записей.")
            conn.rollback()
        finally:
            conn.close()
    else:
        keyboard = [[
            InlineKeyboardButton("Да", callback_data="clear_trials_confirm"),
            InlineKeyboardButton("Нет", callback_data="clear_trials_cancel")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            "Вы уверены, что хотите удалить все неподтвержденные записи?",
            reply_markup=reply_markup
        )

@admin_required
def get_stats(update: Update, context: CallbackContext):
    """Shows detailed statistics about platform usage and user activity."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)

    try:
        # Общая статистика
        cursor.execute("SELECT COUNT(*) as total FROM users")
        result = cursor.fetchone()
        total_users = result['total'] if result else 0

        # Активные сегодня
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as active_today
            FROM user_activities
            WHERE timestamp >= CURRENT_DATE
        """)
        result = cursor.fetchone()
        active_today = result['active_today'] if result else 0

        # Статистика по платформам
        cursor.execute("""
            SELECT 
                COALESCE(details->>'platform', 'web') as platform,
                COUNT(*) as count
            FROM user_activities
            GROUP BY platform
        """)
        platform_stats = cursor.fetchall()

        # Активность за последние 7 дней
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as count
            FROM user_activities
            WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY date
            ORDER BY date DESC
        """)
        daily_activity = cursor.fetchall()

        # Последние действия
        cursor.execute("""
            SELECT 
                u.username,
                ua.activity_type,
                ua.timestamp
            FROM user_activities ua
            JOIN users u ON ua.user_id = u.id
            ORDER BY ua.timestamp DESC
            LIMIT 5
        """)
        recent_activities = cursor.fetchall()

        # Форматируем сообщение для Telegram
        message = (
            "📊 Статистика платформы\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"✨ Активных сегодня: {active_today}\n\n"
            "📱 По платформам:\n"
        )

        for stat in platform_stats:
            platform_name = "🌐 Веб" if stat['platform'] == 'web' else "📱 Telegram"
            message += f"{platform_name}: {stat['count']}\n"

        message += "\n📈 Активность за 7 дней:\n"
        for activity in daily_activity:
            date_str = activity['date'].strftime('%d.%m')
            count = activity['count']
            message += f"{date_str}: {'📊' * min(count, 5)} ({count})\n"

        message += "\n🔄 Последние действия:\n"
        for activity in recent_activities:
            username = activity['username'] or 'Пользователь'
            timestamp = activity['timestamp'].strftime('%H:%M')
            message += f"• {username} - {activity['activity_type']} ({timestamp})\n"

        update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        update.message.reply_text("Произошла ошибка при получении статистики.")
    finally:
        conn.close()

def help_command(update: Update, context: CallbackContext):
    """Shows available commands."""
    user_id = update.message.from_user.id
    logger.info(f"Help command executed by user {user_id}")

    help_text = USER_COMMANDS

    if is_admin(user_id):
        domain = os.environ.get('REPLIT_DEV_DOMAIN', 'codecreate.tech')
        admin_url = f"https://{domain}/admin"
        help_text += ADMIN_COMMANDS.format(admin_url=admin_url)

    update.message.reply_text(help_text)

def about_command(update: Update, context: CallbackContext):
    """School information."""
    update.message.reply_text(
        """
        🏫 Алгоритмика — международная школа программирования и математики для детей 7-17 лет.

        Мы помогаем детям освоить навыки будущего:
        - Программирование на Python, JavaScript и других языках.
        - Разработка игр и приложений.
        - Основы математики и логики.
        - Создание веб-сайтов и мобильных приложений.
        - Изучение искусственного интеллекта и анализа данных.

        📞 Контактные данные:
        - Телефон: +7 (800) 555-35-35
        - Email: info@algoritmika.org
        - Веб-сайт: algoritmika.org (https://algoritmika.org/)
        - Адрес: Москва, ул. Ленина, д. 42 (главный офис)

        📍 Мы работаем в более чем 20 странах мира!

        Присоединяйтесь к нам и откройте для вашего ребёнка мир программирования и математики!
        Чтобы записаться на пробное занятие, используйте команду /start
        """
    )

def list_locations_command(update: Update, context: CallbackContext):
    """Shows all locations."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT d.name as district_name, l.address 
            FROM locations l
            JOIN districts d ON l.district_id = d.id
            ORDER BY d.name, l.address
        ''')
        locations = cursor.fetchall()
        if not locations:
            update.message.reply_text("К сожалению, сейчас нет доступных адресов.")
            return

        message = "📍 Наши адреса:\n\n"
        current_district = None

        for location in locations:
            district_name, address = location
            if current_district != district_name:
                current_district = district_name  
                message += f"\n🏢 {district_name}:\n"
            message += f"• {address}\n"

        update.message.reply_text(message)
    except Exception as e:
        logger.error(f"Error in list_locations_command: {e}")
        update.message.reply_text("Произошла ошибка при получении списка адресов.")
    finally:
        conn.close()

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels conversation."""
    update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(DIALOG_START)
    return NAME

def get_name(update: Update, context: CallbackContext) -> int:
    """Handles the name input."""
    user_name = update.message.text
    context.user_data['child_name'] = user_name
    update.message.reply_text(DIALOG_GET_AGE.format(name=user_name))
    return AGE

def get_age(update: Update, context: CallbackContext) -> int:
    """Handles the age input."""
    try:
        user_age = int(update.message.text)
        if not MIN_AGE <= user_age <= MAX_AGE:
            update.message.reply_text(ERROR_AGE_RANGE.format(min_age=MIN_AGE, max_age=MAX_AGE))
            return AGE
    except ValueError:
        update.message.reply_text("Пожалуйста, введите число.")
        return AGE

    context.user_data['child_age'] = user_age
    update.message.reply_text(DIALOG_GET_INTERESTS)
    return INTERESTS

def get_interests(update: Update, context: CallbackContext) -> int:
    """Handles the interests input."""
    interests = update.message.text
    context.user_data['child_interests'] = interests
    update.message.reply_text(DIALOG_GET_PARENT_NAME)
    return PARENT_NAME

def get_parent_name(update: Update, context: CallbackContext) -> int:
    """Handles the parent name input."""
    parent_name = update.message.text
    context.user_data['parent_name'] = parent_name
    update.message.reply_text(DIALOG_GET_PHONE)
    return PHONE

def get_phone(update: Update, context: CallbackContext) -> int:
    """Handles the phone number input."""
    phone = update.message.text
    if not is_valid_phone(phone):
        update.message.reply_text(ERROR_PHONE_FORMAT)
        return PHONE

    context.user_data['phone'] = phone

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get user's profile photos
        telegram_user = update.effective_user
        profile_photos = context.bot.get_user_profile_photos(telegram_user.id, limit=1)
        telegram_avatar_url = None

        if profile_photos and profile_photos.photos:
            # Get the file_id of the most recent profile photo
            file_id = profile_photos.photos[0][-1].file_id
            # Get file path
            file = context.bot.get_file(file_id)
            telegram_avatar_url = file.file_path

        # Check if user exists
        cursor.execute('''
            SELECT id FROM users 
            WHERE telegram_id = %s
        ''', (update.effective_user.id,))

        user = cursor.fetchone()

        if user:
            # Update existing user
            cursor.execute('''
                UPDATE users 
                SET parent_name = %s, 
                    phone = %s, 
                    child_name = %s, 
                    child_age = %s,
                    child_interests = %s,
                    telegram_avatar_url = %s,
                    username = %s,
                    first_name = %s,
                    last_name = %s
                WHERE telegram_id = %s
                RETURNING id
            ''', (
                context.user_data['parent_name'],
                context.user_data['phone'],
                context.user_data['child_name'],
                context.user_data['child_age'],
                context.user_data.get('child_interests', ''),
                telegram_avatar_url,
                update.effective_user.username,
                update.effective_user.first_name,
                update.effective_user.last_name,
                update.effective_user.id
            ))
            user_id = cursor.fetchone()[0]
        else:
            # Create new user
            cursor.execute('''
                INSERT INTO users (
                    telegram_id, 
                    parent_name, 
                    phone, 
                    child_name, 
                    child_age,
                    child_interests,
                    telegram_avatar_url,
                    username,
                    first_name,
                    last_name
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                update.effective_user.id,
                context.user_data['parent_name'],
                context.user_data['phone'],
                context.user_data['child_name'],
                context.user_data['child_age'],
                context.user_data.get('child_interests', ''),
                telegram_avatar_url,
                update.effective_user.username,
                update.effective_user.first_name,
                update.effective_user.last_name
            ))
            user_id = cursor.fetchone()[0]

        conn.commit()

        # Get suitable courses
        cursor.execute('''
            SELECT c.id, c.name, c.description, c.min_age, c.max_age
            FROM courses c
            WHERE c.min_age <= %s AND c.max_age >= %s
        ''', (context.user_data['child_age'], context.user_data['child_age']))

        courses = cursor.fetchall()

        if not courses:
            update.message.reply_text("К сожалению, для указанного возраста нет подходящих курсов.")
            return ConversationHandler.END

        keyboard = []
        for course in courses:
            keyboard.append([InlineKeyboardButton(course[1], callback_data=f"course_{course[0]}")])
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="exit")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Выберите интересующий курс:", reply_markup=reply_markup)

        context.user_data['user_id'] = user_id
        return COURSE_SELECTION

    except Exception as e:
        logger.error(f"Error in get_phone: {e}")
        conn.rollback()
        update.message.reply_text("Произошла ошибка при сохранении данных. Пожалуйста, попробуйте позже.")
        return ConversationHandler.END
    finally:
        conn.close()

def select_course(update: Update, context: CallbackContext) -> int:
    """Handles course selection."""
    query = update.callback_query
    query.answer()

    if query.data == "exit":
        query.edit_message_text("Диалог завершен. Если хотите начать заново, напишите /start")
        return ConversationHandler.END

    course_id = int(query.data.split("_")[1])
    context.user_data['course_id'] = course_id
    logger.info(f"User {update.effective_user.id} selected course {course_id}")

    # Get course details
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Get course name
        cursor.execute('SELECT name FROM courses WHERE id = %s', (course_id,))
        course = cursor.fetchone()
        if not course:
            logger.error(f"Course {course_id} not found in database")
            query.edit_message_text("Извините, выбранный курс не найден. Попробуйте начать сначала с /start")
            return ConversationHandler.END

        logger.info(f"Found course: {course[0]}")

        # Get locations
        cursor.execute('''
            SELECT d.name as district_name, l.address, l.id
            FROM locations l
            JOIN districts d ON l.district_id = d.id
            ORDER BY d.name, l.address
        ''')
        locations = cursor.fetchall()
        logger.info(f"Found {len(locations)} available locations")

        if not locations:
            logger.warning("No locations available in the database")
            query.edit_message_text("К сожалению, сейчас нет доступных локаций для записи.")
            return ConversationHandler.END

        # Create keyboard with locations
        keyboard = []
        for location in locations:
            district_name = location[0]
            address = location[1]
            location_id = location[2]
            keyboard.append([
                InlineKeyboardButton(
                    f"{district_name} - {address}",
                    callback_data=f"location_{location_id}"
                )
            ])
            logger.debug(f"Added location option: {district_name} - {address} (ID: {location_id})")

        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="exit")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = (
            f"Вы выбрали курс: {course[0]}\n\n"
            "Теперь выберите удобную локацию:"
        )
        query.edit_message_text(message, reply_markup=reply_markup)
        logger.info(f"Showing location selection menu for course {course[0]}")

        return LOCATION_SELECTION

    except Exception as e:
        logger.error(f"Error in select_course: {str(e)}", exc_info=True)
        query.edit_message_text("Произошла ошибка. Пожалуйста, попробуйте позже.")
        return ConversationHandler.END
    finally:
        conn.close()

def select_location(update: Update, context: CallbackContext) -> int:
    """Handles location selection."""
    query = update.callback_query
    query.answer()

    if query.data == "exit":
        query.edit_message_text("Диалог завершен.")
        return ConversationHandler.END

    if query.data.startswith("location_"):
        location_id = int(query.data.split("_")[1])
        context.user_data['location_id'] = location_id

        keyboard = [
            [
                InlineKeyboardButton("✅ Да", callback_data="confirm_yes"),
                InlineKeyboardButton("❌ Нет", callback_data="confirm_no")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        location = get_location_by_id(location_id)
        course_name = get_course_name(context.user_data['course_id'])

        confirmation_text = (
            f"Подтвердите запись на пробное занятие:\n\n"
            f"Курс: {course_name}\n"
            f"Район: {location[0]}\n"
            f"Адрес: {location[1]}\n"
            f"\nВсё верно?"
        )

        query.edit_message_text(text=confirmation_text, reply_markup=reply_markup)
        return CONFIRMATION

    return ConversationHandler.END

def get_location_by_id(location_id: int) -> tuple:
    """Gets location info by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT d.name, l.address
            FROM locations l
            JOIN districts d ON l.district_id = d.id
            WHERE l.id = %s
        ''', (location_id,))
        result = cursor.fetchone()
        return result if result else ("Неизвестный район", "Адрес не найден")
    except Exception as e:
        logger.error(f"Error in get_location_by_id: {e}")
        return ("Неизвестный район", "Адрес не найден")
    finally:
        conn.close()

def confirm_choice(update: Update, context: CallbackContext) -> int:
    """Handles confirmation of trial lesson choice."""
    query = update.callback_query
    query.answer()

    if query.data == "confirm_no":
        query.edit_message_text("Хорошо, давайте выберем другой вариант.")
        return COURSE_SELECTION

    if query.data == "confirm_yes":
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Создаем запись о пробном занятии
            cursor.execute('''
                INSERT INTO trial_lessons (
                    user_id, course_id, location_id, date, confirmed
                ) VALUES (
                    %s, %s, %s, NOW(), FALSE
                ) RETURNING id
            ''', (
                context.user_data['user_id'],
                context.user_data['course_id'],
                context.user_data['location_id']
            ))

            trial_id = cursor.fetchone()
            if not trial_id:
                raise Exception("Failed to create trial lesson")

            conn.commit()

            # Получаем информацию о записи
            location = get_location_by_id(context.user_data['location_id'])
            course_name = get_course_name(context.user_data['course_id'])

            # Отправляем сообщение пользователю
            success_message = (
                f"✅ Запись на пробное занятие создана!\n\n"
                f"📚 Курс: {course_name}\n"
                f"📍 Район: {location[0]}\n"
                f"🏫 Адрес: {location[1]}\n\n"
                "Мы свяжемся с вами для подтверждения времени занятия."
            )
            query.edit_message_text(success_message)

            # Уведомляем администраторов
            admin_message = (
                f"🆕 Новая запись на пробное занятие!\n"
                f"ID записи: {trial_id[0]}\n"
                f"Курс: {course_name}"
            )
            notify_admins(context, admin_message)

            return ConversationHandler.END

        except Exception as e:
            logger.error(f"Error in confirm_choice: {e}")
            if conn:
                conn.rollback()
            query.edit_message_text(
                "Произошла ошибка при создании записи. "
                "Пожалуйста, попробуйте позже или свяжитесь с администратором."
            )
            return ConversationHandler.END
        finally:
            if conn:
                conn.close()

    return ConversationHandler.END

# Get the main conversation handler
def get_conversation_handler():
    """Main conversation handler for course selection and trial lesson signup flow"""
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            AGE: [MessageHandler(Filters.text & ~Filters.command, get_age)],
            INTERESTS: [MessageHandler(Filters.text & ~Filters.command, get_interests)],
            PARENT_NAME: [MessageHandler(Filters.text & ~Filters.command, get_parent_name)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, get_phone)],
            COURSE_SELECTION: [
                CallbackQueryHandler(select_course, pattern='^course_|^exit$')
            ],
            LOCATION_SELECTION: [                CallbackQueryHandler(select_location, pattern='^location_|^exit$')
            ],
            CONFIRMATION: [
                CallbackQueryHandler(confirm_choice, pattern='^confirm_yes$|^confirm_no$|^exit$')
            ],
            COMMENT_INPUT: [
                MessageHandler(Filters.text & ~Filters.command, handle_comment),
                CommandHandler('skip', handle_comment)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

def get_confirm_trial_handler():
    """Returns handler for trial lesson confirmation command."""
    return CommandHandler('confirm_trial', confirm_trial)


# Added functions for course rating
def rate_course_command(update: Update, context: CallbackContext) -> int:
    """Starts the course rating dialog."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT id, name FROM courses ORDER BY name')
        courses = cursor.fetchall()
        if not courses:
            update.message.reply_text("К сожалению, сейчас нет доступных курсов для оценки.")
            return ConversationHandler.END

        keyboard = []
        for course in courses:
            keyboard.append([InlineKeyboardButton(course[1], callback_data=f"rate_{course[0]}")])
        keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="cancel")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "Выберите курс для оценки:",
            reply_markup=reply_markup
        )
        return COURSE_RATING_SELECTION
    except Exception as e:
        logger.error(f"Error in rate_course_command: {e}")
        update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")
        return ConversationHandler.END
    finally:
        conn.close()

def select_course_to_rate(update: Update, context: CallbackContext) -> int:
    """Handles course selection for rating."""
    query = update.callback_query
    query.answer()

    if query.data == "cancel":
        query.edit_message_text("Оценка курса отменена.")
        return ConversationHandler.END

    course_id = int(query.data.split("_")[1])
    context.user_data['rating_course_id'] = course_id

    # Создаем клавиатуру для оценок с шагом 0.5
    keyboard = []
    row = []
    for i in range(10, 0, -1):
        rating = i / 2
        row.append(InlineKeyboardButton(f"{'★' * int(rating)}{('½' if rating % 1 else '')}", 
                                      callback_data=f"stars_{rating}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="cancel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        "Оцените курс от 0.5 до 5 звёзд:",
        reply_markup=reply_markup
    )
    return RATING_INPUT

def handle_rating_input(update: Update, context: CallbackContext) -> int:
    """Handles the rating selection."""
    query = update.callback_query
    query.answer()

    if query.data == "cancel":
        query.edit_message_text("Оценка курса отменена.")
        return ConversationHandler.END

    rating = float(query.data.split("_")[1])
    context.user_data['rating_value'] = rating

    query.edit_message_text(
        f"Вы поставили {rating} звёзд.\n"
        "Хотите добавить комментарий к вашей оценке? "
        "Напишите ваш комментарий или отправьте /skip чтобы пропустить."
    )
    return COMMENT_INPUT

def handle_rating_callback(update: Update, context: CallbackContext) -> int:
    """Handles rating selection."""
    query = update.callback_query
    query.answer()

    if query.data == "rate_later":
        query.edit_message_text("Хорошо, вы можете оценить курс позже.")
        return ConversationHandler.END

    # Extract rating and course_id from callback data
    try:
        # Format: stars_X.X_Y where X.X is rating and Y is course_id
        _, rating_str, course_id = query.data.split('_')
        rating = float(rating_str)
        course_id = int(course_id)
    except (ValueError, IndexError):
        logger.error(f"Invalid rating callback data: {query.data}")
        query.edit_message_text("Произошла ошибка. Пожалуйста, попробуйте позже.")
        return ConversationHandler.END

    # Store rating in context for later use
    context.user_data['rating'] = rating
    context.user_data['course_id'] = course_id

    # Create keyboard for comment options
    keyboard = [
        [InlineKeyboardButton("➡️ Пропустить", callback_data="skip_comment")],
        [InlineKeyboardButton("❌ Отменить", callback_data="rate_later")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        "Спасибо за оценку! Хотите добавить комментарий к вашему отзыву?\n"
        "Если да - просто напишите его.\n"
        "Если нет - нажмите «Пропустить».",
        reply_markup=reply_markup
    )

    return COMMENT_INPUT

def handle_comment(update: Update, context: CallbackContext) -> int:
    """Handles comment input for course review."""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Get user_id
        cursor.execute(
            'SELECT id FROM users WHERE telegram_id = %s',
            (update.effective_user.id,)
        )
        user_result = cursor.fetchone()
        if not user_result:
            logger.error(f"User not found for telegram_id: {update.effective_user.id}")
            if isinstance(update, CallbackQuery):
                update.edit_message_text("Произошла ошибка. Пожалуйста, попробуйте позже.")
            else:
                update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")
            return ConversationHandler.END

        user_id = user_result[0]
        rating = context.user_data.get('rating')
        course_id = context.user_data.get('course_id')

        if not rating or not course_id:
            logger.error("Missing rating or course_id in user_data")
            if isinstance(update, CallbackQuery):
                update.edit_message_text("Произошла ошибка. Пожалуйста, начните процесс оценки заново.")
            else:
                update.message.reply_text("Произошла ошибка. Пожалуйста, начните процесс оценки заново.")
            return ConversationHandler.END

        # Get comment text
        comment = None
        if isinstance(update, CallbackQuery):
            # Skip comment case
            update.answer()
        else:
            comment = update.message.text

        # Check if user already reviewed this course
        cursor.execute('''
            SELECT id FROM course_reviews 
            WHERE user_id = %s AND course_id = %s
        ''', (user_id, course_id))
        existing_review = cursor.fetchone()

        if existing_review:
            # Update existing review
            cursor.execute('''
                UPDATE course_reviews 
                SET rating = %s, comment = %s, updated_at = NOW(), source = 'telegram'
                WHERE user_id = %s AND course_id = %s
                RETURNING id
            ''', (rating, comment, user_id, course_id))
        else:
            # Create new review
            cursor.execute('''
                INSERT INTO course_reviews (user_id, course_id, rating, comment, source)
                VALUES (%s, %s, %s, %s, 'telegram')
                RETURNING id
            ''', (user_id, course_id, rating, comment))

        review_id = cursor.fetchone()[0]

        # Log activity
        activity_details = {
            'review_id': review_id,
            'course_id': course_id,
            'rating': rating,
            'action': 'update' if existing_review else 'create',
            'platform': 'telegram'
        }

        # Convert dict to JSON string using json.dumps()
        activity_details_json = json.dumps(activity_details)

        cursor.execute('''
            INSERT INTO user_activities (user_id, activity_type, details)
            VALUES (%s, %s, %s::JSON)
        ''', (
            user_id,
            'review_update' if existing_review else 'review_create',
            activity_details_json
        ))

        # Update course average rating
        cursor.execute('''
            UPDATE courses 
            SET rating = (
                SELECT AVG(rating)::NUMERIC(3,2)
                FROM course_reviews
                WHERE course_id = %s
            ),
            rating_count = (
                SELECT COUNT(*)
                FROM course_reviews
                WHERE course_id = %s
            )
            WHERE id = %s
        ''', (course_id, course_id, course_id))

        conn.commit()

        # Send confirmation message
        thank_you_text = "Спасибо за ваш отзыв! 🌟"
        if isinstance(update, CallbackQuery):
            update.edit_message_text(thank_you_text)
        else:
            update.message.reply_text(thank_you_text)

    except Exception as e:
        logger.error(f"Error saving review: {e}")
        conn.rollback()
        error_message = "Произошла ошибка при сохранении отзыва. Пожалуйста, попробуйте позже."
        if isinstance(update, CallbackQuery):
            update.edit_message_text(error_message)
        else:
            update.message.reply_text(error_message)
    finally:
        conn.close()

    return ConversationHandler.END

def get_rating_conversation_handler():
    """Returns the conversation handler for course rating."""
    return ConversationHandler(
        entry_points=[CommandHandler('rate_course', rate_course_command)],
        states={
            COURSE_RATING_SELECTION: [
                CallbackQueryHandler(select_course_to_rate, pattern='^rate_|^cancel$')
            ],
            RATING_INPUT: [
                CallbackQueryHandler(handle_rating_input, pattern='^stars_|^cancel$')
            ],
            COMMENT_INPUT: [
                MessageHandler(Filters.text & ~Filters.command, handle_comment),
                CommandHandler('skip', handle_comment)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

def handle_star_rating(update: Update, context: CallbackContext) -> None:
    """Handles star rating callback."""
    query = update.callback_query
    query.answer()

    data = query.data.split('_')
    if len(data) < 3:
        return

    rating = float(data[1])
    course_id = int(data[2])

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Получаем информацию о пользователе
        cursor.execute('SELECT id FROM users WHERE telegram_id = %s', (update.effective_user.id,))
        user = cursor.fetchone()

        if not user:
            query.edit_message_text("Сначала нужно зарегистрироваться. Используйте команду /start")
            return

        # Проверяем, не оставлял ли уже пользователь отзыв
        cursor.execute('''
            SELECT id FROM course_reviews 
            WHERE user_id = %s AND course_id = %s
        ''', (user[0], course_id))

        if cursor.fetchone():
            query.edit_message_text("Вы уже оставляли отзыв для этого курса.")
            return

        # Добавляем отзыв
        cursor.execute('''
            INSERT INTO course_reviews (course_id, user_id, rating, source)
            VALUES (%s, %s, %s, 'telegram')
            RETURNING id
        ''', (course_id, user[0], rating))
        review_id = cursor.fetchone()[0]

        # Обновляем рейтинг курса
        cursor.execute('''
            SELECT rating, rating_count
            FROM courses
            WHERE id = %s
        ''', (course_id,))
        course_data = cursor.fetchone()
        current_rating = course_data[0] or 0
        rating_count = course_data[1] or 0

        # Вычисляем новый средний рейтинг
        new_rating = ((current_rating * rating_count) + rating) / (rating_count + 1)

        cursor.execute('''
            UPDATE courses
            SET rating = %s, rating_count = rating_count + 1
            WHERE id = %s
        ''', (new_rating, course_id))

        conn.commit()

        # Спрашиваем, хочет ли пользователь добавить комментарий
        keyboard = [[
            InlineKeyboardButton("Да", callback_data=f"add_comment_{review_id}"),
            InlineKeyboardButton("Нет", callback_data="no_comment")
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        query.edit_message_text(
            "Спасибо за оценку! Хотите добавить комментарий к вашему отзыву?",
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error handling star rating: {e}")
        query.edit_message_text("Произошла ошибка при сохранении оценки. Пожалуйста, попробуйте позже.")
        conn.rollback()
    finally:
        conn.close()