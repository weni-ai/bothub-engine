import os

import environ

from django.utils.log import DEFAULT_LOGGING

from .utils import cast_supported_languages
from .utils import cast_empty_str_to_none


environ.Env.read_env(env_file=(environ.Path(__file__) - 2)(".env"))

env = environ.Env(
    # set casting, default value
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
    BOTHUB_ENGINE_AWS_ACCESS_KEY_ID=(str, ""),
    BOTHUB_ENGINE_AWS_SECRET_ACCESS_KEY=(str, ""),
    BOTHUB_ENGINE_AWS_S3_BUCKET_NAME=(str, ""),
    BOTHUB_ENGINE_AWS_REGION_NAME=(str, "us-east-1"),
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "drf_yasg",
    "django_filters",
    "corsheaders",
    "bothub.authentication",
    "bothub.common",
    "bothub.api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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
            ]
        },
    }
]

WSGI_APPLICATION = "bothub.wsgi.application"


# Database


DATABASES = {"default": env.db(var="DEFAULT_DATABASE", default="sqlite:///db.sqlite3")}


# Auth

AUTH_USER_MODEL = "authentication.User"


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

LANGUAGE_CODE = env.str("LANGUAGE_CODE")

TIME_ZONE = env.str("TIME_ZONE")

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = env.str("STATIC_URL")

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# rest framework

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication"
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination." + "LimitOffsetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_METADATA_CLASS": "bothub.api.v1.metadata.Metadata",
}


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
LOGGING["loggers"]["bothub.health.checks"] = {
    "handlers": ["bothub.health"],
    "level": "DEBUG",
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


# AWS

AWS_ACCESS_KEY_ID = env.str("BOTHUB_ENGINE_AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.str("BOTHUB_ENGINE_AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = env.str("BOTHUB_ENGINE_AWS_S3_BUCKET_NAME")
AWS_REGION_NAME = env.str("BOTHUB_ENGINE_AWS_REGION_NAME")


# User Permissions

USER_PERMISSIONS = {
    "Owner": [
        "write.repository",
        "delete.repositoryevaluate",
        "write.repositoryadminmanager",
        "edit.repositoryupdate",
        "write.repositoryupdate",
        "delete.repository",
        "write.repositoryevaluate",
        "view.repositoryupdate",
        "delete.repositoryadminmanager",
        "delete.repositoryupdate",
        "view.repositoryevaluateresult",
        "view.repositoryadminmanager",
        "edit.repository",
        "edit.repositoryevaluateresult",
        "delete.repositoryevaluateresult",
        "delete.repositoryexample",
        "view.repositoryevaluate",
        "write.repositoryevaluateresult",
        "write.repositoryexample",
        "view.repositoryexample",
        "write.repositorytranslatedexample",
        "edit.repositorytranslatedexample",
        "delete.repositorytranslatedexample",
        "edit.repositoryexample",
        "view.repositorytranslatedexample",
        "edit.repositoryadminmanager",
        "edit.repositoryevaluate",
        "view.repository",
    ],
    # "Admin": [
    #     "write.repository",
    #     "delete.repositoryevaluate",
    #     "write.repositoryadminmanager",
    #     "edit.repositoryupdate",
    #     "write.repositoryupdate",
    #     "delete.repository",
    #     "write.repositoryevaluate",
    #     "view.repositoryupdate",
    #     "delete.repositoryadminmanager",
    #     "delete.repositoryupdate",
    #     "view.repositoryevaluateresult",
    #     "view.repositoryadminmanager",
    #     "edit.repository",
    #     "edit.repositoryevaluateresult",
    #     "delete.repositoryevaluateresult",
    #     "delete.repositoryexample",
    #     "view.repositoryevaluate",
    #     "write.repositoryevaluateresult",
    #     "write.repositoryexample",
    #     "view.repositoryexample",
    #     "write.repositorytranslatedexample",
    #     "edit.repositorytranslatedexample",
    #     "delete.repositorytranslatedexample",
    #     "edit.repositoryexample",
    #     "view.repositorytranslatedexample",
    #     "edit.repositoryadminmanager",
    #     "edit.repositoryevaluate",
    #     "view.repository",
    # ],
    # "Contributor": [
    #     "write.repository",
    #     "delete.repositoryevaluate",
    #     "write.repositoryadminmanager",
    #     "edit.repositoryupdate",
    #     "write.repositoryupdate",
    #     "delete.repository",
    #     "write.repositoryevaluate",
    #     "view.repositoryupdate",
    #     "delete.repositoryadminmanager",
    #     "delete.repositoryupdate",
    #     "view.repositoryevaluateresult",
    #     "view.repositoryadminmanager",
    #     "edit.repository",
    #     "edit.repositoryevaluateresult",
    #     "delete.repositoryevaluateresult",
    #     "delete.repositoryexample",
    #     "view.repositoryevaluate",
    #     "write.repositoryevaluateresult",
    #     "write.repositoryexample",
    #     "view.repositoryexample",
    #     "write.repositorytranslatedexample",
    #     "edit.repositorytranslatedexample",
    #     "delete.repositorytranslatedexample",
    #     "edit.repositoryexample",
    #     "view.repositorytranslatedexample",
    #     "edit.repositoryadminmanager",
    #     "edit.repositoryevaluate",
    #     "view.repository",
    # ],
    "Public": [
        "write.repository",
        "delete.repositoryevaluate",
        "write.repositoryadminmanager",
        "edit.repositoryupdate",
        "write.repositoryupdate",
        "delete.repository",
        "write.repositoryevaluate",
        "view.repositoryupdate",
        "delete.repositoryadminmanager",
        "delete.repositoryupdate",
        "view.repositoryevaluateresult",
        "view.repositoryadminmanager",
        "edit.repository",
        "edit.repositoryevaluateresult",
        "delete.repositoryevaluateresult",
        "delete.repositoryexample",
        "view.repositoryevaluate",
        "write.repositoryevaluateresult",
        "write.repositoryexample",
        "view.repositoryexample",
        "write.repositorytranslatedexample",
        "edit.repositorytranslatedexample",
        "delete.repositorytranslatedexample",
        "edit.repositoryexample",
        "view.repositorytranslatedexample",
        "edit.repositoryadminmanager",
        "edit.repositoryevaluate",
        "view.repository",
    ]
}
