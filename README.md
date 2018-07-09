# Bothub

[![Build Status](https://travis-ci.org/Ilhasoft/bothub-engine.svg?branch=master)](https://travis-ci.org/Ilhasoft/bothub-engine) [![Coverage Status](https://coveralls.io/repos/github/Ilhasoft/bothub-engine/badge.svg?branch=master)](https://coveralls.io/github/Ilhasoft/bothub-engine?branch=master) [![Python Version](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/) [![License GPL-3.0](https://img.shields.io/badge/license-%20GPL--3.0-yellow.svg)](https://github.com/Ilhasoft/bothub-engine/blob/master/LICENSE)

## Development

Use ```make``` commands to ```check_environment```, ```install_requirements```, ```lint```, ```test```, ```migrate```, ```start``` and ```migrations```.

| Command | Description |
|--|--|
| make help | Show make commands help
| make check_environment | Check if all dependencies was installed
| make install_requirements | Install pip dependencies
| make lint | Show lint warnings and errors
| make test | Run unit tests and show coverage report
| make migrate | Update DB shema, apply migrations
| make start | Start development web server
| make migrations | Create DB migrations files


### Fill database using fake data

Run ```pipenv run python ./manage.py fill_db_using_fake_data``` to fill database using fake data. This can help you to test [Bothub Webapp](https://github.com/Ilhasoft/bothub-webapp).


#### Fake users infos:

| nickname | email | password | is superuser |
|---|---|---|---|
| admin | admin@bothub.it | admin | yes |
| douglas | douglas@bothub.it | douglas | no |
| user | user@bothub.it | user | no |


## Production

Docker images available in [Bothub's Docker Hub repository](https://hub.docker.com/r/ilha/bothub/).

## Environment Variables

You can set environment variables in your OS, write on ```.env``` file or pass via Docker config.

| Variable | Type | Default | Description |
|--|--|--|--|
| SECRET_KEY | ```string```|  ```None``` | A secret key for a particular Django installation. This is used to provide cryptographic signing, and should be set to a unique, unpredictable value.
| DEBUG | ```boolean``` | ```False``` | A boolean that turns on/off debug mode.
| ALLOWED_HOSTS | ```string``` | ```*``` | A list of strings representing the host/domain names that this Django site can serve.
| DEFAULT_DATABASE | ```string``` | ```sqlite:///db.sqlite3``` | Read [dj-database-url](https://github.com/kennethreitz/dj-database-url) to configure the database connection.
| LANGUAGE_CODE | ```string``` | ```en-us``` | A string representing the language code for this installation.This should be in standard [language ID format](https://docs.djangoproject.com/en/2.0/topics/i18n/#term-language-code).
| TIME_ZONE | ```string``` | ```UTC``` | A string representing the time zone for this installation. See the [list of time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
| STATIC_URL | ```string``` | ```/static/``` | URL to use when referring to static files located in ```STATIC_ROOT```.
| EMAIL_HOST | ```string``` | ```None``` | The host to use for sending email. When setted to ```None``` and ```DEBUG``` is ```True```, the ```EMAIL_BACKEND``` setting is setted to ```django.core.mail.backends.console.EmailBackend```
| EMAIL_PORT | ```int``` | ```25``` | Port to use for the SMTP server defined in ```EMAIL_HOST```.
| DEFAULT_FROM_EMAIL | ```string``` | ```webmaster@localhost``` | Default email address to use for various automated correspondence from the site manager(s).
| SERVER_EMAIL | ```string``` | ```root@localhost``` | The email address that error messages come from, such as those sent to ```ADMINS``` and ```MANAGERS```.
| EMAIL_HOST_USER | ```string``` | ```''``` | Username to use for the SMTP server defined in ```EMAIL_HOST```.
| EMAIL_HOST_PASSWORD | ```string``` | ```''``` | Password to use for the SMTP server defined in ```EMAIL_HOST```.
| EMAIL_USE_SSL | ```boolean``` | ```False``` | Whether to use an implicit TLS (secure) connection when talking to the SMTP server.
| EMAIL_USE_TLS | ```boolean``` | ```False``` | Whether to use a TLS (secure) connection when talking to the SMTP server.
| ADMINS | ```string``` | ```''``` | A list of all the people who get code error notifications. Follow the pattern: ```admin1@email.com\|Admin 1,admin2@email.com\|Admin 2```
| CSRF_COOKIE_DOMAIN | ```string``` | ```None``` | The domain to be used when setting the CSRF cookie.
| CSRF_COOKIE_SECURE | ```boolean``` | ```False``` | Whether to use a secure cookie for the CSRF cookie.
| BOTHUB_WEBAPP_BASE_URL | ```string``` | ```http://localhost:8080/``` | The bothub-webapp production application URL. Used to refer and redirect user correctly.
| BOTHUB_NLP_BASE_URL | ```string``` | ```http://localhost:8001/``` | The bothub-blp production application URL. Used to proxy requests.
| SUPPORTED_LANGUAGES | ```string```| ```en|pt``` | Set supported languages. Separe languages using ```|```. You can set location follow the format: ```[LANGUAGE_CODE]:[LANGUAGE_LOCATION]```.


### Docker Environment Variables

| Variable | Type | Default | Description |
|--|--|--|--|
| WEBAPP_REPO | ```string``` | ```https://github.com/Ilhasoft/bothub-webapp``` | bothub-webapp git repository URL. It will clone and run ```npm install && npm run build``` command on the entrypoint. This build is served by Nginx.
| WEBAPP_BRANCH | ```string``` | ```master``` | Specify the branch of the bothub-webapp Git repository.
| API_BASE_URL | ```string``` | Not defined | The bothub production application URL. Used by ```bothub-webapp``` application.
