import requests
from datetime import timedelta
from django.utils import timezone
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
                {
                    "id_task": train.id_queue,
                    "from_queue": services.get(train.from_queue),
                }
            ),
        ).json()

        if int(result.get("status")) != train.status:
            fields = ["status", "ml_units"]
            train.status = result.get("status")
            if train.status == RepositoryQueueTask.STATUS_SUCCESS:
                train.end_training = timezone.now()
                fields.append("end_training")
            train.ml_units = result.get("ml_units")
            train.save(update_fields=fields)
            continue

        # Verifica o treinamento que esta em execução, caso o tempo de criação seja maior que 2 horas
        # ele torna a task como falha
        if train.created_at + timedelta(hours=2) <= timezone.now():
            train.status = RepositoryQueueTask.STATUS_FAILED
            train.end_training = timezone.now()
            train.save(update_fields=["status", "end_training"])
