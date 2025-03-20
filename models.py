from extensions import db
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import CheckConstraint
import os
import bbcode
from datetime import datetime
from utils.bbcode_formatter import parse_bbcode

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(120))
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))

    def get_id(self):
        return str(self.id)

    @property
    def is_admin(self):
        return True

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False)
    username = db.Column(db.String(120))
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    parent_name = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    child_name = db.Column(db.String(120))
    child_age = db.Column(db.Integer)
    child_interests = db.Column(db.Text)
    avatar_path = db.Column(db.String(255))
    telegram_avatar_url = db.Column(db.String(255))

    # Relationships
    trial_lessons = db.relationship('TrialLesson', back_populates='user', lazy=True)
    reviews = db.relationship('CourseReview', back_populates='user', lazy=True)
    activities = db.relationship('UserActivity', back_populates='user', lazy=True)
    sessions = db.relationship('UserSessionStats', back_populates='user', lazy=True)

    def get_id(self):
        return str(self.id)

    @property
    def is_admin(self):
        return Admin.query.filter_by(telegram_id=self.telegram_id).first() is not None

    @property
    def display_name(self):
        if self.parent_name:
            return self.parent_name
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.username:
            return self.username
        return "Анонимный пользователь"

    @property
    def avatar_url(self):
        """Returns the URL of the user's avatar"""
        if self.avatar_path and os.path.exists(f"static/uploads/avatars/{self.avatar_path}"):
            return f"/static/uploads/avatars/{self.avatar_path}"
        return self.telegram_avatar_url or "/static/img/default-avatar.svg"

    def delete_avatar(self):
        """Удаляет загруженный аватар пользователя"""
        if self.avatar_path:
            try:
                os.remove(f"static/uploads/avatars/{self.avatar_path}")
                self.avatar_path = None
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                return False
        return True

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    min_age = db.Column(db.Integer, nullable=False)
    max_age = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)

    # Relationships
    tags = db.relationship('CourseTag', back_populates='course', lazy=True, cascade="all, delete-orphan")
    trial_lessons = db.relationship('TrialLesson', back_populates='course', lazy=True)
    reviews = db.relationship('CourseReview', back_populates='course', lazy=True)

class District(db.Model):
    __tablename__ = 'districts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    locations = db.relationship('Location', back_populates='district', lazy=True, cascade="all, delete-orphan")

class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), nullable=False)
    address = db.Column(db.Text, nullable=False)

    # Relationships
    district = db.relationship('District', back_populates='locations')
    trial_lessons = db.relationship('TrialLesson', back_populates='location', lazy=True)

