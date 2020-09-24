from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, schedules

from bothub import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bothub.settings")

app = Celery("bothub")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    "check-training-status": {
        "task": "bothub.common.tasks.trainings_check_task",
        "schedule": 5.0,
    },
    "repositories-count-authorizations": {
        "task": "bothub.common.tasks.repositories_count_authorizations",
        "schedule": schedules.crontab(hour="8", minute=0),
    },
}


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
