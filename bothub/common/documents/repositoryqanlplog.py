import json

from django.conf import settings
from django_elasticsearch_dsl import Document, Index, fields

from bothub.common.models import QALogs

REPOSITORYQANLPLOG_INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES[__name__])


@REPOSITORYQANLPLOG_INDEX.doc_type
class RepositoryQANLPLogDocument(Document):
    user = fields.IntegerField(attr="user.id")
    context = fields.IntegerField(attr="context.id")
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
    language = fields.TextField(
        attr="context_indexing.language",
        fields={"raw": fields.KeywordField()},
    )
    knowledge_base = fields.IntegerField(
        attr="context_indexing.knowledge_base"
    )
    repository_uuid = fields.TextField(
        attr="context_indexing.repository",
        fields={"raw": fields.KeywordField()},
    )

    pk = fields.IntegerField()

    class Django:
        model = QALogs
        fields = ["id", "answer", "confidence", "question", "from_backend", "user_agent", "created_at"]

    def prepare_nlp_log(self, obj):
        return json.loads(obj.nlp_log)