import os
import multiprocessing

import environ
import sentry_sdk

from django.utils.log import DEFAULT_LOGGING
from django.utils.translation import ugettext_lazy as _
from sentry_sdk.integrations.django import DjangoIntegration

from .utils import cast_supported_languages
from .utils import cast_empty_str_to_none


environ.Env.read_env(env_file=(environ.Path(__file__) - 2)(".env"))

env = environ.Env(
    # set casting, default value
    ENVIRONMENT=(str, "production"),
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(lambda v: [s.strip() for s in v.split(",")], "*"),
    LANGUAGE_CODE=(str, "en-us"),
    TIME_ZONE=(str, "UTC"),
    STATIC_URL=(str, "/static/"),
    EMAIL_HOST=(cast_empty_str_to_none, None),
    ADMINS=(
        lambda v: [
            (s.strip().split("|")[0], s.strip().split("|")[1]) for s in v.split(",")
        ]
        if v
        else [],
        [],
    ),
    DEFAULT_FROM_EMAIL=(str, "webmaster@localhost"),
    SERVER_EMAIL=(str, "root@localhost"),
    EMAIL_PORT=(int, 25),
    EMAIL_HOST_USER=(str, ""),
    EMAIL_HOST_PASSWORD=(str, ""),
    EMAIL_USE_SSL=(bool, False),
    EMAIL_USE_TLS=(bool, False),
    SEND_EMAILS=(bool, True),
    BOTHUB_WEBAPP_BASE_URL=(str, "http://localhost:8080/"),
    BOTHUB_NLP_BASE_URL=(str, "http://localhost:2657/"),
    CSRF_COOKIE_DOMAIN=(cast_empty_str_to_none, None),
    CSRF_COOKIE_SECURE=(bool, False),
    SUPPORTED_LANGUAGES=(cast_supported_languages, "en|pt"),
    CHECK_ACCESSIBLE_API_URL=(str, None),
    BOTHUB_ENGINE_AWS_ENDPOINT_URL=(str, None),
    BOTHUB_ENGINE_AWS_ACCESS_KEY_ID=(str, ""),
    BOTHUB_ENGINE_AWS_SECRET_ACCESS_KEY=(str, ""),
    BOTHUB_ENGINE_AWS_S3_BUCKET_NAME=(str, ""),
    BOTHUB_ENGINE_AWS_REGION_NAME=(str, "us-east-1"),
    BOTHUB_ENGINE_AWS_SEND=(bool, False),
    BASE_URL=(str, "http://api.bothub.it"),
    BOTHUB_BOT_EMAIL=(str, "bot_repository@bothub.it"),
    BOTHUB_BOT_NAME=(str, "Bot Repository"),
    BOTHUB_BOT_NICKNAME=(str, "bot_repository"),
    BOTHUB_ENGINE_USE_SENTRY=(bool, False),
    BOTHUB_ENGINE_SENTRY=(str, None),
    BOTHUB_NLP_RASA_VERSION=(str, "1.4.3"),
    CELERY_BROKER_URL=(str, "redis://localhost:6379/0"),
    TOKEN_SEARCH_REPOSITORIES=(str, None),
    GOOGLE_API_TRANSLATION_KEY=(str, None),
    N_WORDS_TO_GENERATE=(int, 4),
    SUGGESTION_LANGUAGES=(cast_supported_languages, "en|pt_br"),
    N_SENTENCES_TO_GENERATE=(int, 10),
    REDIS_TIMEOUT=(int, 3600),
    APM_DISABLE_SEND=(bool, False),
    APM_SERVICE_DEBUG=(bool, False),
    APM_SERVICE_NAME=(str, ""),
    APM_SECRET_TOKEN=(str, ""),
    APM_SERVER_URL=(str, ""),
    APM_SERVICE_ENVIRONMENT=(str, "production"),
    DJANGO_REDIS_URL=(str, "redis://localhost:6379/1"),
    OIDC_ENABLED=(bool, False),
    SECRET_KEY_CHECK_LEGACY_USER=(str, None),
    CONNECT_GRPC_SERVER_URL=(str, "localhost:8002"),
    CONNECT_CERTIFICATE_GRPC_CRT=(str, None),
    REPOSITORY_RESTRICT_ACCESS_NLP_LOGS=(list, []),
    ELASTICSEARCH_DSL=(str, "localhost:9200"),
    ELASTICSEARCH_REPOSITORYNLPLOG_INDEX=(str, "ai_repositorynlplog"),
    ELASTICSEARCH_REPOSITORYQANLPLOG_INDEX=(str, "ai_repositoryqanlplog"),
    ELASTICSEARCH_NUMBER_OF_SHARDS=(int, 1),
    ELASTICSEARCH_NUMBER_OF_REPLICAS=(int, 1),
    ELASTICSEARCH_SIGNAL_PROCESSOR=(str, "realtime"),
    GUNICORN_WORKERS=(int, multiprocessing.cpu_count() * 2 + 1),
)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

