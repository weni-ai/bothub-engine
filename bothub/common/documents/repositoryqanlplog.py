import json

from django.conf import settings
from django_elasticsearch_dsl import Index, fields
from bothub.utils import TimeBasedDocument

from bothub.common.models import QALogs

REPOSITORYQANLPLOG_INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])


@REPOSITORYQANLPLOG_INDEX.doc_type
class RepositoryQANLPLogDocument(TimeBasedDocument):
    _time_based = True

    user = fields.IntegerField(attr="user.id")
    knowledge_base = fields.IntegerField(attr="knowledge_base.id")
    nlp_log = fields.NestedField(
        properties={
            "answers": fields.NestedField(
                properties={
                    "text": fields.TextField(fields={"raw": fields.KeywordField()}),
                    "confidence": fields.FloatField(),
                }
            ),
            "id": fields.IntegerField(),
        }
    )
    text = fields.IntegerField()
    repository_uuid = fields.TextField(
        fields={"raw": fields.KeywordField()},
    )

    pk = fields.IntegerField()

    class Django:
        model = QALogs
        fields = [
            "id",
            "answer",
            "language",
            "confidence",
            "question",
            "from_backend",
            "user_agent",
            "created_at",
        ]

    def prepare_text(self, obj):
        try:
            return obj.knowledge_base.texts.filter(language=obj.language).first().id
        except AttributeError:
            return None

    def prepare_nlp_log(self, obj):
        return json.loads(obj.nlp_log)

    def prepare_repository_uuid(self, obj):
        return obj.knowledge_base.repository.uuid
