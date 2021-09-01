import json

from django.test import TestCase
from django.test import tag
from django_elasticsearch_dsl.registries import registry
from rest_framework import status

from bothub.api.v2.tests.test_knowledge_base import DefaultSetUpKnowledgeBaseMixin
from bothub.common.models import QALogs
from bothub.api.v2.repository.views import RepositoryQANLPLogViewSet
from bothub.api.v2.nlp.views import RepositoryQANLPLogsViewSet


class QALogsTestCase(DefaultSetUpKnowledgeBaseMixin, TestCase):
    def request(self, data={}, token=None):
        request = self.factory.post(
            "/v2/repository/nlp/qa/log/", json.dumps(data), content_type="application/json"
        )

        response = RepositoryQANLPLogsViewSet.as_view({"post": "create"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        data = {
            "context": self.context_1.pk,
            "question": "teste",
            "answer": "teste",
            "confidence": 0.0505176697224809,
            "user_agent": "python-requests/2.20.1",
            "nlp_log": json.dumps(
                {
                    "answers": [
                        {
                        "text": "test",
                        "confidence": 0.0505176697224809
                        },
                        {
                        "text": "empty",
                        "confidence": 0.0005176697224809
                        },
                    ],
                    "id": 0
                }
            ),
            "from_backend": True,
            "user": str(self.repository_auth.pk),
        }
        response, content_data = self.request(data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(data.get("user_agent"), content_data.get("user_agent"))
        self.assertEqual(data.get("answer"), content_data.get("answer"))
        self.assertEqual(data.get("question"), content_data.get("question"))
        self.assertEqual(
            data.get("nlp_log"), content_data.get("nlp_log")
        )


@tag(
    "elastic"
)  # Need to run separately, running with the other tests will make this test fail
class ListQALogTestCase(DefaultSetUpKnowledgeBaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.log = QALogs.objects.create(
            context= self.context_1,
            question= "test",
            answer="test",
            confidence= 0.0505176697224809,
            user_agent= "python-requests/2.20.1",
            from_backend= True,
            nlp_log=json.dumps(
                {
                    "answers": [
                        {"text": "biases", "confidence": 0.9994810819625854},
                        {"text": "doubtes", "confidence": 0.039212167263031006},
                        {"text": "negativees", "confidence": 0.0},
                        {"text": "affirmativees", "confidence": 0.0},
                    ],
                    "id": 0,
                }
            ),
            user= self.owner,
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
        self.assertEqual(content_data.get("results")[0].get("confidence"), 0.0505176697224809)
