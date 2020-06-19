import requests
from datetime import timedelta
from django.utils import timezone
from collections import OrderedDict
from urllib.parse import urlencode

from django.conf import settings
from django.db.models import Q

from bothub.celery import app
from bothub.common.models import RepositoryQueueTask


@app.task()
def trainings_check_task():
    trainers = RepositoryQueueTask.objects.filter(
        Q(status=RepositoryQueueTask.STATUS_PENDING)
        | Q(status=RepositoryQueueTask.STATUS_TRAINING)
    )
    for train in trainers:
        services = {
            RepositoryQueueTask.QUEUE_AIPLATFORM: "ai-platform",
            RepositoryQueueTask.QUEUE_CELERY: "celery",
        }
        result = requests.get(
            url=f"{settings.BOTHUB_NLP_BASE_URL}v2/task-queue/",
            params=urlencode(
                OrderedDict(
                    [
                        ("id_task", train.id_queue),
                        ("from_queue", services.get(train.from_queue)),
                    ]
                )
            ),
        ).json()

        if int(result.get("status")) != train.status:
            train.status = result.get("status")
            train.save(update_fields=["status"])
            continue

        if train.created_at + timedelta(hours=2) > timezone.now():
            train.status = RepositoryQueueTask.STATUS_FAILED
            train.save(update_fields=["status"])
