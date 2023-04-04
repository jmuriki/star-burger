#!/bin/bash
set -e

cd /opt/starburger/star-burger/

# Обновление кода репозитория
git pull

# Активация виртуального окружения
source /opt/starburger/bin/activate

# Установка библиотек для Python
pip install -r requirements.txt

# Установка библиотек для Node.js
npm ci --dev

# Пересборка статики Django
python manage.py collectstatic --noinput

# Накат миграций
python manage.py migrate

# Перезапуск сервисов Systemd
systemctl restart star-burger_node.service
systemctl restart star-burger_gunicorn.service
systemctl reload nginx.service

# Сообщение об успешном завершении деплоя
echo "Деплой успешно завершен!"
