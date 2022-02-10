import json
from datetime import datetime

from django.conf import settings
from django_elasticsearch_dsl import Document, Index, fields

from bothub.common.models import RepositoryNLPLog

REPOSITORYNLPLOG_INDEX_NAME = settings.ELASTICSEARCH_INDEX_NAMES[__name__]
REPOSITORYNLPLOG_INDEX = Index(REPOSITORYNLPLOG_INDEX_NAME)


@REPOSITORYNLPLOG_INDEX.doc_type
class RepositoryNLPLogDocument(Document):
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

    # def save(self, **kwargs):
    #     # assign now if no timestamp given
    #     if not self.timestamp:
    #         self.timestamp = self.created_at

    #     # override the index to go to the proper timeslot
    #     index = REPOSITORYNLPLOG_INDEX_NAME.replace("*", "%Y%m%d")
    #     kwargs["index"] = self.timestamp.strftime(index)
    #     return super().save(**kwargs)

    def prepare_nlp_log(self, obj):
        return json.loads(obj.nlp_log)

    def prepare_version_name(self, obj):
        return obj.repository_version_language.repository_version.name
