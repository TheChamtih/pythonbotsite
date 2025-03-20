import os
import logging
import time
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from telegram.error import NetworkError, Unauthorized, BadRequest
from handlers import (
    start,
    add_admin_command,
    list_courses,
    view_trials,
    help_command,
    about_command,
    filter_trials,
    cancel,
    clear_trials,
    handle_clear_trials,
    list_locations_command,
    confirm_trial,
    get_confirm_trial_handler,
    list_courses_admin,
    get_stats,
    add_tags_command,
    delete_tags_command,
    get_conversation_handler,
    handle_rating_callback,
    handle_comment,
    COMMENT_INPUT
)
from database import init_db
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_bot(max_retries=5, retry_delay=5):
    """Запускает бота с механизмом повторных попыток при ошибках подключения"""
    retry_count = 0
    last_error_time = 0
    error_count = 0

    while retry_count < max_retries:
        try:
            logger.info("Starting bot initialization...")
            logger.info(f"Bot token starts with: {BOT_TOKEN[:4]}...")

            # Инициализация базы данных
            init_db()
            logger.info("Database initialized successfully")

            # Создание бота
            updater = Updater(BOT_TOKEN, use_context=True)
            dispatcher = updater.dispatcher

            # Добавление основного обработчика диалога
            conversation_handler = get_conversation_handler()
            dispatcher.add_handler(conversation_handler)

            # Команды для всех пользователей
            basic_commands = [
                ('start', start),
                ('courses', list_courses),
                ('help', help_command),
                ('about', about_command),
                ('cancel', cancel),
                ('list_locations', list_locations_command)
            ]

            # Команды для администраторов
            admin_commands = [
                ('add_admin', add_admin_command),
                ('view_trials', view_trials),
                ('filter_trials', filter_trials),
                ('clear_trials', clear_trials),
                ('confirm_trial', confirm_trial),
                ('list_courses_admin', list_courses_admin),
                ('stats', get_stats),
                ('add_tags', add_tags_command),
                ('delete_tags', delete_tags_command)
            ]

            # Регистрация всех команд
            for command, handler in basic_commands + admin_commands:
                dispatcher.add_handler(CommandHandler(command, handler))

            # Add conversation handlers
            confirm_trial_handler = get_confirm_trial_handler()
            dispatcher.add_handler(confirm_trial_handler)

            # Add rating callback handlers
            rating_handler = ConversationHandler(
                entry_points=[
                    CallbackQueryHandler(handle_rating_callback, pattern=r"^stars_\d+(\.\d+)?_\d+$"),
                ],
                states={
                    COMMENT_INPUT: [
                        MessageHandler(
                            Filters.text & ~Filters.command,
                            handle_comment
                        ),
                        CallbackQueryHandler(handle_comment, pattern="^skip_comment$")
                    ],
                },
                fallbacks=[
                    CallbackQueryHandler(handle_rating_callback, pattern="^rate_later$"),
                    CommandHandler("cancel", cancel)
                ]
            )
            dispatcher.add_handler(rating_handler)

            # Add general callback handlers
            dispatcher.add_handler(CallbackQueryHandler(handle_clear_trials, pattern="^clear_trials_"))

            logger.info("All handlers registered successfully")

            # Error handler
            def error_callback(update, context):
                nonlocal error_count, last_error_time
                current_time = time.time()

                # Сброс счетчика ошибок, если прошло достаточно времени
                if current_time - last_error_time > 300:  # 5 минут
                    error_count = 0

                error_count += 1
                last_error_time = current_time

                try:
                    raise context.error
                except Unauthorized:
                    logger.error("Unauthorized - Invalid bot token")
                except BadRequest as e:
                    logger.error(f"Bad Request: {e}")
                except NetworkError as e:
                    logger.error(f"Network Error: {e}")
                    if "terminated by other getUpdates request" in str(e):
                        logger.error("Detected multiple bot instances, waiting before retry")
                        time.sleep(60)  # Ждем минуту перед следующей попыткой
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")

                # Если слишком много ошибок за короткий период, увеличиваем задержку
                if error_count > 10:
                    logger.warning("Too many errors, increasing retry delay")
                    time.sleep(300)  # 5 минут
                    error_count = 0

            dispatcher.add_error_handler(error_callback)

            # Запуск бота
            logger.info("Starting bot polling...")
            updater.start_polling(drop_pending_updates=True)
            updater.idle()
            return  # Успешный запуск, выходим из функции

        except NetworkError as e:
            retry_count += 1
            logger.error(f"Network error on attempt {retry_count}/{max_retries}: {e}")
            if retry_count < max_retries:
                wait_time = retry_delay * (2 ** (retry_count - 1))  # Экспоненциальная задержка
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logger.error("Max retries reached. Bot initialization failed.")
                raise
        except Exception as e:
            logger.error(f"Critical error starting bot: {str(e)}", exc_info=True)
            raise

if __name__ == '__main__':
    start_bot()