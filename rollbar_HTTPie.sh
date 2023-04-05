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

# Активация виртуального окружения
source /opt/starburger/bin/activate

# Проверка наличия установленного HTTPie
if ! command -v http >/dev/null 2>&1; then
    echo "HTTPie не найден, выполняется установка..."
    pip install httpie
fi

# Отправка запроса на API Rollbar с информацией о деплое
http POST https://api.rollbar.com/api/1/deploy/ \
     Content-Type:application/json \
     access_token="$access_token" \
     environment="production" \
     revision="$commit_hash" \
     rollbar_name="jmuriki" \
     local_username="jmuriki-root" \
     comment="Комментарий" \
     status="succeeded"

echo "Rollbar уведомлён о деплое"

