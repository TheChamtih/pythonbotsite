import os
import hmac
import hashlib
import time
import logging
import traceback
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import BOT_TOKEN, BOT_USERNAME, MAIN_ADMIN_ID
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from functools import wraps
from decorators import track_user_activity
from extensions import db
from models import Admin, Course, Location, TrialLesson, User, CourseReview, CourseTag, District, UserActivity, SiteSettings, News, NewsImage, NewsComment, NewsTag, NewsCategory
from notifications import notify_admin_action, notify_admin_login
from forms import LoginForm, CourseForm, LocationForm, DistrictForm, AdminForm, NewsForm, NewsCommentForm, NewsCategoryForm
from bot_instance import bot
from settings_site import update_site_settings, get_site_settings
from utils.avatar import save_avatar
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from PIL import Image
from utils.bbcode_formatter import parse_bbcode

# Настройка расширенного логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация Flask приложения
app = Flask(__name__)

# Получаем DATABASE_URL и модифицируем его для SSL
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # Parse the URL to add SSL mode if not present
    parsed = urlparse(database_url)
    if 'sslmode' not in parsed.query:
        if '?' in database_url:
            database_url += '&sslmode=require'
        else:
            database_url += '?sslmode=require'
    logger.info("Database URL configured with SSL mode")
else:
    logger.error("DATABASE_URL environment variable is not set")
    raise ValueError("DATABASE_URL environment variable is required")

# Базовая конфигурация
app.config['SECRET_KEY'] = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "connect_args": {
        "sslmode": "require",
        "connect_timeout": 30,
    }
}
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize database
db.init_app(app)

