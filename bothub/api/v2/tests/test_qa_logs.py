import json
import requests

from django.conf import settings
from django.test import TestCase
from django.test import tag
from django_elasticsearch_dsl.registries import registry
from rest_framework import status

from bothub.api.v2.tests.test_knowledge_base import DefaultSetUpKnowledgeBaseMixin
from bothub.common.models import QALogs
from bothub.api.v2.repository.views import RepositoryQANLPLogViewSet
from bothub.api.v2.nlp.views import RepositoryQANLPLogsViewSet
from bothub.common.documents.repositoryqanlplog import REPOSITORYQANLPLOG_INDEX_NAME


class QALogsTestCase(DefaultSetUpKnowledgeBaseMixin, TestCase):
    def request(self, data={}, token=None):
        request = self.factory.post(
            "/v2/repository/nlp/qa/log/",
            json.dumps(data),
            content_type="application/json",
        )

        response = RepositoryQANLPLogsViewSet.as_view({"post": "create"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        data = {
            "answer": "teste",
            "confidence": 0.0505176697224809,
            "question": "teste",
            "user_agent": "python-requests/2.20.1",
            "nlp_log": json.dumps(
                {
                    "answers": [
                        {"text": "test", "confidence": 0.0505176697224809},
                        {"text": "empty", "confidence": 0.0005176697224809},
                    ],
                    "id": 0,
                }
            ),
            "user": str(self.repository_auth.pk),
            "knowledge_base": self.knowledge_base_1.pk,
            "language": self.context_2.language,
            "from_backend": True,
        }
        response, content_data = self.request(data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(data.get("user_agent"), content_data.get("user_agent"))
        self.assertEqual(data.get("answer"), content_data.get("answer"))
        self.assertEqual(data.get("question"), content_data.get("question"))
        self.assertEqual(data.get("nlp_log"), content_data.get("nlp_log"))


@tag(
    "elastic"
)  # Need to run separately, running with the other tests will make this test fail
class ListQALogTestCase(DefaultSetUpKnowledgeBaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        requests.delete(
            f"{settings.ELASTICSEARCH_DSL['default']['hosts']}/_data_stream/{REPOSITORYQANLPLOG_INDEX_NAME}"
        )
        self.log = QALogs.objects.create(
            id=2,
            knowledge_base=self.knowledge_base_1,
            question="t2est",
            answer="te123st",
            language=self.context_1.language,
            confidence=0.0505176697224809,
            user_agent="python-requests/2.20.1",
            from_backend=True,
            nlp_log=json.dumps(
                {
                    "answers": [
                        {"text": "bias123es", "confidence": 0.9994810819625854},
                        {"text": "dou1123btes", "confidence": 0.039212167263031006},
                        {"text": "negat123ivees", "confidence": 0.0},
                        {"text": "affir132mativees", "confidence": 0.0},
                    ],
                    "id": 1,
                }
            ),
            user=self.owner,
        )
        registry.update(self.log)

    def request(self, data, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )
        request = self.factory.get("/v2/qalog", data, **authorization_header)
        response = RepositoryQANLPLogViewSet.as_view({"get": "list"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {"context": int(self.context_1.pk)},
            self.owner_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 1)
        self.assertEqual(
            content_data.get("results")[0].get("confidence"), 0.0505176697224809
        )
