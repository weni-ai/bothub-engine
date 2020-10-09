FROM python:3.6-alpine3.7

ENV WORKDIR /home/app
WORKDIR $WORKDIR

RUN apk update && apk add alpine-sdk postgresql-dev

RUN pip install -U pip==20.2.2 setuptools==49.6.0
RUN pip install pipenv==2018.11.26
RUN pip install gunicorn==19.9.0
RUN pip install gevent==1.4.0
RUN pip install psycopg2-binary
RUN apk add build-base python3-dev py-pip jpeg-dev zlib-dev gpgme-dev libc-dev gcc musl-dev libffi-dev openssl-dev
ENV LIBRARY_PATH=/lib:/usr/lib

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --system

COPY . .

RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]