# Декоратор для проверки прав администратора
def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        if not getattr(current_user, 'is_admin', False):
            flash('У вас нет доступа к этому разделу', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    """Главная страница"""
    # Get latest news for carousel, increased limit to show more pages
    latest_news = News.query.order_by(News.created_at.desc()).limit(9).all()
    # Get all courses
    courses = Course.query.all()
    return render_template('index.html', courses=courses, latest_news=latest_news)

@app.route('/debug')
def debug():
    """Simple debug endpoint."""
    return 'Debug OK', 200

@app.route('/test')
def test():
    """Simple test endpoint."""
    return 'Debug OK', 200

@app.route('/healthz')
def health_check():
    """Simple health check endpoint."""
    try:
        # Try to make a simple database query
        Admin.query.first()
        return 'OK', 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return 'Error', 500


@login_manager.user_loader
def load_user(user_id):
    """Загружает пользователя (администратора или обычного пользователя)"""
    admin = Admin.query.get(int(user_id))
    if admin:
        return admin
    return User.query.get(int(user_id))


@app.route('/course/<int:id>')
@track_user_activity('view_course')
def course_detail(id):
    course = Course.query.get_or_404(id)
    reviews = CourseReview.query.filter_by(course_id=id) \
        .order_by(CourseReview.created_at.desc()) \
        .all()
    return render_template('course_detail.html',
                           course=course,
                           reviews=reviews)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Неверный email или пароль', 'error')
    return render_template('admin/login.html',
                           form=form,
                           bot_username=BOT_USERNAME,
                           auth_url=f"/admin/telegram-auth")


@app.route('/admin/telegram-auth')
@track_user_activity('login')
def admin_telegram_auth():
    logger.debug(f"Получены данные авторизации Telegram: {request.args}")
    auth_data = request.args

    if check_telegram_authorization(auth_data):
        telegram_id = int(auth_data['id'])
        logger.debug(f"Проверка администратора с telegram_id: {telegram_id}")

        admin = Admin.query.filter_by(telegram_id=telegram_id).first()
        if admin:
            login_user(admin)

            # Отправляем уведомление главному администратору о входе другого админа
            if telegram_id != MAIN_ADMIN_ID:
                try:
                    message = (
                        f"👤 Вход в админ-панель\n"
                        f"Администратор: {admin.username or admin.first_name}\n"
                        f"ID: {admin.telegram_id}\n"
                        f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    bot.send_message(MAIN_ADMIN_ID, message)
                except Exception as e:
                    logger.error(
                        f"Ошибка отправки уведомления главному администратору: {e}"
                    )

            notify_admin_login(admin)
            return jsonify({'success': True})
        else:
            if telegram_id == MAIN_ADMIN_ID:
                # Создаем временный email для главного администратора
                temp_email = f"admin_{telegram_id}@example.com"
                admin = Admin(
                    telegram_id=telegram_id,
                    email=temp_email,  # Добавляем временный email
                    username=auth_data.get('username'),
                    first_name=auth_data.get('first_name'),
                    last_name=auth_data.get('last_name', ''))
                db.session.add(admin)
                try:
                    db.session.commit()
                    logger.info(
                        f"Создан новый администратор с telegram_id: {telegram_id}"
                    )
                    login_user(admin)
                    notify_admin_login(admin)
                    return jsonify({'success': True})
                except Exception as e:
                    logger.error(
                        f"Ошибка при создании администратора: {str(e)}")
                    db.session.rollback()
                    return jsonify({
                        'success':
                            False,
                        'error':
                            'Ошибка при создании администратора'
                    })

            logger.warning(
                f"Пользователь с telegram_id {telegram_id} попытался войти, но не является администратором"
            )
            return jsonify({
                'success': False,
                'error': 'У вас нет прав администратора'
            })
    else:
        logger.error("Не удалось проверить авторизацию Telegram")
        return jsonify({'success': False, 'error': 'Ошибка авторизации'})


def check_telegram_authorization(auth_data):
    """Validates the authorization data from Telegram login widget."""
    if not auth_data:
        logger.error("No auth data provided")
        return False

    required_fields = ['id', 'first_name', 'auth_date', 'hash']
    if not all(field in auth_data for field in required_fields):
        logger.error(f"Missing required fields. Got: {list(auth_data.keys())}")
        return False

    auth_data_dict = dict(auth_data)
    received_hash = auth_data_dict.pop('hash', '')

    # Remove undefined values and create check string
    data_check_arr = []
    for key in sorted(auth_data_dict.keys()):
        val = auth_data_dict[key]
        # Skip 'undefined' values from JavaScript and None values
        if val not in ['undefined', None, 'None', '']:
            data_check_arr.append(f'{key}={val}')

    data_check_string = '\n'.join(data_check_arr)
    logger.debug(f"Data check string: {data_check_string}")

    # Use bot token to create secret key
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode('utf-8'),
                             hashlib.sha256).hexdigest()

    logger.debug(f"Computed hash: {computed_hash}")
    logger.debug(f"Received hash: {received_hash}")

    if computed_hash != received_hash:
        logger.error("Hash verification failed")
        return False

    # Check auth_date is not too old (< 24h)
    auth_date = int(auth_data_dict.get('auth_date', 0))
    now = int(time.time())
    if (now - auth_date) > 86400:
        logger.error(f"Auth date too old. Auth date: {auth_date}, Now: {now}")
        return False

    return True


@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    courses_count = Course.query.count()
    locations_count = Location.query.count()
    applications_count = TrialLesson.query.count()
    pending_count = TrialLesson.query.filter_by(confirmed=False).count()

    return render_template('admin/dashboard.html',
                           courses_count=courses_count,
                           locations_count=locations_count,
                           applications_count=applications_count,
                           pending_count=pending_count)


@app.route('/course/<int:course_id>/rate', methods=['POST'])
@login_required
def rate_course(course_id):
    """Handle course rating submission."""
    logger.info(f"Получен запрос на оценку курса {course_id}")

    try:
        # Проверяем существование пользователя
        user = User.query.get(current_user.id)
        if not user:
            logger.error(
                f"Пользователь с ID {current_user.id} не найден в базе данных")
            flash('Ошибка аутентификации', 'error')
            return redirect(url_for('login'))

        # Проверяем существование курса
        course = Course.query.get_or_404(course_id)
        logger.info(f"Найден курс: id={course.id}, name={course.name}")

        # Получаем и валидируем данные
        try:
            rating = float(request.form.get('rating', 0))
            logger.info(f"Полученный рейтинг: {rating}")
        except ValueError:
            logger.error("Некорректное значение рейтинга")
            flash('Некорректное значение оценки', 'error')
            return redirect(url_for('course_detail', id=course_id))

        if not 0.5 <= rating <= 5:
            logger.error(f"Рейтинг {rating} вне допустимого диапазона")
            flash('Оценка должна быть от 0.5 до 5 звёзд', 'error')
            return redirect(url_for('course_detail', id=course_id))

        comment = request.form.get('comment', '').strip()
        logger.info(f"Данные отзыва: comment={comment}")

        # Проверяем наличие существующего отзыва
        existing_review = CourseReview.query.filter_by(
            course_id=course_id, user_id=user.id).first()

        if existing_review:
            logger.warning(
                f"Пользователь {user.id} пытается оставить повторный отзыв для курса {course_id}"
            )
            flash('Вы уже оставляли отзыв для этого курса', 'error')
            return redirect(url_for('course_detail', id=course_id))

        # Создаем отзыв в рамках транзакции
        try:
            review = CourseReview(course_id=course.id,
                                  user_id=user.id,
                                  rating=rating,
                                  comment=comment,
                                  source='website')
            logger.info(
                f"Создан объект отзыва: course_id={review.course_id}, user_id={review.user_id}"
            )

            db.session.add(review)

            # Обновляем рейтинг курса
            if course.rating_count:
                new_rating = ((course.rating * course.rating_count) +
                              rating) / (course.rating_count + 1)
                logger.info(
                    f"Обновление рейтинга курса: старый={course.rating}, новый={new_rating}"
                )
                course.rating = new_rating
            else:
                logger.info(f"Установка первого рейтинга курса: {rating}")
                course.rating = rating
            course.rating_count += 1

            # Логируем активность
            review.log_activity('create')

            db.session.commit()
            logger.info(f"Успешно сохранен отзыв для курса {course_id}")
            flash('Спасибо за ваш отзыв!', 'success')

        except Exception as e:
            db.session.rollback()
            logger.error(
                f"Ошибка при сохранении отзыва в транзакции: {str(e)}",
                exc_info=True)
            flash('Произошла ошибка при сохранении отзыва', 'error')
            return redirect(url_for('course_detail', id=course_id))

    except Exception as e:
        logger.error(f"Ошибка при обработке отзыва: {str(e)}", exc_info=True)
        flash('Произошла ошибка при обработке отзыва', 'error')

    return redirect(url_for('course_detail', id=course_id))


@app.route('/review/<int:review_id>/edit', methods=['POST'])
@login_required
def edit_review(review_id):
    """Edit an existing review."""
    review = CourseReview.query.get_or_404(review_id)

    if not review.can_edit:
        flash('У вас нет прав на редактирование этого отзыва', 'error')
        return redirect(url_for('course_detail', id=review.course_id))

    try:
        rating = float(request.form.get('rating', 0))
        if not 0.5 <= rating <= 5:
            flash('Оценка должна быть от 0.5 до 5 звёзд', 'error')
            return redirect(url_for('course_detail', id=review.course_id))

        # Сохраняем старый рейтинг для пересчета
        old_rating = review.rating

        # Обновляем отзыв
        review.rating = rating
        review.comment = request.form.get('comment', '').strip()

        # Пересчитываем общий рейтинг курса
        course = review.course
        course.rating = ((course.rating * course.rating_count) - old_rating +
                         rating) / course.rating_count

        # Логируем изменение
        review.log_activity('edit')

        db.session.commit()
        flash('Отзыв успешно обновлен', 'success')

    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при обновлении отзыва: {str(e)}")
        flash('Произошла ошибка при обновлении отзыва', 'error')

    return redirect(url_for('course_detail', id=review.course_id))


@app.route('/review/<int:review_id>/delete')
@login_required
def delete_review(review_id):
    """Delete a review."""
    review = CourseReview.query.get_or_404(review_id)

    if not review.can_edit:
        flash('У вас нет прав на удаление этого отзыва', 'error')
        return redirect(url_for('course_detail', id=review.course_id))

    try:
        course = review.course

        # Пересчитываем рейтинг курса
        if course.rating_count > 1:
            course.rating = ((course.rating * course.rating_count) -
                             review.rating) / (course.rating_count - 1)
        else:
            course.rating = 0
        course.rating_count -= 1

        # Логируем удаление
        review.log_activity('delete')

        db.session.delete(review)
        db.session.commit()

        flash('Отзыв успешно удален', 'success')

    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при удалении отзыва: {str(e)}")
        flash('Произошла ошибка при удалении отзыва', 'error')

    return redirect(url_for('course_detail', id=review.course_id))


@app.route('/admin/courses')
@admin_required
def admin_courses():
    courses = Course.query.all()
    return render_template('admin/courses.html',
                           courses=courses,
                           form=CourseForm())


@app.route('/admin/courses/add', methods=['POST'])
@admin_required
def add_course():
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(name=form.name.data,
                        description=form.description.data,
                        min_age=form.min_age.data,
                        max_age=form.max_age.data)
        db.session.add(course)
        db.session.commit()

        # Add tags
        tags = [
            tag.strip() for tag in form.tags.data.split(',') if tag.strip()
        ]
        for tag in tags:
            course_tag = CourseTag(course_id=course.id, tag=tag)
            db.session.add(course_tag)
        db.session.commit()

        notify_admin_action(
            current_user,
            'course_add',
            f"Добавлен новый курс: {course.name}\n" \
            f"Возраст: {course.min_age}-{course.max_age} лет\n" \
            f"Теги: {', '.join(tags)}"
        )

        flash('Курс успешно добавлен', 'success')
    return redirect(url_for('admin_courses'))


@app.route('/admin/courses/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_course(id):
    course = Course.query.get_or_404(id)
    form = CourseForm(obj=course)

    if form.validate_on_submit():
        form.populate_obj(course)

        # Update tags
        CourseTag.query.filter_by(course_id=id).delete()
        tags = [
            tag.strip() for tag in form.tags.data.split(',') if tag.strip()
        ]
        for tag in tags:
            course_tag = CourseTag(course_id=id, tag=tag)
            db.session.add(course_tag)

        try:
            db.session.commit()
            notify_admin_action(
                current_user,
                'course_edit',
                f"Обновлен курс: {course.name}\n" \
                f"Возраст: {course.min_age}-{course.max_age} лет\n" \
                f"Теги: {', '.join(tags)}"
            )
            flash('Курс успешно обновлен', 'success')
            return redirect(url_for('admin_courses'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при обновлении курса: {str(e)}")
            flash('Ошибка при обновлении курса', 'error')

    current_tags = CourseTag.query.filter_by(course_id=id).all()
    form.tags.data = ', '.join([tag.tag for tag in current_tags])

    return render_template('admin/edit_course.html', form=form, course=course)


@app.route('/admin/courses/<int:id>/delete')
@admin_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    CourseTag.query.filter_by(course_id=id).delete()
    db.session.delete(course)
    db.session.commit()
    flash('Курс успешно удален', 'success')
    return redirect(url_for('admin_courses'))


@app.route('/admin/locations', methods=['GET', 'POST'])
@admin_required
def admin_locations():
    district_form = DistrictForm()
    location_form = LocationForm()

    if district_form.validate_on_submit():
        district = District(name=district_form.name.data)
        try:
            db.session.add(district)
            db.session.commit()
            notify_admin_action(
                current_user,
                'district_add',
                f"Добавлен новый район:\n" \
                f"Название: {district.name}"
            )
            flash('Район успешно добавлен', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding district: {str(e)}")
            flash('Ошибка при добавлении района', 'error')
        return redirect(url_for('admin_locations'))

    districts = District.query.all()
    locations = Location.query.join(District).order_by(District.name,
                                                       Location.address).all()

    return render_template('admin/locations.html',
                           districts=districts,
                           locations=locations,
                           district_form=district_form,
                           location_form=location_form)


@app.route('/admin/districts/<int:id>/edit', methods=['POST'])
@admin_required
def edit_district(id):
    district = District.query.get_or_404(id)
    form = DistrictForm()
    if form.validate_on_submit():
        old_name = district.name
        district.name = form.name.data
        try:
            db.session.commit()
            notify_admin_action(
                current_user,
                'district_edit',
                f"Изменен район:\n" \
                f"Название: {old_name} → {district.name}"
            )
            flash('Район успешно обновлен', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating district: {str(e)}")
            flash('Ошибка при обновлении района', 'error')
    return redirect(url_for('admin_locations'))


@app.route('/admin/districts/<int:id>/delete')
@admin_required
def delete_district(id):
    district = District.query.get_or_404(id)
    try:
        name = district.name
        db.session.delete(district)
        db.session.commit()
        notify_admin_action(
            current_user,
            'district_delete',
            f"Удален район:\n" \
            f"Название: {name}\n" \
            f"Количество адресов: {len(district.locations)}"
        )
        flash('Район успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting district: {str(e)}")
        flash('Ошибка при удалении района', 'error')
    return redirect(url_for('admin_locations'))


@app.route('/admin/districts/<int:district_id>/locations/add',
           methods=['POST'])
@admin_required
def add_location(district_id):
    district = District.query.get_or_404(district_id)
    form = LocationForm(district_id=district_id)
    logger.info(f"Adding location for district: {district.name}")

    if form.validate_on_submit():
        location = Location(district_id=district_id, address=form.address.data)
        try:
            logger.info(
                f"Creating new location with address: {form.address.data}")
            db.session.add(location)
            db.session.commit()
            notify_admin_action(
                current_user,
                'location_add',
                f"Добавлен новый адрес:\n" \
                f"Район: {district.name}\n" \
                f"Адрес: {location.address}"
            )
            flash('Адрес успешно добавлен', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding location: {str(e)}")
            flash('Ошибка при добавлении адреса', 'error')
    else:
        logger.error(f"Form validation failed: {form.errors}")
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Ошибка в поле {field}: {error}', 'error')

    return redirect(url_for('admin_locations'))


@app.route('/admin/locations/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_location(id):
    location = Location.query.get_or_404(id)
    form = LocationForm(obj=location)
    logger.info(f"Editing location {id}: {location.address}")

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                old_address = location.address
                location.address = form.address.data
                logger.info(
                    f"Updating location {id} from '{old_address}' to '{form.address.data}'"
                )
                db.session.commit()

                notify_admin_action(
                    current_user,
                    'location_edit',
                    f"Изменен адрес:\n" \
                    f"Район: {location.district.name}\n" \
                    f"Адрес: {old_address} → {location.address}"
                )
                flash('Адрес успешно обновлен', 'success')
                return redirect(url_for('admin_locations'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error updating location {id}: {str(e)}")
                flash('Ошибка при обновлении адреса', 'error')
        else:
            logger.error(f"Form validation failed: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Ошибка в поле {field}: {error}', 'error')

    return render_template('admin/edit_location.html',
                           form=form,
                           location=location)


@app.route('/admin/locations/<int:id>/delete')
@admin_required
def delete_location(id):
    location = Location.query.get_or_404(id)
    try:
        district_name = location.district.name
        address = location.address
        db.session.delete(location)
        db.session.commit()
        notify_admin_action(
            current_user,
            'location_delete',
            f"Удален адрес:\n" \
            f"Район: {district_name}\n" \
            f"Адрес: {address}"
        )
        flash('Адрес успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting location: {str(e)}")
        flash('Ошибка при удалении адреса', 'error')
    return redirect(url_for('admin_locations'))


@app.route('/admin/applications')
@admin_required
def admin_applications():
    applications = TrialLesson.query.all()
    return render_template('admin/applications.html',
                           applications=applications)


@app.route('/admin/applications/<int:id>/approve')
@admin_required
def approve_application(id):
    application = TrialLesson.query.get_or_404(id)
    application.confirmed = True
    db.session.commit()

    # Notify via Telegram
    notify_admin_action(
        current_user,
        'application_approve',
        f"Подтверждена заявка на пробное занятие\n" \
        f"Курс: {application.course.name}\n" \
        f"Ученик: {application.user.child_name}\n" \
        f"Дата: {application.date.strftime('%Y-%m-%d %H:%M')}"
    )

    # Send rating request to user via Telegram
    if application.user.telegram_id:
        confirmation_message = (
            f"✅ Ваша запись на пробное занятие по курсу \"{application.course.name}\" подтверждена!\n\n"
            "Мы были бы благодарны, если бы вы оценили курс после занятия.")

        keyboard = []
        row = []
        for i in range(10, 0, -1):
            rating = i / 2
            row.append(
                InlineKeyboardButton(
                    f"{'★' * int(rating)}{('½' if rating % 1 else '')}",
                    callback_data=f"stars_{rating}_{application.course_id}"))
            if len(row) == 5:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append(
            [InlineKeyboardButton("❌ Позже", callback_data="rate_later")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            bot.send_message(chat_id=application.user.telegram_id,
                             text=confirmation_message,
                             reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error sending rating request to user: {str(e)}")

    flash('Заявка успешно подтверждена', 'success')
    return redirect(url_for('admin_applications'))


@app.route('/admin/applications/<int:id>/reject')
@admin_required
def reject_application(id):
    application = TrialLesson.query.get_or_404(id)

    # Store application details before deletion for notification
    details = {
        'course_name': application.course.name,
        'child_name': application.user.child_name,
        'date': application.date.strftime('%Y-%m-%d %H:%M')
    }

    try:
        db.session.delete(application)
        db.session.commit()

        # Notify via Telegram
        notify_admin_action(
            current_user,
            'application_reject',
            f"Отклонена заявка на пробное занятие\n"
            f"Курс: {details['course_name']}\n"
            f"Ученик: {details['child_name']}\n"
            f"Дата: {details['date']}"
        )
        flash('Заявка отклонена', 'success')
        return redirect(url_for('admin_applications'))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error rejecting application: {str(e)}")
        flash('Ошибка при отклонении заявки', 'error')
        return redirect(url_for('admin_applications'))

@app.route('/admin/admins')
@admin_required
def admin_list():
    try:
        admins = Admin.query.all()        # Получаем статистику по активным администраторам
        active_admins= 0  # Здесь можно добавить логику подсчета активных админов
        return render_template('admin/admins.html',
                               admins=admins,
                               form=AdminForm(),                               edit_form=AdminForm(),
                               main_admin_id=MAIN_ADMIN_ID,
                               active_admins=active_admins)
    except Exception as e:
        logger.error(f"Error in admin_list route: {str(e)}")
        flash('Произошла ошибка при загрузке списка администраторов', 'error')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/admins/add', methods=['POST'])
@admin_required
def add_admin():
    if current_user.telegram_id != MAIN_ADMIN_ID:
        flash(
            'Только главный администратор может добавлять новых администраторов',
            'error')
        return redirect(url_for('admin_list'))

    form = AdminForm()
    if form.validate_on_submit():
        try:
            admin = Admin(telegram_id=form.telegram_id.data,
                          email=form.email.data,
                          username=form.username.data,
                          first_name=form.first_name.data,
                          last_name=form.last_name.data)
            db.session.add(admin)
            db.session.commit()

            notify_admin_action(
                current_user, 'admin_add',
                f"Добавлен новый администратор:\n"
                f"Username: {admin.username}\n"
                f"Email: {admin.email}\n"
                f"Telegram ID: {admin.telegram_id}\n"
                f"First Name: {admin.first_name}\n"
                f"Last Name: {admin.last_name}\n"
            )

            flash('Администратор успешно добавлен', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding admin: {str(e)}")
            flash('Ошибка при добавлении администратора', 'error')
    return redirect(url_for('admin_list'))


@app.route('/admin/admins/<int:id>/edit', methods=['POST'])
@admin_required
def edit_admin(id):
    if current_user.telegram_id != MAIN_ADMIN_ID:
        flash(
            'Только главный администратор может редактировать администраторов',
            'error')
        return redirect(url_for('admin_list'))

    admin = Admin.query.get_or_404(id)
    form = AdminForm()

    if form.validate_on_submit():
        try:
            # Сохраняем старые данные для лога
            old_data = {
                'username': admin.username,
                'email': admin.email,
                'telegram_id': admin.telegram_id
            }

            # Обновляем данные
            admin.email = form.email.data
            admin.telegram_id = form.telegram_id.data
            admin.username = form.username.data
            admin.first_name = form.first_name.data
            admin.last_name = form.last_name.data

            db.session.commit()

            notify_admin_action(
                current_user,
                'admin_edit',
                f"Изменены данные администратора:\n" \
                f"Username: {old_data['username']} → {admin.username}\n" \
                f"Email: {old_data['email']} → {admin.email}\n" \
                f"Telegram ID: {old_data['telegram_id']} → {admin.telegram_id}"
            )

            flash('Данные администратора обновлены', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при обновлении администратора: {str(e)}")
            flash('Ошибка при обновлении данных администратора', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Ошибка в поле {field}: {error}', 'error')

    return redirect(url_for('admin_list'))


@app.route('/admin/admins/<int:id>/delete')
@admin_required
def delete_admin(id):
    if current_user.telegram_id != MAIN_ADMIN_ID:
        flash('Только главный администратор может удалять администраторов',
              'error')
        return redirect(url_for('admin_list'))

    admin = Admin.query.get_or_404(id)
    if admin.telegram_id == MAIN_ADMIN_ID:
        flash('Невозможно удалить главного администратора', 'error')
        return redirect(url_for('admin_list'))

    try:
        # Сохраняем данные для лога
        admin_data = {
            'username': admin.username,
            'telegram_id': admin.telegram_id,
            'email': admin.email
        }

        db.session.delete(admin)
        db.session.commit()

        notify_admin_action(
            current_user,
            'admin_delete',
            f"Удален администратор:\n" \
            f"Username: {admin_data['username']}\n" \
            f"Email: {admin_data['email']}\n" \
            f"Telegram ID: {admin_data['telegram_id']}"
        )

        flash('Администратор успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при удалении администратора: {str(e)}")
        flash('Ошибка при удалении администратора', 'error')

    return redirect(url_for('admin_list'))


@app.route('/login')
def login():
    """Единая точка входа через Telegram"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return render_template('login.html',
                           bot_username=BOT_USERNAME,
                           auth_url=f"/telegram-auth")


@app.route('/telegram-auth')
def telegram_auth():
    """Обработка авторизации через Telegram"""
    logger.debug(f"Получены данные авторизации Telegram: {request.args}")
    auth_data = request.args

    if check_telegram_authorization(auth_data):
        telegram_id = int(auth_data['id'])
        logger.debug(f"Проверка пользователя с telegram_id: {telegram_id}")

        # Проверяем, является ли пользователь администратором
        admin = Admin.query.filter_by(telegram_id=telegram_id).first()
        if admin:
            login_user(admin)
            notify_admin_login(admin)
            return redirect(url_for('admin_dashboard'))

        # Проверяем обычного пользователя
        user = User.query.filter_by(telegram_id=telegram_id).first()
        if user:
            login_user(user)
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            # Создаем нового пользователя
            user = User(telegram_id=telegram_id,
                        username=auth_data.get('username'),
                        first_name=auth_data.get('first_name'),
                        last_name=auth_data.get('last_name', ''))
            db.session.add(user)
            try:
                db.session.commit()
                login_user(user)
                flash(
                    'Добро пожаловать! Пожалуйста, заполните информацию о себе.',
                    'info')
                return redirect(url_for('edit_profile'))
            except Exception as e:
                logger.error(f"Ошибка при создании пользователя: {str(e)}")
                db.session.rollback()
                flash('Произошла ошибка при регистрации', 'error')
                return redirect(url_for('login'))

    flash('Ошибка авторизации через Telegram', 'error')
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/dashboard')
@login_required
def user_dashboard():
    """User dashboard page."""
    try:
        # Check if user is Admin first
        if isinstance(current_user, Admin):
            logger.info(f"Admin {current_user.id} accessing dashboard")
            return redirect(url_for('admin_dashboard'))

        # Refresh user data from database
        db.session.refresh(current_user)
        logger.info(f"Refreshed user data for user_id={current_user.id}")

        # Get user's trial lessons
        trial_lessons = TrialLesson.query.filter_by(user_id=current_user.id) \
            .order_by(TrialLesson.date.desc()).all()

        # Get user's reviews
        reviews = CourseReview.query.filter_by(user_id=current_user.id) \
            .order_by(CourseReview.created_at.desc()).all()

        # Log user profile data only for regular users
        logger.debug(f"User profile data: "
                    f"parent_name={getattr(current_user, 'parent_name', 'N/A')}, "
                    f"child_name={getattr(current_user, 'child_name', 'N/A')}, "
                    f"child_age={getattr(current_user, 'child_age', 'N/A')}, "
                    f"child_interests={getattr(current_user, 'child_interests', 'N/A')}")

        return render_template('user/dashboard.html',
                             trial_lessons=trial_lessons,
                             reviews=reviews)
    except Exception as e:
        logger.error(f"Error in user_dashboard: {str(e)}", exc_info=True)
        flash('Произошла ошибка при загрузке профиля', 'error')
        return redirect(url_for('index'))


@app.route('/user/applications')
@login_required
def user_applications():
    applications = TrialLesson.query.filter_by(user_id=current_user.id) \
        .order_by(TrialLesson.created_at.desc()) \
        .all()
    return render_template('user/applications.html', applications=applications)


@app.route('/user/reviews')
@login_required
def user_reviews():
    reviews = CourseReview.query.filter_by(user_id=current_user.id) \
        .order_by(CourseReview.created_at.desc()) \
        .all()
    return render_template('user/reviews.html', reviews=reviews)


@app.route('/user/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile."""
    # Check if user is Admin
    if isinstance(current_user, Admin):
        flash('Администраторы не могут редактировать профиль через этот интерфейс', 'warning')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        try:
            # Handle avatar upload
            avatar_file = request.files.get('avatar')
            if avatar_file:
                filename = save_avatar(avatar_file)
                if filename:
                    # Delete old avatar if exists
                    current_user.delete_avatar()
                    current_user.avatar_path = filename
                else:
                    flash('Ошибка при загрузке аватара', 'error')

            # Update user profile data
            current_user.parent_name = request.form.get('parent_name')
            current_user.phone = request.form.get('phone')
            current_user.child_name = request.form.get('child_name')
            current_user.child_age = request.form.get('child_age', type=int)
            current_user.child_interests = request.form.get('child_interests')

            logger.info(f"Updating profile for user_id={current_user.id}")
            logger.debug(f"New profile data: "
                        f"parent_name={current_user.parent_name}, "
                        f"phone={current_user.phone}, "
                        f"child_name={current_user.child_name}, "
                        f"child_age={current_user.child_age}, "
                        f"child_interests={current_user.child_interests}")

            db.session.commit()
            flash('Профиль успешно обновлен', 'success')

            # Refresh user data after update
            db.session.refresh(current_user)
            return redirect(url_for('user_dashboard'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Ошибка при обновлении профиля: {str(e)}", exc_info=True)
            flash('Произошла ошибка при обновлении профиля', 'error')

    return render_template('user/edit_profile.html')


@app.route('/course/<int:course_id>/apply', methods=['POST'])
@login_required
def apply_for_trial(course_id):
    course = Course.query.get_or_404(course_id)
    location_id = request.form.get('location_id', type=int)
    date_str = request.form.get('date')

    if not all([location_id, date_str]):
        flash('Пожалуйста, заполните все поля', 'error')
        return redirect(url_for('course_detail', id=course_id))

    try:
        # Преобразование строки даты в объект datetime
        date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')

        # Создание новой заявки с привязкой к текущему пользователю
        trial = TrialLesson(
            user_id=current_user.id,  # Используем ID текущего пользователя
            course_id=course_id,
            location_id=location_id,
            date=date,
            telegram_id=current_user.
            telegram_id  # Add telegram_id to TrialLesson
        )

        db.session.add(trial)
        db.session.commit()

        flash('Заявка на пробное занятие успешно отправлена!', 'success')
    except ValueError:
        flash('Неверный формат даты', 'error')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating trial lesson: {str(e)}")
        flash('Произошла ошибка при создании заявки', 'error')

    return redirect(url_for('course_detail', id=course_id))


@app.route('/admin/statistics')
@admin_required
def admin_statistics():
    # Получаем общую статистику
    total_users = User.query.count()
    active_today = UserActivity.query \
        .filter(UserActivity.timestamp >= db.func.current_date()) \
        .distinct(UserActivity.user_id) \
        .count()

    # Статистика по платформам
    platform_stats = db.session.query(
        db.func.coalesce(UserActivity.details.op('->>')('platform'),
                         'web').label('platform'),
        db.func.count(UserActivity.id)).group_by('platform').all()

    platform_stats = [count for _, count in platform_stats]

    # Получаем активность за последние 7 дней
    activity_data = db.session.query(
        db.func.date_trunc('day', UserActivity.timestamp).label('date'),
        db.func.count(UserActivity.id)
    ).group_by('date') \
        .order_by('date') \
        .limit(7) \
        .all()

    activity_dates = [date.strftime('%Y-%m-%d') for date, _ in activity_data]
    activity_counts = [count for _, count in activity_data]

    # Получаем последние действия
    recent_activities = UserActivity.query \
        .join(User) \
        .order_by(UserActivity.timestamp.desc()) \
        .limit(10) \
        .all()

    return render_template('admin/statistics.html',
                           total_users=total_users,
                           active_today=active_today,
                           platform_stats=platform_stats,
                           activity_dates=activity_dates,
                           activity_counts=activity_counts,
                           recent_activities=recent_activities)


@app.route('/admin/reviews')
@admin_required
def admin_reviews():
    """Страница управления отзывами."""
    try:
        # Получаем все отзывы, отсортированные по дате
        recent_reviews = CourseReview.query.order_by(
            CourseReview.created_at.desc()).all()

        # Подсчитываем общую статистику
        total_reviews = len(recent_reviews)
        reviews_with_comments = sum(1 for r in recent_reviews if r.comment)

        # Считаем средний рейтинг
        average_rating = 0
        if total_reviews > 0:
            average_rating = sum(r.rating
                                 for r in recent_reviews) / total_reviews

        # Подготавливаем данные для графика распределения оценок
        ratings_data = [0] * 10  # Для оценок от 0.5 до 5.0 с шагом 0.5
        for review in recent_reviews:
            index = int(
                review.rating * 2) - 1  # Преобразуем рейтинг в индекс массива
            ratings_data[index] += 1

        ratings_labels = [str(i / 2)
                          for i in range(1, 11)]  # ["0.5", "1.0", ..., "5.0"]

        # Подготавливаем данные для графика источников отзывов
        website_reviews = sum(1 for r in recent_reviews
                              if r.source == 'website')
        telegram_reviews = sum(1 for r in recent_reviews
                               if r.source == 'telegram')
        sources_data = [website_reviews, telegram_reviews]

        return render_template('admin/reviews.html',
                               recent_reviews=recent_reviews,
                               total_reviews=total_reviews,
                               average_rating=average_rating,
                               reviews_with_comments=reviews_with_comments,
                               ratings_data=ratings_data,
                               ratings_labels=ratings_labels,
                               sources_data=sources_data)

    except Exception as e:
        logger.error(f"Error in admin_reviews: {str(e)}")
        flash('Произошла ошибка при загрузке страницы отзывов', 'error')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/reviews/<int:review_id>/delete')
@admin_required
def admin_delete_review(review_id):
    """Удаление отзыва администратором."""
    logger.info(f"Attempting to delete review {review_id}")

    try:
        review = CourseReview.query.get_or_404(review_id)
        course = review.course

        # Сохраняем данные для уведомления
        details = {
            'course_name': course.name,
            'rating': review.rating,
            'reviewer_name': 'Анонимный пользователь'
        }

        # Определяем имя рецензента
        if review.user:
            if review.user.parent_name:
                details['reviewer_name'] = review.user.parent_name
            elif review.user.username:
                details['reviewer_name'] = review.user.username
            elif review.user.first_name:
                details[
                    'reviewer_name'] = f"{review.user.first_name} {review.user.last_name or ''}"

        logger.info(f"Found review for course: {details['course_name']}")

        # Пересчитываем рейтинг курса
        remaining_reviews = CourseReview.query.filter(
            CourseReview.course_id == course.id, CourseReview.id
            != review_id).all()

        # Удаляем отзыв
        db.session.delete(review)

        # Обновляем рейтинг курса
        if remaining_reviews:
            total_rating = sum(r.rating for r in remaining_reviews)
            course.rating = total_rating / len(remaining_reviews)
            course.rating_count = len(remaining_reviews)
            logger.info(
                f"Updated course rating to {course.rating} ({course.rating_count} reviews)"
            )
        else:
            course.rating = 0
            course.rating_count = 0
            logger.info("Reset course rating (no reviews left)")

        # Сохраняем изменения
        db.session.commit()

        # Отправляем уведомление
        notify_admin_action(
            current_user,
            'review_delete',
            f"Удален отзыв:\n" \
            f"Курс: {details['course_name']}\n" \
            f"Автор: {details['reviewer_name']}\n" \
            f"Оценка: {details['rating']}"
        )

        flash('Отзыв успешно удален', 'success')
        logger.info(f"Successfully deleted review {review_id}")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting review {review_id}: {str(e)}",
                     exc_info=True)
        flash('Произошла ошибка при удалении отзыва', 'error')

    return redirect(url_for('admin_reviews'))


@app.route('/admin/delete/<int:id>', methods=['POST'])
@admin_required
def delete_admin_new(id):
    if current_user.telegram_id != MAIN_ADMIN_ID:
        flash(
            'Только главный администратор может удалять других администраторов',
            'error')
        return redirect(url_for('admin_list'))

    if id == current_user.id:
        flash('Невозможно удалить собственную учетную запись', 'error')
        return redirect(url_for('admin_list'))

    try:
        admin = Admin.query.get_or_404(id)

        # Сохраняем данные для уведомления перед удалением
        admin_info = {
            'username': admin.username,
            'telegram_id': admin.telegram_id,
            'email': admin.email
        }

        db.session.delete(admin)
        db.session.commit()

        # Отправляем уведомление об удалении администратора
        notify_admin_action(
            current_user,
            'admin_delete',
            f"Удален администратор:\n" \
            f"Username: {admin_info['username']}\n" \
            f"Telegram ID: {admin_info['telegram_id']}\n" \
            f"Email: {admin_info['email']}"
        )

        flash('Администратор успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при удалении администратора: {str(e)}")
        flash('Произошла ошибка при удалении администратора', 'error')

    return redirect(url_for('admin_list'))


@app.context_processor
def utility_processor():
    return {'current_year': datetime.now().year}


@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    """Страница настроек сайта"""
    if request.method == 'POST':
        try:
            logger.info("Получены данные формы настроек:")
            for key, value in request.form.items():
                logger.info(f"{key}: {value}")

            icon_file = request.files.get('site_icon')
            success, message = update_site_settings(request.form, icon_file)
            flash(message, 'success' if success else 'error')
        except Exception as e:
            logger.error(f"Ошибка при сохранении настроек: {str(e)}")
            flash('Произошла ошибка при сохранении настроек', 'error')
        return redirect(url_for('admin_settings'))

    settings = SiteSettings.get_settings()
    return render_template('admin/settings.html', settings=settings)


@app.context_processor
def inject_site_settings():
    """Make site settings available to all templates"""
    return {'site_settings': SiteSettings.get_settings()}
def nl2br(value):
    if value:
        # Сначала экранируем HTML для предотвращения XSS
        from markupsafe import escape
        from markupsafe import Markup
        # Экранируем значение для предотвращения XSS
        escaped_value = escape(value)
        # Заменяем символы переноса строк на HTML тег <br> и возвращаем как безопасную разметку
        # Важно: используем Markup, чтобы Flask не экранировал теги <br> повторно
        return Markup(escaped_value.replace('\n', Markup('<br>\n')))
    return ''

# Регистрация фильтра
app.jinja_env.filters['nl2br'] = nl2br

# Add range filter to Jinja2 environment
app.jinja_env.filters['range'] = range

# Add routes for terms and privacy pages
@app.route('/terms')
def terms():
    """Render terms of service page."""
    try:
        site_settings = get_site_settings()
        logger.debug(f"Terms text loaded: {bool(site_settings and site_settings.terms_of_service)}")
        return render_template('terms.html', site_settings=site_settings)
    except Exception as e:
        logger.error("Error loading terms page", exc_info=True)
        flash('Произошла ошибка при загрузке условий использования', 'error')
        return render_template('terms.html', site_settings=None)

@app.route('/privacy')
def privacy():
    """Render privacy policy page."""
    try:
        site_settings = get_site_settings()
        logger.debug(f"Privacy policy loaded: {bool(site_settings and site_settings.privacy_policy)}")
        return render_template('privacy.html', site_settings=site_settings)
    except Exception as e:
        logger.error("Error loading privacy page", exc_info=True)
        flash('Произошла ошибка при загрузке политики конфиденциальности', 'error')
        return render_template('privacy.html', site_settings=None)

@app.route('/user/delete_avatar', methods=['POST'])
@login_required
def delete_avatar():
    """Удаление загруженного аватара пользователя"""
    success = current_user.delete_avatar()
    return jsonify({'success': success})

# Добавляем функцию для сохранения изображений новостей
def save_news_image(file):
    """Save a news image and return the filename"""
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{timestamp}_{filename}"

    # Создаем директорию, если её нет
    upload_path = os.path.join('static', 'uploads', 'news')
    os.makedirs(upload_path, exist_ok=True)

    filepath = os.path.join(upload_path, new_filename)

    # Сохраняем и оптимизируем изображение
    with Image.open(file) as img:
        # Максимальный размер 1200x1200
        img.thumbnail((1200, 1200))
        img.save(filepath, optimize=True, quality=85)

    return new_filename

# Маршруты для новостей
@app.route('/news')
def news_list():
    """Display list of news with search and sorting."""
    search_query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'newest')  # newest, popular
    current_category = request.args.get('category')
    current_tag = request.args.get('tag')

    # Base query
    query = News.query

    # Apply search filter
    if search_query:
        query = query.filter(
            db.or_(News.title.ilike(f'%{search_query}%'),
                   News.content.ilike(f'%{search_query}%'))
        )

    # Apply category filter
    if current_category:
        category = NewsCategory.query.filter_by(slug=current_category).first()
        if category:
            query = query.filter(News.category_id == category.id)

    # Apply tag filter
    if current_tag:
        query = query.join(News.tags).filter(NewsTag.name == current_tag)

    # Apply sorting
    if sort_by == 'popular':
        query = query.order_by(News.views_count.desc())
    else:  # newest
        query = query.order_by(News.created_at.desc())

    # Get all categories and tags for filters
    all_categories = NewsCategory.query.order_by(NewsCategory.name).all()
    all_tags = NewsTag.query.order_by(NewsTag.name).all()

    # Execute query
    news = query.all()

    # Get popular news for sidebar
    popular_news = News.query.order_by(News.views_count.desc()).limit(5).all()

    return render_template('news/list.html',
                         news=news,
                         search_query=search_query,
                         sort_by=sort_by,
                         current_category=current_category,
                         current_tag=current_tag,
                         all_categories=all_categories,
                         all_tags=all_tags,
                         popular_news=popular_news)


@app.route('/news/create', methods=['GET', 'POST'])
@login_required
def news_create():
    """Create a new news post."""
    if not current_user.is_admin:
        flash('Только администраторы могут создавать новости', 'error')
        return redirect(url_for('news_list'))

    form = NewsForm()
    # Set choices for category select field
    categories = NewsCategory.query.all()
    form.category_id.choices = [(0, 'Без категории')] + [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        try:
            # Create news object and add to session
            news = News(
                title=form.title.data,
                content=form.content.data,
                author_id=current_user.id,
                category_id=form.category_id.data if form.category_id.data != 0 else None,
                is_admin_author=True  # Устанавливаем флаг администратора
            )
            db.session.add(news)
            db.session.commit()  # Commit to get news.id

            # Process tags
            if form.tags.data:
                tags = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
                for tag_name in tags:
                    tag = NewsTag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = NewsTag(name=tag_name)
                        db.session.add(tag)
                    news.tags.append(tag)

            # Handle images
            images = request.files.getlist('images')
            for image in images:
                if image and allowed_file(image.filename):
                    original_filename = image.filename
                    filename = secure_filename(image.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'news', filename)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    image.save(filepath)
                    news_image = NewsImage(
                        news_id=news.id,
                        filename=filename,
                        original_filename=original_filename,
                        url=url_for('static', filename=f'uploads/news/{filename}')
                    )
                    db.session.add(news_image)

            db.session.commit()
            flash('Новость успешно создана', 'success')
            return redirect(url_for('news_detail', id=news.id))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating news: {str(e)}")
            flash('Ошибка при создании новости', 'error')

    return render_template('news/create.html', form=form)


@app.route('/news/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def news_edit(id):
    news = News.query.get_or_404(id)
    if not news.can_edit:
        flash('У вас нет прав на редактирование этой новости', 'error')
        return redirect(url_for('news_detail', id=id))

    form = NewsForm(obj=news)

    if form.validate_on_submit():
        form.populate_obj(news)

        # Update category
        if form.category_id.data != 0:
            news.category_id = form.category_id.data
        else:
            news.category_id =None

        # Update tags
        news.tags = []
        if form.tags.data:
            tags = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
            for tag_name in tags:
                tag = NewsTag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag = NewsTag(name=tag_name)
                    db.session.add(tag)
                news.tags.append(tag)

        try:
            db.session.commit()
            flash('Новость успешно обновлена', 'success')
            return redirect(url_for('news_detail', id=id))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при обновлении новости', 'error')
            logger.error(f"Error updating news: {str(e)}")

    # Set current values
    if news.category_id:
        form.category_id.data = news.category_id
    form.tags.data = ', '.join(tag.name for tag in news.tags)

    return render_template('news/edit.html', form=form, news=news)


@app.route('/news/<int:id>')
def news_detail(id):
    """Display a specific news post."""
    news = News.query.get_or_404(id)
    news.views_count +=1
    db.session.commit()
    form = NewsCommentForm()
    return render_template('news/detail.html', news=news, form=form)


@app.route('/news/<int:id>/delete')
@login_required
def news_delete(id):
    """Delete a news post."""
    news = News.query.get_or_404(id)

    if not news.can_edit:
        flash('У вас нет прав на удаление этой новости', 'error')
        return redirect(url_for('news_detail', id=id))

    try:
        # Delete associated images first
        for image in news.images:
            image.delete_file()

        db.session.delete(news)
        db.session.commit()
        flash('Новость успешно удалена', 'success')
        return redirect(url_for('news_list'))
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting news: {str(e)}")
        flash('Ошибка при удалении новости', 'error')
        return redirect(url_for('news_detail', id=id))

@app.route('/news/comment/add', methods=['POST'])
@login_required
def news_comment_add():
    """Add a comment to a news post."""
    form = NewsCommentForm()
    if form.validate_on_submit():
        try:
            comment = NewsComment(
                content=form.content.data,
                news_id=form.news_id.data,
                author_id=current_user.id,
                is_admin_author=current_user.is_admin,
                parent_id=form.parent_id.data if form.parent_id.data else None
            )
            db.session.add(comment)
            db.session.commit()
            flash('Комментарий успешно добавлен', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding comment: {str(e)}")
            flash('Ошибка при добавлении комментария', 'error')
    return redirect(url_for('news_detail', id=form.news_id.data))

@app.route('/admin/news-categories', methods=['GET', 'POST'])
@admin_required
def admin_news_categories():
    form = NewsCategoryForm()
    if form.validate_on_submit():
        category = NewsCategory(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Категория успешно добавлена', 'success')
        return redirect(url_for('admin_news_categories'))
    categories = NewsCategory.query.all()
    return render_template('admin/news_categories.html', categories=categories, form=form)


@app.route('/admin/news-categories/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_news_category(id):
    category = NewsCategory.query.get_or_404(id)
    form = NewsCategoryForm(obj=category)
    if form.validate_on_submit():
        form.populate_obj(category)
        db.session.commit()
        flash('Категория успешно обновлена', 'success')
        return redirect(url_for('admin_news_categories'))
    return render_template('admin/edit_news_category.html', category=category, form=form)


@app.route('/admin/news-categories/<int:id>/delete', methods=['GET', 'DELETE'])
@admin_required
def delete_news_category(id):
    """Delete a news category."""
    category = NewsCategory.query.get_or_404(id)
    try:
        # Store category name for notification
        category_name = category.name

        # Delete the category
        db.session.delete(category)
        db.session.commit()

        # Notify admin
        notify_admin_action(
            current_user,
            'category_delete',
            f"Удалена категория новостей:\n"
            f"Название: {category_name}\n"
            f"Количество новостей: {len(category.news)}"
        )

        flash('Категория успешно удалена', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting news category: {str(e)}")
        flash('Ошибка при удалении категории', 'error')

    return redirect(url_for('admin_news_categories'))


@app.route('/admin/news-categories/add', methods=['POST'])
@admin_required
def add_news_category():
    """Add a new news category."""
    form = NewsCategoryForm()
    if form.validate_on_submit():
        try:
            category = NewsCategory(
                name=form.name.data,
                slug=form.slug.data,
                description=form.description.data
            )
            db.session.add(category)
            db.session.commit()

            notify_admin_action(
                current_user,
                'category_add',
                f"Добавлена новая категория новостей:\n" \
                f"Название: {category.name}\n" \
                f"Slug: {category.slug}"
            )

            flash('Категория успешно добавлена', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding category: {str(e)}")
            flash('Ошибка при добавлении категории', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Ошибка в поле {field}: {error}', 'error')

    return redirect(url_for('admin_news_categories'))


if __name__ == "__main__":
    try:
        logger.info("Starting Flask server...")

        # Initialize database and create tables
        with app.app_context():
            from extensions import db
            try:
                db.create_all()
                logger.info("Database tables created/updated successfully")
            except Exception as e:
                logger.error(f"Database initialization error: {str(e)}")
                logger.error(traceback.format_exc())
                raise

        app.run(
            host="0.0.0.0",
            port=5000,
            debug=True
        )
    except Exception as e:
        logger.error(f"Server startup error: {str(e)}")
        logger.error(traceback.format_exc())
        raise