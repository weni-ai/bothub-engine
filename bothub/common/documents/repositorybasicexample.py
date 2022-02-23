from django.conf import settings
from django_elasticsearch_dsl import Document, Index, fields

from bothub.common.models import (
    RepositoryExample,
    RepositoryExampleEntity,
    RepositoryIntent,
    RepositoryVersionLanguage,
)

REPOSITORYBASICEXAMPLE_INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])


@REPOSITORYBASICEXAMPLE_INDEX.doc_type
class RepositoryExampleDocument(Document):
    _time_based = False

    repository_version_language = fields.ObjectField(
        properties={
            "pk": fields.IntegerField(),
            "language": fields.TextField(fields={"raw": fields.KeywordField()}),
        }
    )
    intent = fields.ObjectField(
        properties={"text": fields.TextField(fields={"raw": fields.KeywordField()})}
    )
    entities = fields.NestedField(
        properties={
            "entity": fields.ObjectField(
                properties={
                    "value": fields.TextField(fields={"raw": fields.KeywordField()}),
                }
            ),
        }
    )
    pk = fields.IntegerField()

    class Django:
        model = RepositoryExample
        fields = [
            "id",
            "text",
        ]
        related_models = [
            RepositoryVersionLanguage,
            RepositoryIntent,
            RepositoryExampleEntity,
        ]

    def get_queryset(self):
        return (
            super(RepositoryExampleDocument, self)
            .get_queryset()
            .select_related(
                "repository_version_language",
                "intent",
            )
            .prefetch_related(
                "entities",
                "translations",
            )
        )

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, RepositoryVersionLanguage):
            return related_instance.added.all()
        elif isinstance(related_instance, RepositoryIntent):
            return related_instance.repositoryexample_set.all()
        elif isinstance(related_instance, RepositoryExampleEntity):
            return related_instance.repository_example
