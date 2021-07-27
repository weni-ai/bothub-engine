#!/bin/sh
cd $WORKDIR
python manage.py collectstatic --noinput

python manage.py search_index --rebuild -f

gunicorn bothub.wsgi --timeout 999999 -c gunicorn.conf.py
