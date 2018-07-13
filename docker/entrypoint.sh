#!/bin/sh
if [ ${BUILD_WEBAPP} == true ]; then
    git clone --branch $WEBAPP_BRANCH --depth 1 $WEBAPP_REPO /tmp/bothub-webapp/
    cd /tmp/bothub-webapp/ && npm install && npm run build
fi

cd $WORKDIR
python manage.py migrate
python manage.py collectstatic --noinput

GUNICORN_LOG_FILE="/var/log/gunicorn.log"
touch ${GUNICORN_LOG_FILE}
gunicorn bothub.wsgi -c docker/gunicorn.conf.py --log-file ${GUNICORN_LOG_FILE} --log-level debug --capture-output

mkdir -p /run/nginx/
nginx
tail -f /var/log/nginx/* ${GUNICORN_LOG_FILE}
