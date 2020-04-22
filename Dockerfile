FROM python:3.6-alpine3.7

ENV WORKDIR /home/app
WORKDIR $WORKDIR

RUN apk update && apk add alpine-sdk postgresql-dev

RUN pip install --upgrade pip
RUN pip install pipenv
RUN pip install gunicorn
RUN pip install gevent==1.4.0
RUN pip install psycopg2-binary

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --system

COPY . .

RUN chmod +x ./entrypoint.sh
ENTRYPOINT [ "./entrypoint.sh" ]