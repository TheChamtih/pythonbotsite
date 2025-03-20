#!/bin/bash

# Проверка прав суперпользователя
if [ "$EUID" -ne 0 ]; then 
  echo "Пожалуйста, запустите скрипт с правами суперпользователя (sudo)"
  exit 1
fi

# Обновление системы
echo "Обновление системы..."
apt update && apt upgrade -y

# Установка необходимых пакетов
echo "Установка необходимых пакетов..."
apt install -y python3-pip postgresql nginx git gunicorn

# Создание пользователя
echo "Создание пользователя algoritmika..."
useradd -m -s /bin/bash algoritmika
usermod -aG sudo algoritmika

# Создание и настройка директорий
echo "Создание и настройка директорий..."
mkdir -p /opt/algoritmika
mkdir -p /var/log/algoritmika
chown -R algoritmika:algoritmika /opt/algoritmika /var/log/algoritmika
chmod -R 755 /opt/algoritmika /var/log/algoritmika

# Настройка PostgreSQL
echo "Настройка PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE algoritmika;"
sudo -u postgres psql -c "CREATE USER algoritmika WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE algoritmika TO algoritmika;"

# Установка Python пакетов глобально
echo "Установка Python пакетов..."
pip3 install flask flask-sqlalchemy flask-login gunicorn psycopg2-binary python-telegram-bot==13.7 flask-wtf

# Создание файла с переменными окружения
echo "Создание файла с переменными окружения..."
cat > /opt/algoritmika/.env << EOL
DATABASE_URL=postgresql://algoritmika:your_secure_password@localhost/algoritmika
SESSION_SECRET=your_secure_session_secret
BOT_TOKEN=your_telegram_bot_token
MAIN_ADMIN_ID=your_telegram_id
EOL

# Установка прав на файл с переменными окружения
chown algoritmika:algoritmika /opt/algoritmika/.env
chmod 600 /opt/algoritmika/.env

# Загрузка переменных окружения в systemd
echo "Настройка переменных окружения в systemd..."
mkdir -p /etc/systemd/system/algoritmika-web.service.d/
cat > /etc/systemd/system/algoritmika-web.service.d/override.conf << EOL
[Service]
EnvironmentFile=/opt/algoritmika/.env
EOL

# Копирование и настройка systemd сервисов
echo "Настройка systemd сервисов..."
cp /opt/algoritmika/deployment/algoritmika-web.service /etc/systemd/system/
cp /opt/algoritmika/deployment/algoritmika-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable algoritmika-web algoritmika-bot
systemctl start algoritmika-web algoritmika-bot

echo "Базовая настройка завершена."
echo "Проверьте статус сервисов командами:"
echo "sudo systemctl status algoritmika-web"
echo "sudo systemctl status algoritmika-bot"
echo "sudo journalctl -u algoritmika-web -f"