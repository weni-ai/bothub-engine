import json

from django.conf import settings
from django_elasticsearch_dsl import Index, fields
from bothub.common.models import RepositoryNLPLog
from bothub.utils import TimeBasedDocument

REPOSITORYNLPLOG_INDEX_NAME = settings.ELASTICSEARCH_INDEX_NAMES[__name__]
REPOSITORYNLPLOG_INDEX = Index(REPOSITORYNLPLOG_INDEX_NAME)


@REPOSITORYNLPLOG_INDEX.document
class RepositoryNLPLogDocument(TimeBasedDocument):
    time_based = True

    user = fields.IntegerField(attr="user.id")
    log_intent = fields.NestedField(
        attr="log_intent_field_indexing",
        properties={
            "intent": fields.TextField(fields={"raw": fields.KeywordField()}),
            "confidence": fields.FloatField(),
            "is_default": fields.BooleanField(),
        },
    )

    nlp_log = fields.NestedField(
        properties={
            "intent": fields.ObjectField(
                properties={
                    "name": fields.TextField(fields={"raw": fields.KeywordField()}),
                    "confidence": fields.FloatField(),
                }
            ),
            "intent_ranking": fields.NestedField(
                properties={
                    "name": fields.TextField(fields={"raw": fields.KeywordField()}),
                    "confidence": fields.FloatField(),
                }
            ),
            "entities": fields.NestedField(),
            "label_list": fields.TextField(multi=True),
            "entities_list": fields.TextField(multi=True),
            "text": fields.TextField(),
            "language": fields.TextField(),
            "repository_version": fields.IntegerField(),
        }
    )

    version_name = fields.TextField(
        attr="repository_version_language_field_indexing.version_name",
        fields={"raw": fields.KeywordField()},
    )
    repository_uuid = fields.TextField(
        attr="repository_version_language_field_indexing.repository",
        fields={"raw": fields.KeywordField()},
    )
    language = fields.TextField(
        attr="repository_version_language_field_indexing.language",
        fields={"raw": fields.KeywordField()},
    )
    repository_version_language = fields.IntegerField(
        attr="repository_version_language_field_indexing.repository_version_language"
    )
    repository_version = fields.IntegerField(
        attr="repository_version_language_field_indexing.version"
    )

    pk = fields.IntegerField()

    class Django:
        model = RepositoryNLPLog
        fields = ["id", "text", "from_backend", "user_agent", "created_at"]

    def prepare_nlp_log(self, obj):
        return json.loads(obj.nlp_log)

    def prepare_version_name(self, obj):
        return obj.repository_version_language.repository_version.name
