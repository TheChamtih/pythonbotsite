# Инструкция по развертыванию Algoritmika на VPS

## Подготовка системы

1. Обновите систему:
```bash
sudo apt update && sudo apt upgrade -y
```

2. Установите необходимые пакеты:
```bash
sudo apt install -y python3-venv python3-pip postgresql nginx git
```

3. Создайте пользователя:
```bash
sudo useradd -m -s /bin/bash algoritmika
sudo usermod -aG sudo algoritmika
```

## Настройка PostgreSQL

1. Создайте базу данных и пользователя:
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE algoritmika;
CREATE USER algoritmika WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE algoritmika TO algoritmika;
\q
```

## Развертывание приложения

1. Клонируйте репозиторий:
```bash
sudo mkdir /opt/algoritmika
sudo chown algoritmika:algoritmika /opt/algoritmika
cd /opt/algoritmika
git clone <your-repo-url> .
```

2. Создайте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Создайте файл с переменными окружения:
```bash
sudo nano /etc/algoritmika.env
```

Добавьте следующие переменные:
```
DATABASE_URL=postgresql://algoritmika:your_secure_password@localhost/algoritmika
SESSION_SECRET=your_secure_session_secret
BOT_TOKEN=your_telegram_bot_token
```

4. Настройте Nginx:
```bash
sudo nano /etc/nginx/sites-available/algoritmika
```

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/algoritmika /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

5. Установите systemd сервисы:
```bash
sudo cp deployment/algoritmika-web.service /etc/systemd/system/
sudo cp deployment/algoritmika-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable algoritmika-web algoritmika-bot
sudo systemctl start algoritmika-web algoritmika-bot
```

## Проверка работоспособности

1. Проверьте статус сервисов:
```bash
sudo systemctl status algoritmika-web
sudo systemctl status algoritmika-bot
```

2. Проверьте логи:
```bash
sudo journalctl -u algoritmika-web -f
sudo journalctl -u algoritmika-bot -f
```

## Обновление приложения

1. Остановите сервисы:
```bash
sudo systemctl stop algoritmika-web algoritmika-bot
```

2. Обновите код:
```bash
cd /opt/algoritmika
git pull
```

3. Обновите зависимости:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

4. Запустите сервисы:
```bash
sudo systemctl start algoritmika-web algoritmika-bot
```

## Резервное копирование

1. Создайте скрипт для резервного копирования базы данных:
```bash
sudo nano /opt/algoritmika/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/algoritmika/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
pg_dump -U algoritmika algoritmika > $BACKUP_DIR/backup_$TIMESTAMP.sql
```

2. Настройте автоматическое резервное копирование:
```bash
sudo chmod +x /opt/algoritmika/backup.sh
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/algoritmika/backup.sh") | crontab -
```
