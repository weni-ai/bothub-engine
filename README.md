<p align="center">
  <img src="https://i.imgur.com/PKrSNGY.png" alt="BLACK LIVES MATTER" />

  <h3 align="center">BLACK LIVES MATTER</h3>

  <p align="center">
    <a href="https://blacklivesmatter.com/" target="_blank">Black Lives Matter</a>
    ·
    <a href="https://act.unicefusa.org/blm" target="_blank">Supporting the cause</a>
    ·
  </p>
</p>
    
<br />
<p align="center">
    <img src="https://user-images.githubusercontent.com/5360835/65427083-1af35900-de01-11e9-86ef-59f1eee79a68.png" width="230" height="70" alt="Bothub" />
</p>


# Bothub

[![Build Status](https://travis-ci.com/Ilhasoft/bothub-engine.svg?branch=master)](https://travis-ci.com/Ilhasoft/bothub-engine)
[![Coverage Status](https://coveralls.io/repos/github/bothub-it/bothub-engine/badge.svg?branch=master)](https://coveralls.io/github/bothub-it/bothub-engine?branch=master)
[![Code Climate](https://codeclimate.com/github/bothub-it/bothub-engine/badges/gpa.svg)](https://codeclimate.com/github/bothub-it/bothub-engine)
[![Python Version](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/)
[![License GPL-3.0](https://img.shields.io/badge/license-%20GPL--3.0-yellow.svg)](https://github.com/bothub-it/bothub-engine/blob/master/LICENSE)

# Requirements

* Python (3.6)
* Poetry
* Docker
* Docker-compose

## Development

Use ```make``` commands to ```check_environment```, ```install_requirements```, ```lint```, ```test```, ```migrate```, ```start```, ```migrations``` and ```collectstatic```.

| Command | Description |
|--|--|
| make help | Show make commands help
| make check_environment | Check if all dependencies was installed
| make install_requirements | Install pip dependencies
| make lint | Show lint warnings and errors
| make test | Run unit tests and show coverage report
| make migrate | Update DB shema, apply migrations
| make search_index | (Re)create and (re)populate the indices in Elasticsearch
| make start | Start development web server
| make start_celery | Start celery service
| make migrations | Create DB migrations files
| make collectstatic | Collects the static files into ```STATIC_ROOT```


### Fill database using fake data

Run ```poetry run python ./manage.py fill_db_using_fake_data``` to fill database using fake data. This can help you to test [Bothub Webapp](https://github.com/bothub-it/bothub-webapp).


### Migrate all training for aws

Run ```poetry run python ./manage.py transfer_train_aws``` Migrate all trainings to an aws bucket defined in project settings.


### Enable all repository to train

Run ```poetry run python ./manage.py enable_all_train```


### Start Train in all repositories

Run ```poetry run python ./manage.py start_all_repository_train```


#### Fake users infos:

| nickname | email | password | is superuser |
|---|---|---|---|
| admin | admin@bothub.it | admin | yes |
| user | user@bothub.it | user | no |


## Production

Docker images available in [Bothub's Docker Hub repository](https://hub.docker.com/r/ilha/bothub/).


# Deployment


## Heroku
Host your own Bothub Engine with [One-Click Deploy] (https://heroku.com/deploy).

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)



## Environment Variables

You can set environment variables in your OS, write on ```.env``` file or pass via Docker config.

| Variable | Type | Default | Description |
|--|--|--|--|
| SECRET_KEY | ```string```|  ```None``` | A secret key for a particular Django installation. This is used to provide cryptographic signing, and should be set to a unique, unpredictable value.
| DEBUG | ```boolean``` | ```False``` | A boolean that turns on/off debug mode.
| BASE_URL | ```string``` | ```http://api.bothub.it``` | URL Base Bothub Engine Backend.
| ALLOWED_HOSTS | ```string``` | ```*``` | A list of strings representing the host/domain names that this Django site can serve.
| DEFAULT_DATABASE | ```string``` | ```sqlite:///db.sqlite3``` | Read [dj-database-url](https://github.com/kennethreitz/dj-database-url) to configure the database connection.
| LANGUAGE_CODE | ```string``` | ```en-us``` | A string representing the language code for this installation.This should be in standard [language ID format](https://docs.djangoproject.com/en/2.0/topics/i18n/#term-language-code).
| TIME_ZONE | ```string``` | ```UTC``` | A string representing the time zone for this installation. See the [list of time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
| STATIC_URL | ```string``` | ```/static/``` | URL to use when referring to static files located in ```STATIC_ROOT```.
| EMAIL_HOST | ```string``` | ```None``` | The host to use for sending email. When setted to ```None``` or empty string, the ```EMAIL_BACKEND``` setting is setted to ```django.core.mail.backends.console.EmailBackend```
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
| SUPPORTED_LANGUAGES | ```string```| ```en|pt``` | Set supported languages. Separe languages using ```|```. You can set location follow the format: ```[LANGUAGE_CODE]:[LANGUAGE_LOCATION]```.
| BOTHUB_NLP_BASE_URL | ```string``` | ```http://localhost:2657/``` | The bothub-blp production application URL. Used to proxy requests.
| CHECK_ACCESSIBLE_API_URL | ```string``` | ```http://localhost/api/repositories/``` | URL used by ```bothub.health.check.check_accessible_api``` to make a HTTP request. The response status code must be 200.
| SEND_EMAILS | ```boolean``` | ```True``` | Send emails flag.
| BOTHUB_ENGINE_AWS_S3_BUCKET_NAME | ```string``` | ```None``` | Specify the bucket name to send to s3
| BOTHUB_ENGINE_AWS_ACCESS_KEY_ID | ```string``` | ```None``` | Specify the access key to send to s3
| BOTHUB_ENGINE_AWS_SECRET_ACCESS_KEY | ```string``` | ```None``` | Specify the secret access key to send to s3
| BOTHUB_ENGINE_AWS_REGION_NAME | ```string``` | ```None``` | Specify the region to send to s3
| BOTHUB_ENGINE_AWS_ENDPOINT_URL | ```string``` | ```None``` | Specify the endpoint to send to s3, if sending to amazon s3, there is no need to specify a value
| BOTHUB_ENGINE_AWS_SEND |  ```bool``` | ```False``` | Authorize sending to s3
| BOTHUB_BOT_EMAIL |  ```string``` | ```bot_repository@bothub.it``` | Email that the system will automatically create for existing repositories that the owner deleted the account
| BOTHUB_BOT_NAME |  ```string``` | ```Bot Repository``` | Name that the system will use to create the account
| BOTHUB_BOT_NICKNAME |  ```string``` | ```bot_repository``` | Nickname that the system will use to create the account
| BOTHUB_ENGINE_USE_SENTRY |  ```bool``` | ```False``` | Enable Support Sentry
| BOTHUB_ENGINE_SENTRY |  ```string``` | ```None``` | URL Sentry
| BOTHUB_NLP_RASA_VERSION |  ```string``` | ```1.4.3``` | Specify the version of rasa used in the nlp worker
| TOKEN_SEARCH_REPOSITORIES |  ```string``` | ```None``` | Specify the token to be used in the search_repositories_examples route, if not specified, the route is available without authentication
| GOOGLE_API_TRANSLATION_KEY |  ```string``` | ```None``` | Specify the Google Translation API passkey, used in machine translation
| APM_DISABLE_SEND |  ```bool``` | ```False``` | Disable sending Elastic APM
| APM_SERVICE_DEBUG |  ```bool``` | ```False``` | Enable APM debug mode
| APM_SERVICE_NAME |  ```string``` | ```''``` | APM Service Name
| APM_SECRET_TOKEN |  ```string``` | ```''``` | APM Secret Token
| APM_SERVER_URL |  ```string``` | ```''``` | APM URL
| APM_SERVICE_ENVIRONMENT |  ```string``` | ```''``` | Environment that APM is running on
| ENVIRONMENT |  ```string``` | ```production``` | Specify the environment you are going to run, it is also used for sentry
| SUGGESTION_LANGUAGES |  ```string``` | ```en|pt_br``` | Specify the the languages supported by environment for word and intent suggestions
| N_WORDS_TO_GENERATE |  ```int``` | ```4``` | Specify the number of suggestions that will be returned for word suggestions 
| N_SENTENCES_TO_GENERATE |  ```int``` | ```10``` | Specify the number of suggestions that will be returned for intent suggestions
| REDIS_TIMEOUT |  ```int``` | ```3600``` | Specify a systemwide Redis keys life time
| SECRET_KEY_CHECK_LEGACY_USER | ```string``` | ```None``` | Enables and specifies the token to use for the legacy user endpoint.
| OIDC_ENABLED | ```bool``` | ```False``` | Enable using OIDC.
| OIDC_RP_CLIENT_ID | ```string``` | ```None``` | OpenID Connect client ID provided by your OP.
| OIDC_RP_CLIENT_SECRET | ```string``` | ```None``` | OpenID Connect client secret provided by your OP.
| OIDC_OP_AUTHORIZATION_ENDPOINT | ```string``` | ```None``` | URL of your OpenID Connect provider authorization endpoint.
| OIDC_OP_TOKEN_ENDPOINT | ```string``` | ```None``` | URL of your OpenID Connect provider token endpoint.
| OIDC_OP_USER_ENDPOINT | ```string``` | ```None``` | URL of your OpenID Connect provider userinfo endpoint.
| OIDC_OP_JWKS_ENDPOINT | ```string``` | ```None``` | URL of your OpenID Connect provider JWKS endpoint.
| OIDC_RP_SIGN_ALGO | ```string``` | ```RS256``` | Sets the algorithm the IdP uses to sign ID tokens.
| OIDC_DRF_AUTH_BACKEND | ```string``` | ```bothub.authentication.authorization.WeniOIDCAuthenticationBackend``` | Define the authentication middleware for the django rest framework.
| OIDC_RP_SCOPES | ```string``` | ```openid email``` | The OpenID Connect scopes to request during login.
| CONNECT_GRPC_SERVER_URL | ```string``` | ```localhost:8002``` | Define grpc connect server url
| CONNECT_CERTIFICATE_GRPC_CRT | ```string``` | ```None``` | Absolute certificate path for secure grpc communication
| CONNECT_API_URL | ```string``` | ```None``` | Connect module api url
| USE_GRPC | ```bool``` | ```False``` | Use connect gRPC clients
| RECAPTCHA_SECRET_KEY | ```string``` | ```''``` | Token of the recaptcha used in the validation of a user's registration.
| REPOSITORY_NLP_LOG_LIMIT | ```int``` | ```10000``` | Limit of query size to repository log.
| REPOSITORY_RESTRICT_ACCESS_NLP_LOGS | ```list``` | ```[]``` | Restricts log access to a particular or multiple intelligences
| REPOSITORY_KNOWLEDGE_BASE_DESCRIPTION_LIMIT | ```int``` | ```450``` | Limit of characters in the knowledge base description
| REPOSITORY_EXAMPLE_TEXT_WORDS_LIMIT | ```int``` | ```200``` | Limit of words for the example sentence text
| ELASTICSEARCH_DSL | ```string``` | ```es:9200``` | URL Elasticsearch.
| ELASTICSEARCH_NUMBER_OF_SHARDS | ```int``` | ```1``` | Specify the number of shards for the indexes.
| ELASTICSEARCH_NUMBER_OF_REPLICAS | ```int``` | ```1``` | Specify the number of replicas for the indexes.
| ELASTICSEARCH_REPOSITORYNLPLOG_INDEX | ```string``` | ```ai_repositorynlplog``` | Specify the index title for the RepositoryNLPLog document.
| ELASTICSEARCH_REPOSITORYQANLPLOG_INDEX | ```string``` | ```ai_repositoryqanlplog``` | Specify the index title for the RepositoryQANLPLog document.
| ELASTICSEARCH_REPOSITORYBASICEXAMPLE_INDEX | ```string``` | ```ai_repositorybasicexample``` | Specify the index title for the RepositoryBasicExample document.
| ELASTICSEARCH_SIGNAL_PROCESSOR | ```string``` | ```celery``` | Specify the signal processor responsible for updating the Elasticsearch data.
| ELASTICSEARCH_DELETE_ILM_NAME | ```string``` | ```delete_nlp_logs``` | Specify the name of the ILM responsible to delete the logs.
| ELASTICSEARCH_TIMESTAMP_PIPELINE_NAME | ```string``` | ```set_timestamp``` | Specify the pipeline name that will be responsible to create the @timestamp field.
| ES_TIMESTAMP_PIPELINE_FIELD | ```string``` | ```created_at``` | Specify the field that will be used to populate the @timestamp field.
| ELASTICSEARCH_LOGS_ROLLOVER_AGE | ```string``` | ```1d``` | Specify the ILM rollover age, when a new index will be created.
| ELASTICSEARCH_LOGS_DELETE_AGE | ```string``` | ```90d``` | Specify the ILM delete age, when the index will be deleted.
| GUNICORN_WORKERS | ``` int ``` | ``` multiprocessing.cpu_count() * 2 + 1 ``` | Gunicorn number of workers.
| USE_ELASTICSEARCH | ```boolean``` | ```true``` | Change the logic in requirements_to_train to use either elasticsearch or postgres.
| REPOSITORY_BLOCK_USER_LOGS | ```list``` | ```[]``` | List of repository authorization(api bearer) that won't save logs





## Roadmap

See the [open issues](https://trello.com/b/ab5IvrLe/bothub-roadmap-2020) for a list of proposed features (and known issues).


## License

Distributed under the GPL-3.0 License. See `LICENSE` for more information.


## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

