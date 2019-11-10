#!/bin/sh
cd $WORKDIR
python manage.py migrate
python manage.py collectstatic --noinput

gunicorn bothub.wsgi --timeout 360 -c gunicorn.conf.py
