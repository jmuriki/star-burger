#!/bin/bash

python manage.py migrate
cp -r /star-burger/staticfiles/* /var/www/static/
gunicorn -w 3 -b 0.0.0.0:8080 star_burger.wsgi:application
