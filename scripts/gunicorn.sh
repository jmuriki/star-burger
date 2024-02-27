#!/bin/bash

python manage.py migrate
gunicorn -w 3 -b 0.0.0.0:8080 star_burger.wsgi:application
