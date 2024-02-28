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
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from django_elasticsearch_dsl.registries import registry

from bothub import translate
from bothub.event_driven.publisher.rabbitmq_publisher import RabbitMQPublisher
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


if settings.USE_GRPC:
    from bothub.api.grpc.connect_grpc_client import ConnectGRPCClient as ConnectClient
else:
    from bothub.api.v2.internal.connect_rest_client import (
        ConnectRESTClient as ConnectClient,
    )


@app.task(name="es_handle_save")
def handle_save(pk, app_label, model_name):
    if settings.USE_ELASTICSEARCH:
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
        )
        if result:
            result = result.json()
        else:
            continue

        status = int(result.get("status"))

        if status != train.status:
            fields = ["status", "ml_units"]
            train.status = status
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
def clone_version(
    repository_id_from_original_version: str,
    original_version_id: int,
    clone_id: int,
    *args,
    **kwargs,
):
    original_version = RepositoryVersion.objects.get(
        pk=original_version_id, repository_id=repository_id_from_original_version
    )
    clone = RepositoryVersion.objects.get(pk=clone_id)

    # Copy version_languages and direct fields
    bulk_version_languages = [
        RepositoryVersionLanguage(**version, pk=None, repository_version=clone)
        for version in original_version.version_languages.values()
    ]
    RepositoryVersionLanguage.objects.bulk_create(
        bulk_version_languages, ignore_conflicts=True
    )

    # Copy version_languages relations (examples, intents, etc)
    for original_version_language in original_version.version_languages:
        clone_version_language = clone.get_version_language(
            original_version_language.language
        )

        clone_version_language.update_trainer(
            original_version_language.get_bot_data.bot_data,
            original_version_language.get_bot_data.rasa_version,
        )

        examples = RepositoryExample.objects.filter(
            repository_version_language=original_version_language
        )

        for original_example in examples:
            intent, created = RepositoryIntent.objects.get_or_create(
                text=original_example.intent.text,
                repository_version=clone_version_language.repository_version,
            )
            example_id = RepositoryExample.objects.create(
                repository_version_language=clone_version_language,
                text=original_example.text,
                intent=intent,
                created_at=original_example.created_at,
                last_update=original_example.last_update,
            )

            example_entities = RepositoryExampleEntity.objects.filter(
                repository_example=original_example
            )

            for example_entity in example_entities:
                if example_entity.entity.group:
                    group, created_group = RepositoryEntityGroup.objects.get_or_create(
                        repository_version=clone,
                        value=example_entity.entity.group.value,
                    )
                    entity, created_entity = RepositoryEntity.objects.get_or_create(
                        repository_version=clone,
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
                        repository_version=clone, value=example_entity.entity.value
                    )
                    RepositoryExampleEntity.objects.create(
                        repository_example=example_id,
                        start=example_entity.start,
                        end=example_entity.end,
                        entity=entity,
                        created_at=example_entity.created_at,
                    )

            translated_examples = RepositoryTranslatedExample.objects.filter(
                original_example=original_example
            )

            for translated_example in translated_examples:
                translated = RepositoryTranslatedExample.objects.create(
                    repository_version_language=clone.get_version_language(
                        translated_example.language
                    ),
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
                        (
                            group,
                            created_group,
                        ) = RepositoryEntityGroup.objects.get_or_create(
                            repository_version=clone,
                            value=translated_entity.entity.group.value,
                        )
                        entity, created_entity = RepositoryEntity.objects.get_or_create(
                            repository_version=clone,
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
                            repository_version=clone,
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
            repository_version_language=original_version_language
        )

        for evaluate in evaluates:
            evaluate_id = RepositoryEvaluate.objects.create(
                repository_version_language=clone_version_language,
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

    clone.is_deleted = False
    clone.save(update_fields=["is_deleted"])
    return True


@app.task()
def clone_repository(
    source_repository_id: str,
    clone_repository_id: str,
    new_owner_id: int,
    language: str = None,
) -> Repository:
    """
    Clone a Repository Instance ans it's related fields.
    Returns a Repository instance or None
    """
    if not language:
        language = "en"

    source_repository = Repository.objects.get(pk=source_repository_id)
    clone_repository = Repository.objects.get(pk=clone_repository_id)

    # region 1. clone Repository and direct fields

    # copy fields from source repository to clone repository
    exclude_fields = ("id", "pk", "uuid", "slug")
    for field in Repository._meta.fields:
        if field.name in exclude_fields or field.primary_key:
            continue
        setattr(clone_repository, field.name, getattr(source_repository, field.name))

    # Keep full name if the field's "max_length" allows it, else crop it
    size = Repository.name.field.max_length
    translation.activate(language)
    name = "{name} [{suffix}]".format(name=source_repository.name, suffix=_("Copy"))
    translation.deactivate()
    if len(name) > size:
        name = name[: size - 3] + "..."
    clone_repository.name = name

    # Update necessary fields
    clone_repository.owner_id = new_owner_id
    clone_repository.is_private = True
    clone_repository.count_authorizations = 0
    clone_repository.created_at = timezone.now()

    clone_repository.save()
    # endregion

    # region 2. ForeignKeys and ManyToManyFields
    clone_repository.categories.set(source_repository.categories.all())

    score_queue = []
    score_exclude_fields = ("id", "pk", "uuid", "repository")
    score_fields = RepositoryScore._meta.fields
    for original_score in source_repository.repository_score.all():
        clone_score = RepositoryScore(repository=clone_repository)
        # copy fields and values
        for field in score_fields:
            if not (field.name in score_exclude_fields or field.primary_key):
                setattr(clone_score, field.name, getattr(original_score, field.name))
        score_queue.append(clone_score)
    RepositoryScore.objects.bulk_create(score_queue)
    # endregion

    # region 3. reverse ForeignKeys and ManyToManyFields (the ones which reference the Repository)
    for knowledge_base in source_repository.knowledge_bases.all():
        knowledge_base.pk = None
        knowledge_base.repository = clone_repository
        knowledge_base.save()
    # endregion

    return clone_repository.pk


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
    repository_version, source_language, target_language, selected_ids, *args, **kwargs
):

    repository_version = RepositoryVersion.objects.get(pk=repository_version)

    task_queue = repository_version.get_version_language(
        language=target_language
    ).create_task(
        id_queue=app.current_task.request.id,
        from_queue=RepositoryQueueTask.QUEUE_CELERY,
        type_processing=RepositoryQueueTask.TYPE_PROCESSING_AUTO_TRANSLATE,
    )
    if len(selected_ids) > 0:
        examples = (
            RepositoryExample.objects.filter(
                repository_version_language__repository_version=repository_version,
                repository_version_language__language=source_language,
                pk__in=selected_ids
            )
            .annotate(
                translation_count=Count(
                    "translations", filter=Q(translations__language=target_language)
                )
            )
            .filter(translation_count=0)
        )
    else:
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
def get_project_organization(
    project_uuid: str, user_email: str = ""
):  # pragma: no cover
    grpc_client = ConnectClient()
    if settings.USE_GRPC:
        authorizations = grpc_client.list_authorizations(project_uuid=project_uuid)
    else:
        authorizations = grpc_client.list_authorizations(
            project_uuid=project_uuid, user_email=user_email
        )
    return authorizations


@app.task(name="remove_authorizations_project")
def remove_authorizations_project(
    project_uuid: str, authorizations_uuids: list, user_email: str
):
    grpc_client = ConnectClient()
    for authorization_uuid in authorizations_uuids:
        grpc_client.remove_authorization(project_uuid, authorization_uuid, user_email)


@app.task(name="create_repository_project")
def create_repository_project(**kwargs):
    grpc_client = ConnectClient()
    grpc_client.create_classifier(**kwargs)
    return kwargs


@app.task(name="send_recent_activity")
def send_recent_activity(recent_activity_data):
    rabbitmq_publisher = RabbitMQPublisher()
    rabbitmq_publisher.send_message(
        body=recent_activity_data,
        exchange="recent-activities.topic",
        routing_key="",
    )
    print(f"[ intelligencePublisher ] message sent - {recent_activity_data} to recent-activities.topic")
