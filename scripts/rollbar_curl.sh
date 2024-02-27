#!/bin/bash
set -e

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


echo "Rollbar уведомлён о деплое"

