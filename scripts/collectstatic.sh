#!/bin/bash

cd /star-burger
python manage.py collectstatic --noinput
cp -r /star-burger/staticfiles/* /var/www/static/
