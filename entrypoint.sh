#!/bin/sh
cd $WORKDIR
python manage.py collectstatic --noinput

if [ "$RUN_AS_DEVELOPMENT_MODE" = true -o "$RUN_AS_DEVELOPMENT_MODE" = "True" ]
then
    python3 manage.py runserver 0.0.0.0:80
else
    gunicorn bothub.wsgi --timeout 999999 -c gunicorn.conf.py
fi