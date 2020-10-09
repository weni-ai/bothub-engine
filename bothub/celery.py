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
    "delete-nlp-logs": {
        "task": "bothub.common.tasks.delete_nlp_logs",
        "schedule": schedules.crontab(hour="22", minute=0),
    },
    "repositories-count-authorizations": {
        "task": "bothub.common.tasks.repositories_count_authorizations",
        "schedule": schedules.crontab(hour="8", minute=0),
    },
    "intentions-balance-scores": {
        "task": "bothub.common.tasks.intents_score",
        "schedule": 0.5,
    },
}


@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))
