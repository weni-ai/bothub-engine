FROM python:3.6-alpine3.7

ENV WORKDIR /home/app
WORKDIR $WORKDIR

RUN apk update && apk upgrade
RUN apk add alpine-sdk postgresql-dev

COPY . .
COPY ./docker/entrypoint.sh ./entrypoint.sh
COPY ./docker/gunicorn.conf.py ./gunicorn.conf.py

RUN pip install --exists-action w -r requirements.txt
RUN pip install gunicorn

RUN chmod +x ./entrypoint.sh
EXPOSE 8000
ENTRYPOINT $WORKDIR/entrypoint.sh