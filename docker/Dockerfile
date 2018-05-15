FROM python:3.6-alpine3.7

ENV WORKDIR /home/app
WORKDIR $WORKDIR

RUN apk update && apk upgrade
RUN apk add alpine-sdk postgresql-dev nodejs nginx

COPY ./requirements.txt ./requirements.txt

RUN pip install --exists-action w -r requirements.txt
RUN pip install gunicorn

COPY . .
COPY ./docker/bothub-nginx.conf /etc/nginx/conf.d/default.conf
COPY ./docker/entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh
EXPOSE 80
ENTRYPOINT $WORKDIR/entrypoint.sh