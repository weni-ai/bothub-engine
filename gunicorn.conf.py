import os
import multiprocessing


# bind = '0.0.0.0:80'
workers = os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1)
worker_class = 'gevent'
raw_env = ['DJANGO_SETTINGS_MODULE=bothub.settings']