class TrialLesson(db.Model):
    __tablename__ = 'trial_lessons'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    telegram_id = db.Column(db.BigInteger)
    date = db.Column(db.DateTime, nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    user = db.relationship('User', back_populates='trial_lessons')
    course = db.relationship('Course', back_populates='trial_lessons')
    location = db.relationship('Location', back_populates='trial_lessons')

class CourseReview(db.Model):
    __tablename__ = 'course_reviews'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    source = db.Column(db.String(50), default='website')

    __table_args__ = (
        CheckConstraint('rating >= 0.5 AND rating <= 5', name='rating_range_check'),
    )

    # Relationships
    course = db.relationship('Course', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')

    @property
    def can_edit(self):
        """Проверяет, может ли текущий пользователь редактировать отзыв"""
        if not current_user.is_authenticated:
            return False
        return current_user.is_admin or current_user.id == self.user_id

    @property
    def display_source(self):
        """Возвращает отформатированный источник отзыва"""
        return "через Telegram бота" if self.source == 'telegram' else ""

    def log_activity(self, action_type):
        """Логирует действие с отзывом в аналитику"""
        activity_data = {
            'review_id': self.id,
            'course_id': self.course_id,
            'rating': self.rating,
            'action': action_type
        }
        activity = UserActivity(
            user_id=self.user_id,
            activity_type=f'review_{action_type}',
            details=activity_data
        )
        db.session.add(activity)

class CourseTag(db.Model):
    __tablename__ = 'course_tags'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    tag = db.Column(db.String(100), nullable=False)

    # Relationships
    course = db.relationship('Course', back_populates='tags')

class UserActivity(db.Model):
    __tablename__ = 'user_activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    details = db.Column(db.JSON, nullable=False, default={})

    # Relationships
    user = db.relationship('User', back_populates='activities')

class UserSessionStats(db.Model):
    __tablename__ = 'user_session_stats'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_start = db.Column(db.DateTime, nullable=False)
    session_end = db.Column(db.DateTime)
    platform = db.Column(db.String(50))
    device_info = db.Column(db.String(255))

    # Relationships
    user = db.relationship('User', back_populates='sessions')

class SiteSettings(db.Model):
    __tablename__ = 'site_settings'

    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(255), nullable=False, default='Educational Platform')
    site_icon = db.Column(db.String(255), default='/static/favicon.png')
    logo_icon_class = db.Column(db.String(100), default='fa-solid fa-graduation-cap')
    footer_icons_color = db.Column(db.String(50), default='#ffffff')
    contact_icons_color = db.Column(db.String(50), default='#ffffff')
    show_social_icons = db.Column(db.Boolean, default=True)

    # Theme settings
    primary_color = db.Column(db.String(50), default='#0d6efd')
    accent_color = db.Column(db.String(50), default='#6610f2')
    heading_font = db.Column(db.String(100), default='Roboto')
    body_font = db.Column(db.String(100), default='Open Sans')

    # Social media links
    website_url = db.Column(db.String(255))
    facebook_url = db.Column(db.String(255))
    instagram_url = db.Column(db.String(255))
    telegram_url = db.Column(db.String(255))
    vk_url = db.Column(db.String(255))
    whatsapp_url = db.Column(db.String(255))

    # Footer content
    footer_about = db.Column(db.Text)

    # Contact information
    contact_address = db.Column(db.String(255))
    contact_email = db.Column(db.String(255))
    contact_phone = db.Column(db.String(255))
    contact_hours = db.Column(db.Text)

    # SEO and Analytics
    meta_description = db.Column(db.String(255))
    meta_keywords = db.Column(db.String(255))
    meta_author = db.Column(db.String(255))
    og_title = db.Column(db.String(255))
    og_description = db.Column(db.String(255))
    og_image = db.Column(db.String(255))
    google_analytics_id = db.Column(db.String(50))
    yandex_metrika_id = db.Column(db.String(50))
    robots_txt = db.Column(db.Text)

    # Content
    welcome_text = db.Column(db.Text)
    terms_of_service = db.Column(db.Text)
    privacy_policy = db.Column(db.Text)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    @classmethod
    def get_settings(cls):
        """Get the site settings, create default if not exists"""
        settings = cls.query.first()
        if not settings:
            settings = cls(
                site_name='Educational Platform',
                site_icon='/static/favicon.png',
                logo_icon_class='fa-solid fa-graduation-cap',
                footer_icons_color='#ffffff',
                contact_icons_color='#ffffff',
                show_social_icons=True,
                primary_color='#0d6efd',
                accent_color='#6610f2',
                heading_font='Roboto',
                body_font='Open Sans',
                footer_about='Добро пожаловать на нашу образовательную платформу',
                contact_address='Москва, ул. Ленина, д. 1',
                contact_email='info@example.com',
                contact_phone='+7 (999) 123-45-67',
                contact_hours='Пн-Пт: 9:00 - 18:00',
                meta_description='Образовательная платформа для развития детей',
                meta_keywords='образование, курсы, дети, развитие',
                meta_author='Educational Platform',
                welcome_text='Добро пожаловать на нашу образовательную платформу! Мы рады видеть вас.',
                terms_of_service='''
Условия использования сервиса

1. Общие положения
1.1. Настоящие Условия использования определяют порядок использования образовательной платформы.
1.2. Используя наш сервис, вы соглашаетесь с данными условиями.

2. Регистрация и использование
2.1. Для использования сервиса необходима регистрация через Telegram.
2.2. Вы обязуетесь предоставлять достоверную информацию при регистрации.

3. Образовательные услуги
3.1. Платформа предоставляет доступ к образовательным курсам и материалам.
3.2. Мы оставляем за собой право изменять содержание курсов.

4. Конфиденциальность
4.1. Мы обеспечиваем защиту ваших персональных данных.
4.2. Подробная информация содержится в Политике конфиденциальности.

5. Ответственность
5.1. Мы не несем ответственности за технические сбои.
5.2. Пользователи несут ответственность за свои действия на платформе.
''',
                privacy_policy='''
Политика конфиденциальности

1. Общие положения
1.1. Настоящая Политика конфиденциальности определяет порядок обработки персональных данных пользователей.
1.2. Используя наш сервис, вы соглашаетесь с условиями данной политики.

2. Собираемые данные
2.1. Мы собираем следующую информацию:
- Telegram ID
- Имя и фамилию
- Контактные данные
- Информацию о детях (возраст, интересы)

3. Использование данных
3.1. Собранные данные используются для:
- Предоставления образовательных услуг
- Улучшения качества сервиса
- Связи с пользователями
- Аналитики и статистики

4. Защита данных
4.1. Мы применяем современные методы защиты персональных данных.
4.2. Доступ к данным имеют только авторизованные сотрудники.

5. Права пользователей
5.1. Вы имеете право:
- Получать информацию об обработке ваших данных
- Требовать исправления или удаления данных
- Отзывать согласие на обработку данных
''',
                robots_txt='User-agent: *\nAllow: /'
            )
            db.session.add(settings)
            db.session.commit()
        return settings

class NewsCategory(db.Model):
    __tablename__ = 'news_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Update relationship to include cascade
    news = db.relationship('News', back_populates='category', lazy=True, 
                         cascade='all, delete-orphan')

    def __repr__(self):
        return f'<NewsCategory {self.name}>'

class NewsTag(db.Model):
    __tablename__ = 'news_tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<NewsTag {self.name}>'

# Таблица для связи many-to-many между новостями и тегами
news_tags = db.Table('news_tags_association',
    db.Column('news_id', db.Integer, db.ForeignKey('news.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('news_tags.id', ondelete='CASCADE'), primary_key=True)
)

class News(db.Model):
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    author_id = db.Column(db.Integer, nullable=False)
    is_admin_author = db.Column(db.Boolean, default=False)
    # Make category_id nullable and add ondelete cascade
    category_id = db.Column(db.Integer, db.ForeignKey('news_categories.id', ondelete='SET NULL'), nullable=True)
    views_count = db.Column(db.Integer, default=0)

    # Keep existing relationships
    comments = db.relationship('NewsComment', backref='news', lazy=True, cascade='all, delete-orphan')
    images = db.relationship('NewsImage', backref='news', lazy=True, cascade='all, delete-orphan')
    tags = db.relationship('NewsTag', secondary='news_tags_association', lazy='subquery',
                         backref=db.backref('news', lazy=True))
    category = db.relationship('NewsCategory', back_populates='news')

    @property
    def formatted_content(self):
        """Returns the BB-code formatted content"""
        return parse_bbcode(self.content)

    @property
    def can_edit(self):
        """Check if current user can edit the news post"""
        if not current_user.is_authenticated:
            return False
        if self.is_admin_author:
            return current_user.is_admin
        return current_user.id == self.author_id

    @property
    def display_author(self):
        """Returns the proper author object based on whether it's an admin or regular user"""
        if self.is_admin_author:
            author = Admin.query.get(self.author_id)
            if author:
                return author
        else:
            author = User.query.get(self.author_id)
            if author:
                return author
        return None

    @property
    def author(self):
        """Returns the author object with proper admin check"""
        return self.display_author

class NewsComment(db.Model):
    __tablename__ = 'news_comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    author_id = db.Column(db.Integer, nullable=False)
    is_admin_author = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('news_comments.id'), nullable=True)

    # Relationships
    replies = db.relationship('NewsComment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    @property
    def formatted_content(self):
        """Returns the BB-code formatted content"""
        return parse_bbcode(self.content)

    @property
    def can_edit(self):
        """Check if current user can edit the comment"""
        if not current_user.is_authenticated:
            return False
        if self.is_admin_author:
            return current_user.is_admin
        return current_user.id == self.author_id

    @property
    def author(self):
        """Returns the author object (Admin or User)"""
        if self.is_admin_author:
            return Admin.query.get(self.author_id)
        return User.query.get(self.author_id)

    @property
    def author_display_name(self):
        """Returns the author's display name with admin prefix if applicable"""
        author = self.author
        if not author:
            return "Удаленный пользователь"
        name = author.username or author.first_name or "Аноним"
        return name

class NewsImage(db.Model):
    __tablename__ = 'news_images'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)

    url = db.Column(db.String(255))


    def delete_file(self):
        """Delete the physical image file"""
        try:
            os.remove(f"static/uploads/news/{self.filename}")
            return True
        except Exception as e:
            return False