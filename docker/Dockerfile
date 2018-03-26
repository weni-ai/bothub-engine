FROM python:3.6-alpine

ENV WORKDIR /home/app
WORKDIR $WORKDIR

RUN apk update && apk upgrade
RUN apk add alpine-sdk postgresql-dev
RUN pip install gunicorn

COPY . .
RUN pip install --exists-action w -r requirements.txt
RUN pip install gunicorn

RUN chmod +x ./docker/entrypoint.sh
EXPOSE 8000
ENTRYPOINT $WORKDIR/docker/entrypoint.sh