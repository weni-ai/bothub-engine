FROM python:3.6-alpine3.7

ENV WORKDIR /home/app
WORKDIR $WORKDIR

RUN apk update && apk upgrade
RUN apk add alpine-sdk postgresql-dev nodejs nginx

RUN pip install pipenv
RUN pip install gunicorn
RUN pip install psycopg2-binary

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --system --dev

COPY . .
COPY ./docker/bothub-nginx.conf /etc/nginx/conf.d/default.conf
COPY ./docker/entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh
EXPOSE 80
ENTRYPOINT $WORKDIR/entrypoint.sh