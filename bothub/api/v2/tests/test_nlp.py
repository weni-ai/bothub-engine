import json

from django.test import RequestFactory
from django.test import TestCase
from rest_framework import status

from bothub.api.v2.nlp.views import RepositoryAuthorizationInfoViewSet
from bothub.api.v2.nlp.views import RepositoryAuthorizationTrainViewSet
from bothub.common import languages
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity
from bothub.common.models import RepositoryUpdate
from .utils import create_user_and_token


class TrainStartTrainingTestCase(TestCase):
    fixtures = ["permissions.json"]

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

        self.repository_authorization = self.repository.get_user_authorization(
            self.user, "Owner"
        )

        self.repository_update = RepositoryUpdate.objects.create(
            repository=self.repository,
            language=languages.LANGUAGE_EN,
            algorithm="statistical_model",
        )

    def request(self, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Bearer {}".format(token)}
        request = self.factory.post(
            "/v2/repository/nlp/authorization/train/start_training/",
            json.dumps(
                {"update_id": self.repository_update.pk, "by_user": self.user.pk}
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


class TrainGetTextTestCase(TestCase):
    fixtures = ["permissions.json"]

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

        self.repository_authorization = self.repository.get_user_authorization(
            self.owner, "Owner"
        )

        self.repository_update = RepositoryUpdate.objects.create(
            repository=self.repository,
            language=languages.LANGUAGE_EN,
            algorithm="statistical_model",
        )

        self.repository_examples = RepositoryExample.objects.create(
            repository_update=self.repository_update, text="hello", intent="greet"
        )

    def request(self, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Bearer {}".format(token)}
        request = self.factory.get(
            "/v2/repository/nlp/authorization/train/get_text/"
            "?update_id={}&example_id={}&language={}".format(
                self.repository_update.pk,
                self.repository_examples.pk,
                languages.LANGUAGE_EN,
            ),
            **authorization_header
        )
        response = RepositoryAuthorizationTrainViewSet.as_view({"get": "get_text"})(
            request
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(str(self.repository_authorization.uuid))
        self.assertEqual(content_data.get("get_text"), "hello")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_auth(self):
        response, content_data = self.request("NO-TOKEN")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TrainGetEntitiesTestCase(TestCase):
    fixtures = ["permissions.json"]

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

        self.repository_authorization = self.repository.get_user_authorization(
            self.owner, "Owner"
        )

        self.repository_update = RepositoryUpdate.objects.create(
            repository=self.repository,
            language=languages.LANGUAGE_EN,
            algorithm="statistical_model",
        )

        self.repository_examples = RepositoryExample.objects.create(
            repository_update=self.repository_update, text="hello", intent="greet"
        )

        RepositoryExampleEntity.objects.create(
            repository_example=self.repository_examples, start=11, end=18, entity="name"
        )

    def request(self, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Bearer {}".format(token)}
        request = self.factory.get(
            "/v2/repository/nlp/authorization/train/get_entities/"
            "?update_id={}&example_id={}&language={}".format(
                self.repository_update.pk,
                self.repository_examples.pk,
                languages.LANGUAGE_EN,
            ),
            **authorization_header
        )
        response = RepositoryAuthorizationTrainViewSet.as_view({"get": "get_entities"})(
            request
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(str(self.repository_authorization.uuid))
        self.assertEqual(len(content_data.get("entities")), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_auth(self):
        response, content_data = self.request("NO-TOKEN")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TrainFailTestCase(TestCase):
    fixtures = ["permissions.json"]

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

        self.repository_authorization = self.repository.get_user_authorization(
            self.owner, "Owner"
        )

        self.repository_update = RepositoryUpdate.objects.create(
            repository=self.repository,
            language=languages.LANGUAGE_EN,
            algorithm="statistical_model",
        )

    def request(self, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Bearer {}".format(token)}
        request = self.factory.post(
            "/v2/repository/nlp/authorization/train/train_fail/",
            json.dumps({"update_id": self.repository_update.pk}),
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
            RepositoryUpdate.objects.get(pk=self.repository_update.pk).failed_at
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_auth(self):
        response, content_data = self.request("NO-TOKEN")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizationInfoTestCase(TestCase):
    fixtures = ["permissions.json"]

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

        self.repository_authorization = self.repository.get_user_authorization(
            self.owner, "Owner"
        )

        self.repository_update = RepositoryUpdate.objects.create(
            repository=self.repository,
            language=languages.LANGUAGE_EN,
            algorithm="statistical_model",
        )

        self.repository_examples = RepositoryExample.objects.create(
            repository_update=self.repository_update, text="hello", intent="greet"
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
