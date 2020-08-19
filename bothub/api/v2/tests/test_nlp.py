import json

from django.test import TestCase
from django.test import RequestFactory
from rest_framework import status

from bothub.api.v2.nlp.views import RepositoryAuthorizationTrainViewSet
from bothub.api.v2.nlp.views import RepositoryAuthorizationInfoViewSet
from bothub.common import languages
from bothub.common.models import (
    RepositoryAuthorization,
    RepositoryVersion,
    RepositoryVersionLanguage, RepositoryIntent,
)
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity
from bothub.common.models import Repository

from .utils import create_user_and_token


class TrainStartTrainingTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.repository_authorization = RepositoryAuthorization.objects.create(
            user=self.user, repository=self.repository, role=3
        )

        self.repository_version = RepositoryVersion.objects.create(
            repository=self.repository, name="test"
        )

        self.repository_version_language = RepositoryVersionLanguage.objects.create(
            repository_version=self.repository_version,
            language=languages.LANGUAGE_EN,
            algorithm="neural_network_internal",
        )

    def request(self, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Bearer {}".format(token)}
        request = self.factory.post(
            "/v2/repository/nlp/authorization/train/start_training/",
            json.dumps(
                {
                    "repository_version": self.repository_version_language.pk,
                    "by_user": self.user.pk,
                    "from_queue": "celery",
                }
            ),
            content_type="application/json",
            **authorization_header
        )
        response = RepositoryAuthorizationTrainViewSet.as_view(
            {"post": "start_training"}
        )(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(str(self.repository_authorization.uuid))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_auth(self):
        response, content_data = self.request("NO-TOKEN")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TrainFailTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.repository_authorization = RepositoryAuthorization.objects.create(
            user=self.user, repository=self.repository, role=3
        )

        self.repository_version = RepositoryVersion.objects.create(
            repository=self.repository, name="test"
        )

        self.repository_version_language = RepositoryVersionLanguage.objects.create(
            repository_version=self.repository_version,
            language=languages.LANGUAGE_EN,
            algorithm="neural_network_internal",
        )

    def request(self, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Bearer {}".format(token)}
        request = self.factory.post(
            "/v2/repository/nlp/authorization/train/train_fail/",
            json.dumps({"repository_version": self.repository_version_language.pk}),
            content_type="application/json",
            **authorization_header
        )
        response = RepositoryAuthorizationTrainViewSet.as_view({"post": "train_fail"})(
            request
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(str(self.repository_authorization.uuid))
        self.assertIsNotNone(
            RepositoryVersionLanguage.objects.get(
                pk=self.repository_version_language.pk
            ).failed_at
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_auth(self):
        response, content_data = self.request("NO-TOKEN")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizationInfoTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.repository_authorization = RepositoryAuthorization.objects.create(
            user=self.user, repository=self.repository, role=3
        )

        self.repository_version = RepositoryVersion.objects.create(
            repository=self.repository, name="test"
        )

        self.repository_version_language = RepositoryVersionLanguage.objects.create(
            repository_version=self.repository_version,
            language=languages.LANGUAGE_EN,
            algorithm="neural_network_internal",
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository_version
        )

        self.repository_examples = RepositoryExample.objects.create(
            repository_version_language=self.repository_version_language,
            text="hello",
            intent=self.example_intent_1,
        )

        self.repository_entity = RepositoryExampleEntity.objects.create(
            repository_example=self.repository_examples, start=11, end=18, entity="name"
        )

    def request(self, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Bearer {}".format(token)}
        request = self.factory.get(
            "/v2/repository/nlp/authorization/info/{}/".format(token),
            **authorization_header
        )
        response = RepositoryAuthorizationInfoViewSet.as_view({"get": "retrieve"})(
            request, pk=token
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(str(self.repository_authorization.uuid))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_auth(self):
        response, content_data = self.request("NO-TOKEN")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
