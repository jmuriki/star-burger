#!/bin/bash
set -e

cd /opt/star-burger/

# Обновление кода репозитория
git pull

# Выбор ветки
git checkout star-burger_Docker_lesson2

# Активация виртуального окружения
source /opt/star-burger/venv/bin/activate

# Установка библиотек для Python
pip install -r requirements.txt

# Установка библиотек для Node.js
npm ci --dev

# Пересборка фронтенда
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

# Пересборка статики Django
python manage.py collectstatic --noinput

# Накат миграций
python manage.py migrate --noinput

# Перезапуск сервисов Systemd
systemctl restart star-burger_node.service
systemctl restart star-burger_gunicorn.service
systemctl reload nginx.service

# Загрузка переменных окружения из файла .env
if [[ -f .env ]]; then
    source .env
fi

# Установка переменной с токеном доступа Rollbar
access_token=$ROLLBAR_ACCESS_TOKEN

# Получение хэша последнего коммита
commit_hash=$(git rev-parse HEAD)

# Отправка запроса на API Rollbar с информацией о деплое
curl -X POST https://api.rollbar.com/api/1/deploy/ \
     -H "Content-Type: application/json" \
     -H "X-Rollbar-Access-Token: $access_token" \
     -d '{
           "environment": "production",
           "revision": "'"$commit_hash"'",
           "rollbar_name": "jmuriki",
           "local_username": "jmuriki-root",
           "comment": "Комментарий",
           "status": "succeeded"
         }'

# Сообщение об успешном завершении деплоя
echo "Деплой успешно завершен!"