BASE_URL = env.str("BASE_URL")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_recaptcha",
    "drf_yasg2",
    "django_filters",
    "corsheaders",
    "elasticapm.contrib.django",
    "bothub.authentication",
    "bothub.common",
    "bothub.api",
    "bothub.common.migrate_classifiers",
    "django_celery_results",
    "django_celery_beat",
    "django_redis",
    "django_grpc_framework",
    "django_elasticsearch_dsl",
    "django_elasticsearch_dsl_drf",
]

MIDDLEWARE = [
    "elasticapm.contrib.django.middleware.TracingMiddleware",
    "elasticapm.contrib.django.middleware.Catch404Middleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "bothub.api.v2.middleware.UserLanguageMiddleware",
]

ROOT_URLCONF = "bothub.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "elasticapm.contrib.django.context_processors.rum_tracing",
            ]
        },
    }
]

WSGI_APPLICATION = "bothub.wsgi.application"


# Database


DATABASES = {"default": env.db(var="DEFAULT_DATABASE", default="sqlite:///db.sqlite3")}


# Auth

AUTH_USER_MODEL = "authentication.User"

DRF_RECAPTCHA_SECRET_KEY = env.str("RECAPTCHA_SECRET_KEY", default="")

DRF_RECAPTCHA_VERIFY_ENDPOINT = "https://www.google.com/recaptcha/api/siteverify"

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        + "UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation." + "MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation." + "CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation." + "NumericPasswordValidator"},
]


# Internationalization

DEFAULT_ERROR_MESSAGE = _("An error has occurred")

LANGUAGE_CODE = env.str("LANGUAGE_CODE")


LANGUAGES = (("en-us", _("English")), ("pt-br", _("Brazilian Portuguese")))

MODELTRANSLATION_DEFAULT_LANGUAGE = "en-us"

LOCALE_PATHS = (os.path.join(os.path.dirname(__file__), "locale"),)

TIME_ZONE = env.str("TIME_ZONE")

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = env.str("STATIC_URL")

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# rest framework

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication"
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination." + "LimitOffsetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_METADATA_CLASS": "bothub.api.v2.metadata.Metadata",
}

REPOSITORY_NLP_LOG_LIMIT = env.int("REPOSITORY_NLP_LOG_LIMIT", default=10000)

# cors headers

CORS_ORIGIN_ALLOW_ALL = True


# mail

envvar_EMAIL_HOST = env.str("EMAIL_HOST")

ADMINS = env.list("ADMINS")
EMAIL_SUBJECT_PREFIX = "[bothub] "
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL")
SERVER_EMAIL = env.str("SERVER_EMAIL")

if envvar_EMAIL_HOST:
    EMAIL_HOST = envvar_EMAIL_HOST
    EMAIL_PORT = env.int("EMAIL_PORT")
    EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")
    EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL")
    EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SEND_EMAILS = env.bool("SEND_EMAILS")


# webapp

BOTHUB_WEBAPP_BASE_URL = env.str("BOTHUB_WEBAPP_BASE_URL")


# NLP

BOTHUB_NLP_BASE_URL = env.str("BOTHUB_NLP_BASE_URL")


# CSRF

CSRF_COOKIE_DOMAIN = env.str("CSRF_COOKIE_DOMAIN")

CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE")


# Logging

LOGGING = DEFAULT_LOGGING
LOGGING["formatters"]["bothub.health"] = {
    "format": "[bothub.health] {message}",
    "style": "{",
}
LOGGING["handlers"]["bothub.health"] = {
    "level": "DEBUG",
    "class": "logging.StreamHandler",
    "formatter": "bothub.health",
}
LOGGING["handlers"]["elasticapm"] = {
    "level": "WARNING",
    "class": "elasticapm.contrib.django.handlers.LoggingHandler",
}
LOGGING["loggers"]["bothub.health.checks"] = {
    "handlers": ["bothub.health"],
    "level": "DEBUG",
}
LOGGING["formatters"]["verbose"] = {
    "format": "%(levelname)s  %(asctime)s  %(module)s "
    "%(process)d  %(thread)d  %(message)s"
}
LOGGING["handlers"]["console"] = {
    "level": "DEBUG",
    "class": "logging.StreamHandler",
    "formatter": "verbose",
}
LOGGING["loggers"]["django.db.backends"] = {
    "level": "ERROR",
    "handlers": ["console"],
    "propagate": False,
}
LOGGING["loggers"]["sentry.errors"] = {
    "level": "DEBUG",
    "handlers": ["console"],
    "propagate": False,
}
LOGGING["loggers"]["elasticapm.errors"] = {
    "level": "ERROR",
    "handlers": ["console"],
    "propagate": False,
}


