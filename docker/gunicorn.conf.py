import os
import multiprocessing

current_path = os.path.dirname(os.path.abspath(__file__))
bind = '0.0.0.0:8000'
workers = multiprocessing.cpu_count() * 2 + 1
threads = workers
name = 'boothub'
env = 'DJANGO_SETTINGS_MODULE=boothub.settings'
proc_name = 'boothub'
default_proc_name = proc_name
chdir = current_path
loglevel = 'info'
