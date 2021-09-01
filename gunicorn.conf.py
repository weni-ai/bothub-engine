bind = "0.0.0.0:80"
workers = 3
worker_class = "gevent"
raw_env = ["DJANGO_SETTINGS_MODULE=bothub.settings"]
