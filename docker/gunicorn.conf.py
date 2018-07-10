import multiprocessing

bind = 'unix:/tmp/bothub.sock'
workers = multiprocessing.cpu_count() * 2 + 1
raw_env = ['DJANGO_SETTINGS_MODULE=bothub.settings']
daemon = True
