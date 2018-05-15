#!/bin/sh
git clone --branch $WEBAPP_BRANCH --depth 1 https://github.com/push-flow/bothub-webapp /tmp/bothub-webapp/
cd /tmp/bothub-webapp/ && npm install && npm run build

cd $WORKDIR
python manage.py migrate
python manage.py collectstatic --noinput

gunicorn -e DJANGO_SETTINGS_MODULE=bothub.settings -b unix:/tmp/bothub.sock -D bothub.wsgi

mkdir -p /run/nginx/
nginx -g "daemon off;"
