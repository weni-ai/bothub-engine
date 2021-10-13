from bothub.settings import GUNICORN_WORKERS

bind = '0.0.0.0:80'
workers = GUNICORN_WORKERS
worker_class = 'gevent'
raw_env = ['DJANGO_SETTINGS_MODULE=bothub.settings']
