#!/bin/bash

if [ "$COMMAND" = "runserver" ]; then
    python manage.py migrate
	python manage.py runserver 0.0.0.0:8000

elif [ "$COMMAND" = "gunicorn" ]; then
    python manage.py migrate
    cp -r /star-burger/staticfiles/* /var/www/static/
	gunicorn -w 3 -b 0.0.0.0:8080 star_burger.wsgi:application

else
    echo "Неверная команда."
fi
