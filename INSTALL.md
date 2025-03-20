# Инструкция по установке проекта на Ubuntu 22.04 VPS

## Содержание
1. [Требования к системе](#требования-к-системе)
2. [Подготовка системы](#подготовка-системы)
3. [Установка проекта](#установка-проекта)
4. [Настройка базы данных](#настройка-базы-данных)
5. [Настройка переменных окружения](#настройка-переменных-окружения)
6. [Настройка веб-сервера](#настройка-веб-сервера)
7. [Настройка SSL](#настройка-ssl)
8. [Запуск сервисов](#запуск-сервисов)
9. [Backup и восстановление](#backup-и-восстановление)

## Требования к системе
- Ubuntu 22.04 LTS
- Минимум 2 ГБ RAM
- Минимум 20 ГБ свободного места на диске
- Публичный IP адрес
- Доменное имя (для SSL)

## Подготовка системы

1. Обновление системы:
```bash
sudo apt update
sudo apt upgrade -y
```

2. Установка необходимых пакетов:
```bash
sudo apt install -y python3-pip python3-venv postgresql nginx certbot python3-certbot-nginx git
```

3. Создание пользователя:
```bash
sudo useradd -m -s /bin/bash algoritmika
sudo usermod -aG sudo algoritmika
```

## Установка проекта

1. Клонирование репозитория:
```bash
sudo -u algoritmika git clone [URL_репозитория] /opt/algoritmika
cd /opt/algoritmika
```

2. Создание виртуального окружения:
```bash
sudo -u algoritmika python3 -m venv venv
source venv/bin/activate
```

3. Установка зависимостей:
```bash
pip install -r requirements.txt
```

## Настройка базы данных

1. Настройка PostgreSQL:
```bash
sudo -u postgres psql -c "CREATE DATABASE algoritmika;"
sudo -u postgres psql -c "CREATE USER algoritmika WITH PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE algoritmika TO algoritmika;"
```

2. Настройка доступа:
```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```
Добавить строку:
```
host    algoritmika     algoritmika     127.0.0.1/32            md5
```

3. Перезапуск PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Настройка переменных окружения

1. Создание файла окружения:
```bash
sudo -u algoritmika nano /opt/algoritmika/.env
```

2. Добавить следующие переменные:
```
DATABASE_URL=postgresql://algoritmika:your_secure_password@localhost/algoritmika
SESSION_SECRET=your_secure_session_secret
BOT_TOKEN=your_telegram_bot_token
MAIN_ADMIN_ID=your_telegram_id
```

## Настройка веб-сервера

1. Настройка Nginx:
```bash
sudo nano /etc/nginx/sites-available/algoritmika
```

2. Добавить конфигурацию:
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/algoritmika/static;
        expires 30d;
    }
}
```

3. Активация конфигурации:
```bash
sudo ln -s /etc/nginx/sites-available/algoritmika /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Настройка SSL

1. Получение SSL сертификата:
```bash
sudo certbot --nginx -d your_domain.com
```

2. Настройка автообновления:
```bash
sudo systemctl status certbot.timer
```

## Запуск сервисов

1. Копирование файлов служб:
```bash
sudo cp /opt/algoritmika/deployment/algoritmika-web.service /etc/systemd/system/
sudo cp /opt/algoritmika/deployment/algoritmika-bot.service /etc/systemd/system/
```

2. Перезагрузка systemd:
```bash
sudo systemctl daemon-reload
```

3. Запуск служб:
```bash
sudo systemctl enable algoritmika-web algoritmika-bot
sudo systemctl start algoritmika-web algoritmika-bot
```

4. Проверка статуса:
```bash
sudo systemctl status algoritmika-web
sudo systemctl status algoritmika-bot
```

## Backup и восстановление

1. Настройка автоматического backup базы данных:
```bash
sudo -u algoritmika nano /opt/algoritmika/backup.sh
```

2. Добавить скрипт backup:
```bash
#!/bin/bash
BACKUP_DIR="/opt/algoritmika/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Создание директории для backup если она не существует
mkdir -p $BACKUP_DIR

# Backup базы данных
PGPASSWORD=your_secure_password pg_dump -U algoritmika -h localhost algoritmika > $BACKUP_FILE

# Сжатие backup
gzip $BACKUP_FILE

# Удаление старых backup (оставляем только последние 7 дней)
find $BACKUP_DIR -type f -name "backup_*.sql.gz" -mtime +7 -delete
```

3. Настройка прав и расписания:
```bash
sudo chmod +x /opt/algoritmika/backup.sh
sudo chown algoritmika:algoritmika /opt/algoritmika/backup.sh

# Добавление в crontab
sudo -u algoritmika crontab -e
```

4. Добавить строку для ежедневного backup в 3:00:
```
0 3 * * * /opt/algoritmika/backup.sh
```

### Восстановление из backup:
```bash
# Разархивация backup
gunzip backup_YYYYMMDD_HHMMSS.sql.gz

# Восстановление базы данных
PGPASSWORD=your_secure_password psql -U algoritmika -h localhost algoritmika < backup_YYYYMMDD_HHMMSS.sql
```

## Мониторинг и логи

1. Просмотр логов веб-приложения:
```bash
sudo journalctl -u algoritmika-web -f
```

2. Просмотр логов бота:
```bash
sudo journalctl -u algoritmika-bot -f
```

3. Просмотр логов Nginx:
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Безопасность

1. Настройка файрвола:
```bash
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

2. Регулярное обновление системы:
```bash
sudo apt update
sudo apt upgrade -y
```

3. Настройка автоматических обновлений безопасности:
```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Устранение неполадок

### Проблема: Сервис не запускается
1. Проверить логи:
```bash
sudo journalctl -u algoritmika-web -n 50
```

2. Проверить конфигурацию:
```bash
sudo nginx -t
```

3. Проверить права доступа:
```bash
sudo chown -R algoritmika:algoritmika /opt/algoritmika
```

### Проблема: Ошибка подключения к базе данных
1. Проверить статус PostgreSQL:
```bash
sudo systemctl status postgresql
```

2. Проверить доступность базы:
```bash
psql -U algoritmika -h localhost -d algoritmika
```

### Проблема: Сертификат SSL не обновляется
1. Проверить статус certbot:
```bash
sudo systemctl status certbot.timer
```

2. Попробовать обновить вручную:
```bash
sudo certbot renew --dry-run
```

## Дополнительные рекомендации

1. Регулярно проверяйте:
   - Использование диска: `df -h`
   - Использование памяти: `free -m`
   - Нагрузку на CPU: `top` или `htop`

2. Настройте мониторинг:
   - Установите Prometheus + Grafana
   - Настройте оповещения о критических событиях

3. Создайте план действий при сбоях:
   - Документируйте все изменения конфигурации
   - Храните backup в безопасном месте
   - Имейте план восстановления системы
