import json
import requests

from django.conf import settings
from django.test import RequestFactory
from django.test import tag
from django.test import TestCase
from django_elasticsearch_dsl.registries import registry
from rest_framework import status

from bothub.api.v2.nlp.views import RepositoryNLPLogsViewSet
from bothub.api.v2.repository.views import RepositoryNLPLogViewSet
from bothub.api.v2.tests.utils import create_user_and_token
from bothub.common import languages
from bothub.common.models import (
    Repository,
    RepositoryAuthorization,
    RepositoryNLPLog,
    RepositoryNLPLogIntent,
    RepositoryIntent,
)
from bothub.common.models import RepositoryExample
from bothub.common.documents.repositorynlplog import REPOSITORYNLPLOG_INDEX_NAME


@tag("elastic")
class RepositoryNLPLogTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="bias",
            repository_version=self.repository.current_version().repository_version,
        )
        self.example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=self.example_intent_1,
        )

        self.repository_auth = RepositoryAuthorization.objects.create(
            user=self.owner, repository=self.repository, role=3
        )

    def request(self, data):
        request = self.factory.post(
            "/v2/repository/nlp/log/", json.dumps(data), content_type="application/json"
        )
        response = RepositoryNLPLogsViewSet.as_view({"post": "create"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def list_request(self, data, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )
        request = self.factory.get("/v2/repository/log/", data, **authorization_header)
        response = RepositoryNLPLogViewSet.as_view({"get": "list"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_blocked_user(self):
        with self.settings(REPOSITORY_BLOCK_USER_LOGS=[self.repository_auth.pk]):
            data = {
                "text": "test",
                "user_agent": "python-requests/2.20.1",
                "from_backend": True,
                "user": str(self.repository_auth.pk),
                "repository_version_language": int(
                    self.repository.current_version().pk
                ),
                "nlp_log": json.dumps(
                    {
                        "intent": {"name": "bias", "confidence": 0.9994810819625854},
                        "intent_ranking": [
                            {"name": "bias", "confidence": 0.9994810819625854},
                            {"name": "doubt", "confidence": 0.039212167263031006},
                            {"name": "negative", "confidence": 0.0},
                            {"name": "affirmative", "confidence": 0.0},
                        ],
                        "labels_list": [],
                        "entities_list": [],
                        "entities": {},
                        "text": "test",
                        "repository_version": int(self.repository.current_version().pk),
                        "language": str(self.repository.language),
                    }
                ),
                "log_intent": [],
            }
            self.request(data)
            response, content_data = self.list_request(
                {
                    "repository_version_language": int(
                        self.repository.current_version().pk
                    )
                },
                self.owner_token,
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(content_data.get("count"), 0)

    def test_okay(self):
        data = {
            "text": "test",
            "user_agent": "python-requests/2.20.1",
            "from_backend": True,
            "user": str(self.repository_auth.pk),
            "repository_version_language": int(self.repository.current_version().pk),
            "nlp_log": json.dumps(
                {
                    "intent": {"name": "bias", "confidence": 0.9994810819625854},
                    "intent_ranking": [
                        {"name": "bias", "confidence": 0.9994810819625854},
                        {"name": "doubt", "confidence": 0.039212167263031006},
                        {"name": "negative", "confidence": 0.0},
                        {"name": "affirmative", "confidence": 0.0},
                    ],
                    "labels_list": [],
                    "entities_list": [],
                    "entities": {},
                    "text": "test",
                    "repository_version": int(self.repository.current_version().pk),
                    "language": str(self.repository.language),
                }
            ),
            "log_intent": [],
        }
        response, content_data = self.request(data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(data.get("user_agent"), content_data.get("user_agent"))
        self.assertEqual(data.get("text"), content_data.get("text"))
        self.assertEqual(data.get("nlp_log"), content_data.get("nlp_log"))
        self.assertEqual(
            data.get("repository_version"), content_data.get("repository_version")
        )
        self.assertEqual(data.get("language"), content_data.get("language"))


@tag(
    "elastic"
)  # Need to run separately, running with the other tests was making this test fail
class ListRepositoryNLPLogTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.owner, self.owner_token = create_user_and_token("owneres")

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing Elasticsearch",
            slug="testinges",
            language=languages.LANGUAGE_EN,
        )
        self.example_intent_1 = RepositoryIntent.objects.create(
            text="biases",
            repository_version=self.repository.current_version().repository_version,
        )
        self.example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hies",
            intent=self.example_intent_1,
        )

        nlp_log = RepositoryNLPLog.objects.create(
            id=2,
            text="testes",
            user_agent="python-requests/2.20.1",
            from_backend=True,
            repository_version_language=self.repository.current_version(),
            nlp_log=json.dumps(
                {
                    "intent": {"name": "biases", "confidence": 0.9994810819625854},
                    "intent_ranking": [
                        {"name": "biases", "confidence": 0.9994810819625854},
                        {"name": "doubtes", "confidence": 0.039212167263031006},
                        {"name": "negativees", "confidence": 0.0},
                        {"name": "affirmativees", "confidence": 0.0},
                    ],
                    "labels_list": [],
                    "entities_list": [],
                    "entities": {},
                    "text": "testes",
                    "repository_version": int(self.repository.current_version().pk),
                    "language": str(self.repository.language),
                }
            ),
            user=self.owner,
        )

        RepositoryNLPLogIntent.objects.create(
            intent="biases",
            confidence=0.9994810819625854,
            is_default=True,
            repository_nlp_log=nlp_log,
        )

        RepositoryNLPLogIntent.objects.create(
            intent="doubtes",
            confidence=0.039212167263031006,
            is_default=False,
            repository_nlp_log=nlp_log,
        )

        RepositoryNLPLogIntent.objects.create(
            intent="negativees",
            confidence=0.0,
            is_default=False,
            repository_nlp_log=nlp_log,
        )

        RepositoryNLPLogIntent.objects.create(
            intent="affirmativees",
            confidence=0.0,
            is_default=False,
            repository_nlp_log=nlp_log,
        )
        requests.delete(
            f"{settings.ELASTICSEARCH_DSL['default']['hosts']}/_data_stream/{REPOSITORYNLPLOG_INDEX_NAME}"
        )
        registry.update(nlp_log)

    def request(self, data, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )
        request = self.factory.get("/v2/repository/log/", data, **authorization_header)
        response = RepositoryNLPLogViewSet.as_view({"get": "list"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {"repository_version_language": int(self.repository.current_version().pk)},
            self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 1)
        self.assertEqual(len(content_data.get("results")[0].get("log_intent")), 4)
