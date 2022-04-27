import json
import random
import requests
from datetime import timedelta
from urllib.parse import urlencode
from django.apps import apps
from django.conf import settings
from django.db import transaction
from django.db.models import Q, Count
from django.utils import timezone

from django_elasticsearch_dsl.registries import registry

from bothub import translate
from bothub.api.grpc.connect_grpc_client import ConnectGRPCClient
from bothub.celery import app
from bothub.common.models import (
    RepositoryQueueTask,
    RepositoryReports,
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
    RepositoryIntent,
    Repository,
    RepositoryNLPLog,
    RepositoryScore,
)
from bothub.utils import (
    intentions_balance_score,
    intentions_size_score,
    evaluate_size_score,
    request_nlp,
)


@app.task(name="es_handle_save")
def handle_save(pk, app_label, model_name):
    sender = apps.get_model(app_label, model_name)
    instance = sender.objects.get(pk=pk)
    registry.update(instance)
    registry.update_related(instance)


@app.task()
def trainings_check_task():
    trainers = RepositoryQueueTask.objects.filter(
        Q(status=RepositoryQueueTask.STATUS_PENDING)
        | Q(status=RepositoryQueueTask.STATUS_PROCESSING)
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
def clone_version(instance_id, id_clone, repository, *args, **kwargs):
    clone = RepositoryVersion.objects.get(pk=id_clone, repository=repository)
    instance = RepositoryVersion.objects.get(pk=instance_id)

    bulk_versionlanguages = [
        RepositoryVersionLanguage(**version, pk=None, repository_version=instance)
        for version in clone.version_languages.values()
    ]
    RepositoryVersionLanguage.objects.bulk_create(
        bulk_versionlanguages, ignore_conflicts=True
    )

    for version in clone.version_languages:
        version_language = instance.get_version_language(version.language)

        version_language.update_trainer(
            version.get_bot_data.bot_data, version.get_bot_data.rasa_version
        )

        examples = RepositoryExample.objects.filter(repository_version_language=version)

        for example in examples:
            intent, created = RepositoryIntent.objects.get_or_create(
                text=example.intent.text,
                repository_version=version_language.repository_version,
            )
            example_id = RepositoryExample.objects.create(
                repository_version_language=version_language,
                text=example.text,
                intent=intent,
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
                    repository_version_language=instance.get_version_language(
                        translated_example.language
                    ),
                    original_example=example_id,
                    language=translated_example.language,
                    text=translated_example.text,
                    created_at=translated_example.created_at,
                    clone_repository=True,
                )

                translated_entity_examples = (
                    RepositoryTranslatedExampleEntity.objects.filter(
                        repository_translated_example=translated_example
                    )
                )

                for translated_entity in translated_entity_examples:
                    if translated_entity.entity.group:
                        (
                            group,
                            created_group,
                        ) = RepositoryEntityGroup.objects.get_or_create(
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

            bulk_evaluate_entities = [
                RepositoryEvaluateEntity(
                    **evaluate_entity, pk=None, repository_evaluate=evaluate_id
                )
                for evaluate_entity in evaluate.entities.all().values()
            ]
            RepositoryEvaluateEntity.objects.bulk_create(
                bulk_evaluate_entities, ignore_conflicts=True
            )

    instance.is_deleted = False
    instance.save(update_fields=["is_deleted"])
    return True


@app.task()
def delete_nlp_logs():
    BATCH_SIZE = 5000
    logs = RepositoryNLPLog.objects.filter(
        created_at__lt=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        - timezone.timedelta(days=90)
    )

    num_updated = 0
    max_id = -1
    while True:
        batch = list(logs.filter(id__gt=max_id).order_by("id")[:BATCH_SIZE])

        if not batch:
            break

        max_id = batch[-1].id
        with transaction.atomic():
            for log in batch:
                log.delete()

        num_updated += len(batch)
        print(f" > deleted {num_updated} nlp logs")


@app.task()
def repositories_count_authorizations():
    for repository in Repository.objects.all():
        count = repository.authorizations.filter(
            user__in=RepositoryReports.objects.filter(
                repository_version_language__repository_version__repository=repository,
                report_date__year=timezone.now().year,
                report_date__month=timezone.now().month,
            )
            .distinct()
            .values_list("user", flat=True)
        ).count()
        repository.count_authorizations = count
        repository.save(update_fields=["count_authorizations"])


@app.task(name="auto_translation")
def auto_translation(
    repository_version, source_language, target_language, *args, **kwargs
):

    repository_version = RepositoryVersion.objects.get(pk=repository_version)

    task_queue = repository_version.get_version_language(
        language=target_language
    ).create_task(
        id_queue=app.current_task.request.id,
        from_queue=RepositoryQueueTask.QUEUE_CELERY,
        type_processing=RepositoryQueueTask.TYPE_PROCESSING_AUTO_TRANSLATE,
    )

    examples = (
        RepositoryExample.objects.filter(
            repository_version_language__repository_version=repository_version,
            repository_version_language__language=source_language,
        )
        .annotate(
            translation_count=Count(
                "translations", filter=Q(translations__language=target_language)
            )
        )
        .filter(translation_count=0)
    )

    for example in examples:
        if example.translations.filter(language=target_language).count() > 0:
            # Checks if there is already a translation for this example, it occurs if it is running and the user
            # purposely adds a translation
            continue

        example_translated = translate.translate(
            text=example.get_text(language=source_language),
            source_lang=source_language,
            target_language=target_language,
        )

        translated = RepositoryTranslatedExample.objects.create(
            original_example=example, language=target_language, text=example_translated
        )
        entities = example.get_entities(language=source_language)

        for entity in entities:
            entity_text = example.get_text(language=source_language)[
                entity.start : entity.end
            ]
            entity_translated = translate.translate(
                text=entity_text,
                source_lang=source_language,
                target_language="pt" if target_language == "pt_br" else target_language,
            )
            if entity_translated in example_translated:
                start = example_translated.find(entity_translated)
                end = start + len(entity_translated)
                RepositoryTranslatedExampleEntity.objects.create(
                    repository_translated_example=translated,
                    start=start,
                    end=end,
                    entity=entity.entity,
                )

    task_queue.status = RepositoryQueueTask.STATUS_SUCCESS
    task_queue.end_training = timezone.now()
    task_queue.save(update_fields=["status", "end_training"])


@app.task()
def repository_score():  # pragma: no cover
    for version in RepositoryVersion.objects.filter(
        is_default=True, repository__repository_type="classifier"
    ):
        dataset = {}
        intents = []
        train = {}
        train_total = 0

        repository_examples = RepositoryExample.objects.filter(
            repository_version_language__repository_version=version,
            repository_version_language__language=version.repository.language,
        )

        filtered_examples = list(
            map(
                lambda intent: {
                    "value": intent.text,
                    "examples__count": version.repository.examples(
                        queryset=repository_examples, version_default=version.is_default
                    )
                    .filter(intent=intent)
                    .count(),
                },
                version.version_intents.all(),
            )
        )

        repository_evaluate = RepositoryEvaluate.objects.filter(
            repository_version_language__repository_version=version,
            repository_version_language__language=version.repository.language,
        )

        filtered_evaluate_sentences = dict(
            map(
                lambda x: (
                    x,
                    version.repository.evaluations(
                        language=x,
                        queryset=repository_evaluate,
                        version_default=version.is_default,
                    ).count(),
                ),
                version.repository.available_languages(
                    queryset=RepositoryExample.objects.filter(
                        repository_version_language__repository_version=version,
                        repository_version_language__language=version.repository.language,
                    ),
                    version_default=version.is_default,
                ),
            )
        )

        for example in filtered_examples:
            train[example["value"]] = example["examples__count"]
            intents.append(example["value"])
            train_total += example["examples__count"]

        dataset["intentions"] = intents
        dataset["train_count"] = train_total
        dataset["train"] = train
        dataset["evaluate_count"] = filtered_evaluate_sentences[
            version.repository.language
        ]

        intentions_balance = intentions_balance_score(dataset)
        intentions_size = intentions_size_score(dataset)
        evaluate_size = evaluate_size_score(dataset)

        score, created = RepositoryScore.objects.get_or_create(
            repository=version.repository
        )

        score.intents_balance_score = float(intentions_balance.get("score"))
        score.intents_balance_recommended = intentions_balance.get("recommended")
        score.intents_size_score = float(intentions_size.get("score"))
        score.intents_size_recommended = intentions_size.get("recommended")
        score.evaluate_size_score = float(evaluate_size.get("score"))
        score.evaluate_size_recommended = evaluate_size.get("recommended")

        score.save(
            update_fields=[
                "intents_balance_score",
                "intents_balance_recommended",
                "intents_size_score",
                "intents_size_recommended",
                "evaluate_size_score",
                "evaluate_size_recommended",
            ]
        )


@app.task(name="word_suggestions")
def word_suggestions(repository_example_id, authorization_token):  # pragma: no cover
    example = RepositoryExample.objects.get(pk=repository_example_id)
    try:
        dataset = {}
        if example.language in settings.SUGGESTION_LANGUAGES:
            if len(example.text.split()) > 1:
                for word in example.text.split():
                    data = {
                        "text": word,
                        "language": example.language,
                        "n_words_to_generate": settings.N_WORDS_TO_GENERATE,
                    }
                    suggestions = request_nlp(
                        authorization_token, None, "word_suggestion", data
                    )
                    dataset[word] = suggestions
            else:
                data = {
                    "text": example.text,
                    "language": example.language,
                    "n_words_to_generate": settings.N_WORDS_TO_GENERATE,
                }
                suggestions = request_nlp(
                    authorization_token, None, "word_suggestion", data
                )
                dataset[example.text] = suggestions
        else:
            dataset["language"] = False

        return dataset
    except requests.ConnectionError:
        return False
    except json.JSONDecodeError:
        return False


@app.task(name="migrate_repository")
def migrate_repository(repository_version, auth_token, language, name_classifier):
    version = RepositoryVersion.objects.get(pk=repository_version)
    instance = version.get_migration_types().get(name_classifier)
    instance.repository_version = version
    instance.auth_token = auth_token
    instance.language = language
    return instance.migrate()


@app.task(name="intent_suggestions")
def intent_suggestions(intent_id, language, authorization_token):  # pragma: no cover
    intent = RepositoryIntent.objects.get(pk=intent_id)
    if not language:
        language = intent.repository_version.repository.language

    try:
        dataset = {}
        if intent:
            if language in settings.SUGGESTION_LANGUAGES:
                data = {
                    "intent": intent.text,
                    "language": language,
                    "n_sentences_to_generate": settings.N_SENTENCES_TO_GENERATE,
                    "repository_version": intent.repository_version_id,
                }
                suggestions = request_nlp(
                    authorization_token, None, "intent_sentence_suggestion", data
                )
                suggested_sentences = suggestions.get("suggested_sentences", [])
                if suggested_sentences:
                    random.shuffle(suggested_sentences)
                    dataset[intent.text] = suggested_sentences[
                        : settings.N_SENTENCES_TO_GENERATE
                    ]
            else:
                dataset["language"] = False
        else:
            dataset["intent"] = False

        return dataset
    except requests.ConnectionError:
        return False
    except json.JSONDecodeError:
        return False


@app.task(name="evaluate_crossvalidation")
def evaluate_crossvalidation(data, authorization_token):  # pragma: no cover
    try:
        if data:
            request_data = {
                "language": data.get("language"),
                "repository_version": data.get("repository_version"),
                "cross_validation": True,
            }
        r = request_nlp(authorization_token, None, "evaluate", request_data)
        return r
    except requests.ConnectionError:
        return False
    except json.JSONDecodeError:
        return False


@app.task(name="get_project_organization")
def get_project_organization(project_uuid: str):  # pragma: no cover
    grpc_client = ConnectGRPCClient()
    authorizations = grpc_client.list_authorizations(project_uuid=project_uuid)
    return authorizations


@app.task(name="remove_authorizations_project")
def remove_authorizations_project(
    project_uuid: str, authorizations_uuids: list, user_email: str
):
    grpc_client = ConnectGRPCClient()
    for authorization_uuid in authorizations_uuids:
        grpc_client.remove_authorization(project_uuid, authorization_uuid, user_email)


@app.task(name="create_repository_project")
def create_repository_project(**kwargs):
    grpc_client = ConnectGRPCClient()
    grpc_client.create_classifier(**kwargs)
    return kwargs
