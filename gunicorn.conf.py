import multiprocessing
import os

current_path = os.path.dirname(os.path.abspath(__file__))
bind = '127.0.0.1:8000'
workers = multiprocessing.cpu_count() * 2 + 1
name = 'bothub'
env = 'DJANGO_SETTINGS_MODULE=bothub.settings'
proc_name = name
default_proc_name = proc_name
chdir = current_path
timeout = 120
access_log_format = 'gunicorn - %(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
