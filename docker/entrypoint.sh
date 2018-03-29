#!/bin/sh
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn bothub.wsgi -c gunicorn.conf.py