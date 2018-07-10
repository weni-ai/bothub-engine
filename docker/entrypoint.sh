#!/bin/sh
if [ ${BUILD_WEBAPP} ]; then
    git clone --branch $WEBAPP_BRANCH --depth 1 $WEBAPP_REPO /tmp/bothub-webapp/
    cd /tmp/bothub-webapp/ && npm install && npm run build
fi

cd $WORKDIR
python manage.py migrate
python manage.py collectstatic --noinput

gunicorn -e DJANGO_SETTINGS_MODULE=bothub.settings -b unix:/tmp/bothub.sock -D bothub.wsgi --log-file /var/log/gunicorn.log --log-level debug --capture-output

mkdir -p /run/nginx/
nginx
tail -f /var/log/nginx/* /var/log/gunicorn.log
