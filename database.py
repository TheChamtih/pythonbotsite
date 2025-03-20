import os
import psycopg2
from psycopg2.extras import DictCursor
from config import MAIN_ADMIN_ID

DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://mybotuser:260276mkM@localhost:5432/mybotdb")


def get_connection():
    """Returns a database connection."""
    return psycopg2.connect(
        DATABASE_URL,
        client_encoding='UTF8'
    )


def init_courses():
    """Инициализация курсов при первом запуске."""
    conn = get_connection()
    cursor = conn.cursor()

    # Проверяем, есть ли уже курсы
    cursor.execute('SELECT COUNT(*) FROM courses')
    if cursor.fetchone()[0] == 0:
        courses = [
            (9, 'Геймдизайн', '🎮 Создание игр и игровых миров. Развиваем воображение и технические навыки!', 10, 11, 0, 0),
            (10, 'Математика', '🧮 Углубленное изучение математики для школьников. Подготовка к олимпиадам и экзаменам!', 6, 13, 0, 0),
            (7, 'Видеоблогинг', '🎥 Как создавать и продвигать видеоконтент. Стань звездой YouTube!', 9, 11, 0, 0),
            (2, 'Компьютерная грамотность', '💻 Освойте основы работы с компьютером. Навыки, которые пригодятся каждому!', 7, 9, 0, 0),
            (3, 'Создание веб-сайтов', '🌐 Научим создавать современные веб-сайты с нуля. От HTML до CSS и JavaScript!', 11, 13, 0, 0),
            (5, 'Визуальное программирование', '🖥️ Программирование через визуальные блоки. Идеально для детей!', 9, 10, 0, 0),
            (8, 'Фронтенд-разработка', '🖥️ Курс по созданию интерфейсов для веб-сайтов. Освой HTML, CSS и JavaScript!', 15, 18, 0, 0),
            (11, 'Предпринимательство', '💼 Основы бизнеса и предпринимательства для детей. Как превратить идею в успешный проект!', 13, 16, 0, 0),
            (6, 'Python', '🐍 Изучение языка программирования Python. От основ до создания реальных проектов!', 12, 17, 0, 0),
            (1, 'Основы логики и программирования', '🧠 Развиваем логическое мышление и изучаем основы программирования. Идеально для начинающих!', 6, 7, 0, 0),
            (12, 'Подготовка к ЕГЭ', '📚 Подготовка к ЕГЭ по математике и информатике. Максимальные баллы гарантированы!', 17, 18, 0, 0),
            (4, 'Графический дизайн', '🎨 Курс по созданию графики и дизайну. Развиваем креативность и художественный вкус!', 9, 14, 0, 0)
        ]

        for course in courses:
            cursor.execute('''
                INSERT INTO courses (id, name, description, min_age, max_age, rating, rating_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', course)

        conn.commit()

    conn.close()


def init_db():
    """Инициализация базы данных."""
    conn = get_connection()
    cursor = conn.cursor()

    # Устанавливаем кодировку для сессии
    cursor.execute("SET client_encoding TO 'UTF8';")

    # Таблица для районов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS districts (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Таблица для пользователей с правильной структурой
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT NOT NULL,
            parent_name TEXT,
            phone TEXT,
            child_name TEXT NOT NULL,
            child_age INTEGER NOT NULL,
            child_interests TEXT
        )
    ''')

    # Таблица для курсов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            min_age INTEGER NOT NULL,
            max_age INTEGER NOT NULL,
            duration VARCHAR(100),
            schedule TEXT,
            price VARCHAR(100),
            skills TEXT,
            requirements TEXT,
            rating FLOAT DEFAULT 0,
            rating_count INTEGER DEFAULT 0
        )
    ''')

    # Таблица для локаций
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id SERIAL PRIMARY KEY,
            district_id INTEGER NOT NULL REFERENCES districts(id),
            address TEXT NOT NULL
        )
    ''')

    # Таблица для записей на пробные занятия
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trial_lessons (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            location_id INTEGER NOT NULL,
            date TIMESTAMP NOT NULL,
            confirmed BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id),
            FOREIGN KEY (location_id) REFERENCES locations(id)
        )
    ''')

    # Таблица для администраторов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL,
            username VARCHAR(120),
            first_name VARCHAR(120),
            last_name VARCHAR(120)
        )
    ''')

    # Таблица для тегов курсов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS course_tags (
            id SERIAL PRIMARY KEY,
            course_id INTEGER REFERENCES courses(id),
            tag VARCHAR(50) NOT NULL
        )
    ''')

    # Таблица для отзывов о курсах
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS course_reviews (
            id SERIAL PRIMARY KEY,
            course_id INTEGER REFERENCES courses(id),
            user_id INTEGER REFERENCES users(id),
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Добавляем главного администратора, если его нет
    cursor.execute('SELECT COUNT(*) FROM admins WHERE telegram_id = %s',
                   (MAIN_ADMIN_ID,))
    if cursor.fetchone()[0] == 0:
        # Создаем временный email на основе telegram_id
        temp_email = f"admin_{MAIN_ADMIN_ID}@codecreate.tech"
        cursor.execute('''
            INSERT INTO admins (telegram_id, email, username, first_name) 
            VALUES (%s, %s, %s, %s)
        ''', (MAIN_ADMIN_ID, temp_email, 'MainAdmin', 'Admin'))

    # Добавляем базовые районы, если их нет
    cursor.execute('SELECT COUNT(*) FROM districts')
    if cursor.fetchone()[0] == 0:
        districts = [
            ('Выя',),
            ('Центр',),
            ('ГГМ',),
            ('Вагонка',)
        ]
        for district in districts:
            cursor.execute(
                'INSERT INTO districts (name) VALUES (%s)',
                district)

    # Добавляем тестовые локации, если их нет
    cursor.execute('SELECT COUNT(*) FROM locations')
    if cursor.fetchone()[0] == 0:
        # Сначала получаем ID районов
        cursor.execute('SELECT id, name FROM districts')
        district_ids = {row[1]: row[0] for row in cursor.fetchall()}

        locations = [
            (district_ids['Выя'], "ул. Черных, д. 23"),
            (district_ids['Центр'], "просп. Мира, д. 49 (этаж 3)"),
            (district_ids['ГГМ'], "ул. Захарова, д. 10А"),
            (district_ids['Вагонка'], "ул. Володарского, д. 1")
        ]
        for location in locations:
            cursor.execute(
                'INSERT INTO locations (district_id, address) VALUES (%s, %s)',
                location)

    # Добавляем вызов инициализации курсов
    init_courses()

    conn.commit()
    conn.close()


def get_admin_ids():
    """Возвращает список telegram_id администраторов."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT telegram_id FROM admins')
    admins = [row[0] for row in cursor.fetchall()]
    conn.close()
    return admins


def add_admin(telegram_id: int):
    """Добавляет администратора."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO admins (telegram_id) VALUES (%s)', (telegram_id, ))
    conn.commit()
    conn.close()


def get_locations():
    """Возвращает список всех локаций."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, district, address FROM locations')
    locations = cursor.fetchall()
    conn.close()
    return locations


def get_location_by_id(location_id: int):
    """Возвращает информацию о локации по ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            d.name as district_name,
            l.address
        FROM locations l
        JOIN districts d ON l.district_id = d.id
        WHERE l.id = %s
    ''', (location_id,))
    location = cursor.fetchone()
    conn.close()
    return location if location else None