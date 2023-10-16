import json

from django.conf import settings
from django_elasticsearch_dsl import Index, fields
from bothub.utils import TimeBasedDocument

from bothub.common.models import ZeroshotLogs

REPOSITORYQANLPLOG_INDEX_NAME = settings.ELASTICSEARCH_INDEX_NAMES[__name__]
REPOSITORYQANLPLOG_INDEX = Index(REPOSITORYQANLPLOG_INDEX_NAME)


@REPOSITORYQANLPLOG_INDEX.doc_type
class ZeroshotLogDocument(TimeBasedDocument):
    time_based = True

    text = fields.TextField(
        analyzer='english',
        fields={
            'raw': fields.KeywordField()
        }
    )
    classification = fields.TextField(
        analyzer='english'
    )
    other = fields.BooleanField()
    categories = fields.ObjectField(properties={
        'name': fields.TextField(),
        'value': fields.FloatField()
    })
    nlp_log = fields.TextField(
        analyzer='english'
    )
    created_at = fields.DateField()

    class Django:
        model = ZeroshotLogs
        fields = [
            "id",
            "text",
            "categories",
            "classification",
            "other",
            "created_at",
        ]

