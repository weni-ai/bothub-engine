#!/bin/sh

python manage.py migrate
python manage.py collectstatic --noinput

nginx && gunicorn bothub.wsgi --log-config /home/app/gunicorn-logging.conf -c /home/app/gunicorn.conf.py
