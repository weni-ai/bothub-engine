from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

from bothub import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bothub.settings")

app = Celery("bothub")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'bothub.common.tasks.test_task',
        'schedule': 60.0,
        # 'args': (16, 16)
    },
}


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
