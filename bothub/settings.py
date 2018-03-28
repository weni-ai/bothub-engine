import os
import dj_database_url

from decouple import config


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='*',
    cast=lambda v: [s.strip() for s in v.split(',')])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'corsheaders',
    'bothub.authentication',
    'bothub.common',
    'bothub.api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bothub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bothub.wsgi.application'


# Database

DATABASES = {}
DATABASES['default'] = dj_database_url.parse(
    config(
        'DEFAULT_DATABASE',
        default='sqlite:///db.sqlite3'))


# Auth

AUTH_USER_MODEL = 'authentication.User'


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.' +
        'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.' +
        'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.' +
        'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.' +
        'NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = config('LANGUAGE_CODE', default='en-us')

TIME_ZONE = config('TIME_ZONE', default='UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'


# rest framework

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.' +
    'LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}


# cors headers

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r'^/api/.*$'


# mail

envvar_EMAIL_HOST = config('EMAIL_HOST', default=None)

ADMINS = config(
    'ADMINS',
    default='',
    cast=lambda v: [
        (
            s.strip().split('|')[0],
            s.strip().split('|')[1],
        ) for s in v.split(',')] if v else [])
EMAIL_SUBJECT_PREFIX = '[bothub] '
DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL',
    default='webmaster@localhost')
SERVER_EMAIL = config('SERVER_EMAIL', default='root@localhost')

if not DEBUG and envvar_EMAIL_HOST:
    EMAIL_HOST = envvar_EMAIL_HOST
    EMAIL_PORT = config('EMAIL_PORT', default=25)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False)
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# webapp

BOTHUB_WEBAPP_BASE_URL = config(
    'BOTHUB_WEBAPP_BASE_URL',
    default='http://localhost:3000/')
