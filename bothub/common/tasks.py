import requests
from datetime import timedelta
from django.utils import timezone
from urllib.parse import urlencode

from django.conf import settings
from django.db.models import Q

from bothub.celery import app
from bothub.common.models import (
    RepositoryQueueTask,
    RepositoryVersion,
    RepositoryVersionLanguage,
    RepositoryExample,
    RepositoryExampleEntity,
    RepositoryEntityGroup,
    RepositoryEntity,
    RepositoryTranslatedExample,
    RepositoryTranslatedExampleEntity,
    RepositoryEvaluate,
    RepositoryEvaluateEntity,
)


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


@app.task(name="clone_version")
def debug_parse_text(instance_id, id_clone, repository, *args, **kwargs):
    clone = RepositoryVersion.objects.get(pk=id_clone, repository=repository)
    instance = RepositoryVersion.objects.get(pk=instance_id)

    for version in clone.version_languages:

        version_language = RepositoryVersionLanguage.objects.create(
            language=version.language,
            training_started_at=version.training_started_at,
            training_end_at=version.training_end_at,
            failed_at=version.failed_at,
            use_analyze_char=version.use_analyze_char,
            use_name_entities=version.use_name_entities,
            use_competing_intents=version.use_competing_intents,
            algorithm=version.algorithm,
            repository_version=instance,
            training_log=version.training_log,
            last_update=version.last_update,
            total_training_end=version.total_training_end,
        )
        version_language.update_trainer(
            version.get_bot_data.bot_data, version.get_bot_data.rasa_version
        )

        examples = RepositoryExample.objects.filter(repository_version_language=version)

        for example in examples:
            example_id = RepositoryExample.objects.create(
                repository_version_language=version_language,
                text=example.text,
                intent=example.intent,
                created_at=example.created_at,
                last_update=example.last_update,
            )

            example_entites = RepositoryExampleEntity.objects.filter(
                repository_example=example
            )

            for example_entity in example_entites:
                if example_entity.entity.group:
                    group, created_group = RepositoryEntityGroup.objects.get_or_create(
                        repository_version=instance,
                        value=example_entity.entity.group.value,
                    )
                    entity, created_entity = RepositoryEntity.objects.get_or_create(
                        repository_version=instance,
                        value=example_entity.entity.value,
                        group=group,
                    )
                    RepositoryExampleEntity.objects.create(
                        repository_example=example_id,
                        start=example_entity.start,
                        end=example_entity.end,
                        entity=entity,
                        created_at=example_entity.created_at,
                    )
                else:
                    entity, created = RepositoryEntity.objects.get_or_create(
                        repository_version=instance, value=example_entity.entity.value
                    )
                    RepositoryExampleEntity.objects.create(
                        repository_example=example_id,
                        start=example_entity.start,
                        end=example_entity.end,
                        entity=entity,
                        created_at=example_entity.created_at,
                    )

            translated_examples = RepositoryTranslatedExample.objects.filter(
                original_example=example
            )

            for translated_example in translated_examples:
                translated = RepositoryTranslatedExample.objects.create(
                    repository_version_language=version_language,
                    original_example=example_id,
                    language=translated_example.language,
                    text=translated_example.text,
                    created_at=translated_example.created_at,
                    clone_repository=True,
                )

                translated_entity_examples = RepositoryTranslatedExampleEntity.objects.filter(
                    repository_translated_example=translated_example
                )

                for translated_entity in translated_entity_examples:
                    if translated_entity.entity.group:
                        group, created_group = RepositoryEntityGroup.objects.get_or_create(
                            repository_version=instance,
                            value=translated_entity.entity.group.value,
                        )
                        entity, created_entity = RepositoryEntity.objects.get_or_create(
                            repository_version=instance,
                            value=translated_entity.entity.value,
                            group=group,
                        )
                        RepositoryTranslatedExampleEntity.objects.create(
                            repository_translated_example=translated,
                            start=translated_entity.start,
                            end=translated_entity.end,
                            entity=entity,
                            created_at=translated_entity.created_at,
                        )
                    else:
                        entity, created_entity = RepositoryEntity.objects.get_or_create(
                            repository_version=instance,
                            value=translated_entity.entity.value,
                        )
                        RepositoryTranslatedExampleEntity.objects.create(
                            repository_translated_example=translated,
                            start=translated_entity.start,
                            end=translated_entity.end,
                            entity=entity,
                            created_at=translated_entity.created_at,
                        )

        evaluates = RepositoryEvaluate.objects.filter(
            repository_version_language=version
        )

        for evaluate in evaluates:
            evaluate_id = RepositoryEvaluate.objects.create(
                repository_version_language=version_language,
                text=evaluate.text,
                intent=evaluate.intent,
                created_at=evaluate.created_at,
            )

            evaluate_entities = RepositoryEvaluateEntity.objects.filter(
                repository_evaluate=evaluate
            )

            for evaluate_entity in evaluate_entities:
                RepositoryEvaluateEntity.objects.create(
                    repository_evaluate=evaluate_id,
                    start=evaluate_entity.start,
                    end=evaluate_entity.end,
                    entity=evaluate_entity.entity,
                    created_at=evaluate_entity.created_at,
                )

    instance.is_deleted = False
    instance.save(update_fields=["is_deleted"])
    return True
