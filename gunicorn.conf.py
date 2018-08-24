import multiprocessing

bind = '0.0.0.0:80'
workers = multiprocessing.cpu_count() * 2 + 1
raw_env = ['DJANGO_SETTINGS_MODULE=bothub.settings']