# Supported Languages

SUPPORTED_LANGUAGES = env.get_value(
    "SUPPORTED_LANGUAGES", cast_supported_languages, "en|pt", True
)


# SECURE PROXY SSL HEADER

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Swagger

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "DOC_EXPANSION": "list",
    "APIS_SORTER": "alpha",
    "SECURITY_DEFINITIONS": {
        "api_key": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
}

DRF_YASG_EXCLUDE_VIEWS = (
    [
        "bothub.api.v2.nlp.views.RepositoryAuthorizationTrainViewSet",
        "bothub.api.v2.nlp.views.RepositoryAuthorizationParseViewSet",
        "bothub.api.v2.nlp.views.RepositoryAuthorizationInfoViewSet",
        "bothub.api.v2.nlp.views.RepositoryAuthorizationEvaluateViewSet",
        "bothub.api.v2.nlp.views.NLPLangsViewSet",
        "bothub.api.v2.nlp.views.RepositoryUpdateInterpretersViewSet",
    ]
    if not DEBUG
    else []
)


# AWS
AWS_SEND = env.bool("BOTHUB_ENGINE_AWS_SEND")
AWS_ACCESS_ENDPOINT_URL = env.str("BOTHUB_ENGINE_AWS_ENDPOINT_URL")
AWS_ACCESS_KEY_ID = env.str("BOTHUB_ENGINE_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.str("BOTHUB_ENGINE_AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = env.str("BOTHUB_ENGINE_AWS_S3_BUCKET_NAME")
AWS_REGION_NAME = env.str("BOTHUB_ENGINE_AWS_REGION_NAME")


# Account System for bots deleted

BOTHUB_BOT_EMAIL = env.str("BOTHUB_BOT_EMAIL")
BOTHUB_BOT_NAME = env.str("BOTHUB_BOT_NAME")
BOTHUB_BOT_NICKNAME = env.str("BOTHUB_BOT_NICKNAME")

# Sentry Environment

BOTHUB_ENGINE_USE_SENTRY = env.bool("BOTHUB_ENGINE_USE_SENTRY")


# Sentry

if BOTHUB_ENGINE_USE_SENTRY:
    sentry_sdk.init(
        dsn=env.str("BOTHUB_ENGINE_SENTRY"),
        integrations=[DjangoIntegration()],
        environment=env.str("ENVIRONMENT"),
    )

# Rasa NLP Version

BOTHUB_NLP_RASA_VERSION = env.str("BOTHUB_NLP_RASA_VERSION")


# Celery

CELERY_RESULT_BACKEND = "django-db"
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"


# Search Example Repositories
TOKEN_SEARCH_REPOSITORIES = env.str("TOKEN_SEARCH_REPOSITORIES")


# Google API Translation KEY
GOOGLE_API_TRANSLATION_KEY = env.str("GOOGLE_API_TRANSLATION_KEY")


BASE_MIGRATIONS_TYPES = ["bothub.common.migrate_classifiers.wit.WitType"]


# Suggestion Languages
SUGGESTION_LANGUAGES = env.str("SUGGESTION_LANGUAGES")


# Word suggestions
N_WORDS_TO_GENERATE = env.int("N_WORDS_TO_GENERATE")


# Intent suggestions
N_SENTENCES_TO_GENERATE = env.int("N_SENTENCES_TO_GENERATE")


# Restrict access to the nlp logs by a list of repository uuids
REPOSITORY_RESTRICT_ACCESS_NLP_LOGS = env.list("REPOSITORY_RESTRICT_ACCESS_NLP_LOGS")


# django_redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("DJANGO_REDIS_URL"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# Set Redis timeout
REDIS_TIMEOUT = env.int("REDIS_TIMEOUT")

# Elastic Observability APM
ELASTIC_APM = {
    "DISABLE_SEND": env.bool("APM_DISABLE_SEND"),
    "DEBUG": env.bool("APM_SERVICE_DEBUG"),
    "SERVICE_NAME": env("APM_SERVICE_NAME"),
    "SECRET_TOKEN": env("APM_SECRET_TOKEN"),
    "SERVER_URL": env("APM_SERVER_URL"),
    "ENVIRONMENT": env("APM_SERVICE_ENVIRONMENT"),
    "DJANGO_TRANSACTION_NAME_FROM_ROUTE": True,
    "PROCESSORS": [
        "elasticapm.processors.sanitize_stacktrace_locals",
        "elasticapm.processors.sanitize_http_request_cookies",
        "elasticapm.processors.sanitize_http_headers",
        "elasticapm.processors.sanitize_http_wsgi_env",
        "elasticapm.processors.sanitize_http_request_body",
    ],
}

SECRET_KEY_CHECK_LEGACY_USER = env.str("SECRET_KEY_CHECK_LEGACY_USER")

# mozilla-django-oidc
OIDC_ENABLED = env.bool("OIDC_ENABLED")
if OIDC_ENABLED:
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].append(
        "mozilla_django_oidc.contrib.drf.OIDCAuthentication"
    )
    INSTALLED_APPS = (*INSTALLED_APPS, "mozilla_django_oidc")
    LOGGING["loggers"]["mozilla_django_oidc"] = {
        "level": "DEBUG",
        "handlers": ["console"],
        "propagate": False,
    }
    LOGGING["loggers"]["weni_django_oidc"] = {
        "level": "DEBUG",
        "handlers": ["console"],
        "propagate": False,
    }

    OIDC_RP_CLIENT_ID = env.str("OIDC_RP_CLIENT_ID")
    OIDC_RP_CLIENT_SECRET = env.str("OIDC_RP_CLIENT_SECRET")
    OIDC_OP_AUTHORIZATION_ENDPOINT = env.str("OIDC_OP_AUTHORIZATION_ENDPOINT")
    OIDC_OP_TOKEN_ENDPOINT = env.str("OIDC_OP_TOKEN_ENDPOINT")
    OIDC_OP_USER_ENDPOINT = env.str("OIDC_OP_USER_ENDPOINT")
    OIDC_OP_JWKS_ENDPOINT = env.str("OIDC_OP_JWKS_ENDPOINT")
    OIDC_RP_SIGN_ALGO = env.str("OIDC_RP_SIGN_ALGO", default="RS256")
    OIDC_DRF_AUTH_BACKEND = env.str(
        "OIDC_DRF_AUTH_BACKEND",
        default="bothub.authentication.authorization.WeniOIDCAuthenticationBackend",
    )
    OIDC_RP_SCOPES = env.str("OIDC_RP_SCOPES", default="openid email")


