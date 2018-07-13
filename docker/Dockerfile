FROM python:3.6-alpine3.7

ENV WORKDIR /home/app
WORKDIR $WORKDIR

RUN apk update && apk upgrade && apk add alpine-sdk postgresql-dev nginx && \
pip install pipenv gunicorn

COPY . .

RUN mv ${WORKDIR}/docker/entrypoint.sh ./entrypoint && \
mv docker/nginx.conf /etc/nginx/conf.d/default.conf && \
pipenv install --system --deploy && \
mkdir /run/nginx

COPY ./docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY ./docker/entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh && rm -rf docker
EXPOSE 8000
ENTRYPOINT $WORKDIR/entrypoint.sh
