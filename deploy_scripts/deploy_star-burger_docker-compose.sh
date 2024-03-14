#!/bin/bash

set -e

cd /opt/star-burger_docker/docker-compose/

# Остановка текущего стэка
docker compose -f docker-compose_gunicorn.yaml down

# Cкачивание свежих образов из .yaml файлов
docker compose -f docker-compose_gunicorn.yaml pull

# Запуск стэка с prod-версией:
docker compose -f docker-compose_gunicorn.yaml up -d

# Удаление отработавшего контейнера
IMAGE_NAME="jmuriki/star-burger_frontend"
CONTAINER_IDS=$(docker container ls -aqf "ancestor=$IMAGE_NAME" --filter "status=exited")

if [ -n "$CONTAINER_IDS" ]; then
    docker container rm $CONTAINER_IDS
    echo "Неработающие контейнеры на основе образа $IMAGE_NAME удалены."
else
    echo "Неработающих контейнеров на основе образа $IMAGE_NAME не найдено."
fi

# Перезапуск nginx
systemctl reload nginx.service

cd ../backend

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

# Сообщение об успешном завершении деплоя
echo "Деплой успешно завершен!"