# gRPC Connect Server
CONNECT_GRPC_SERVER_URL = env.str("CONNECT_GRPC_SERVER_URL")

CONNECT_CERTIFICATE_GRPC_CRT = env.str("CONNECT_CERTIFICATE_GRPC_CRT")

# ElasticSearch
ELASTICSEARCH_DSL = {
    "default": {"hosts": env.str("ELASTICSEARCH_DSL", default="es:9200")}
}

ELASTICSEARCH_DSL_INDEX_SETTINGS = {
    "number_of_shards": env.int("ELASTICSEARCH_NUMBER_OF_SHARDS", default=1),
    "number_of_replicas": env.int("ELASTICSEARCH_NUMBER_OF_REPLICAS", default=0),
}

ELASTICSEARCH_INDEX_NAMES = {
    "bothub.common.documents.repositorynlplog": env.str(
        "ELASTICSEARCH_REPOSITORYNLPLOG_INDEX", default="ai_repositorynlplog"
    ),
    "bothub.common.documents.repositoryqanlplog": env.str(
        "ELASTICSEARCH_REPOSITORYQANLPLOG_INDEX", default="ai_repositoryqanlplog"
    ),
}

ELASTICSEARCH_SIGNAL_PROCESSOR_CLASSES = {
    "realtime": "django_elasticsearch_dsl.signals.RealTimeSignalProcessor",
    "celery": "bothub.common.signals.CelerySignalProcessor",
}

ELASTICSEARCH_DSL_SIGNAL_PROCESSOR = ELASTICSEARCH_SIGNAL_PROCESSOR_CLASSES[
    env.str("ELASTICSEARCH_SIGNAL_PROCESSOR", default="realtime")
]

GUNICORN_WORKERS = env.int("GUNICORN_WORKERS", default=multiprocessing.cpu_count() * 2 + 1)