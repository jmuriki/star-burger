#!/bin/bash

set -e

cd /opt/star-burger_docker/

# Остановка текущего стэка
docker compose -f docker-compose_gunicorn.yaml down

# Cкачивание свежих образов из .yaml файлов
docker compose -f docker-compose_gunicorn.yaml pull

# Запуск стэка с prod-версией:
docker compose -f docker-compose_gunicorn.yaml up -d

# Перезапуск nginx
systemctl reload nginx.service

# Загрузка переменных окружения из файла .env
if [[ -f .env ]]; then
    source .env
fi

# Установка переменной с токеном доступа Rollbar
access_token=$ROLLBAR_ACCESS_TOKEN

# Получение хэша последнего коммита
commit_hash=$(docker inspect --format='{{index .Config.Labels "last_commit_hash"}}' jmuriki/star-burger_backend)

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

# Удаление отработавших контейнеров
# docker container prune -f

# Сообщение об успешном завершении деплоя
echo "Деплой успешно завершен!"
