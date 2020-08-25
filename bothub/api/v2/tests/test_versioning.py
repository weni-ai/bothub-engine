import json

from django.test import RequestFactory
from django.test import TestCase
from rest_framework import status

from bothub.api.v2.tests.utils import create_user_and_token
from bothub.api.v2.versionning.views import RepositoryVersionViewSet
from bothub.common import languages
from bothub.common.models import (
    Repository,
    RepositoryExample,
    RepositoryVersionLanguage,
    RepositoryVersion,
    RepositoryIntent,
)


# class CloneRepositoryVersionAPITestCase(TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#
#         self.owner, self.owner_token = create_user_and_token("owner")
#         self.user, self.user_token = create_user_and_token("user")
#
#         self.repository = Repository.objects.create(
#             owner=self.owner,
#             name="Repository 1",
#             slug="repo",
#             language=languages.LANGUAGE_EN,
#         )
#
#         self.example_1 = RepositoryExample.objects.create(
#             repository_version_language=self.repository.current_version(),
#             text="hi",
#             intent="greet",
#         )
#
#         self.example_translated = RepositoryTranslatedExample.objects.create(
#             original_example=self.example_1, language=languages.LANGUAGE_PT, text="oi"
#         )
#
#         self.entity_1 = RepositoryExampleEntity.objects.create(
#             repository_example=self.example_1, start=0, end=0, entity="hi"
#         )
#         self.entity_1.entity.set_group("greet")
#         self.entity_1.entity.save()
#
#     def request(self, data, token=None):
#         authorization_header = (
#             {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
#         )
#
#         request = self.factory.post(
#             "/v2/repository/version/", data, **authorization_header
#         )
#
#         response = RepositoryVersionViewSet.as_view({"post": "create"})(
#             request, pk=self.repository.current_version().repository_version.pk
#         )
#         response.render()
#         content_data = json.loads(response.content)
#         return (response, content_data)
#
#     def test_okay(self):
#         response, content_data = self.request(
#             {
#                 "repository": str(self.repository.pk),
#                 "id": self.repository.current_version().repository_version.pk,
#                 "name": "test",
#             },
#             self.owner_token,
#         )
#
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#
#         version = RepositoryVersion.objects.filter(
#             pk=content_data.get("id"), repository=self.repository
#         )
#
#         self.assertEqual(version.count(), 1)
#
#         version_language = RepositoryVersionLanguage.objects.filter(
#             repository_version=version.first(), language=languages.LANGUAGE_EN
#         )
#
#         self.assertEqual(version_language.count(), 1)
#
#         example = RepositoryExample.objects.filter(
#             repository_version_language=version_language.first()
#         ).first()
#
#         self.assertEqual(example.text, self.example_1.text)
#         self.assertEqual(example.intent, self.example_1.intent)
#
#         example_translated = RepositoryTranslatedExample.objects.filter(
#             repository_version_language=version_language.first()
#         ).first()
#
#         self.assertEqual(example_translated.text, self.example_translated.text)
#
#     def test_only_letters_and_number(self):
#         response, content_data = self.request(
#             {
#                 "repository": str(self.repository.pk),
#                 "id": self.repository.current_version().repository_version.pk,
#                 "name": "testversion#",
#             },
#             self.owner_token,
#         )
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#
#     def test_exist(self):
#         response, content_data = self.request(
#             {
#                 "repository": str(self.repository.pk),
#                 "id": self.repository.current_version().repository_version.pk,
#                 "name": "master",
#             },
#             self.owner_token,
#         )
#
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ListRepositoryVersionAPITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.user_token = create_user_and_token("user")

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Repository 1",
            slug="repo",
            language=languages.LANGUAGE_EN,
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )

        self.example_1 = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=self.example_intent_1,
        )

    def request(self, data={}, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.get(
            "/v2/repository/version/", data, **authorization_header
        )

        response = RepositoryVersionViewSet.as_view({"get": "list"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {"repository": self.repository.uuid}, self.owner_token
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_repository_no_exist(self):
        response, content_data = self.request(
            {"repository": "00000000-0000-0000-0000-000000000000"}, self.owner_token
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DefaultRepositoryVersionAPITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.user_token = create_user_and_token("user")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Repository 1",
            slug="repo",
            language=languages.LANGUAGE_EN,
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )

        self.example_1 = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=self.example_intent_1,
        )

        self.version = RepositoryVersion.objects.create(
            name=self.repository.current_version().repository_version.name,
            last_update=self.repository.current_version().repository_version.last_update,
            is_default=False,
            repository=self.repository.current_version().repository_version.repository,
            created_by=self.repository.current_version().repository_version.created_by,
        )

        self.version_language = RepositoryVersionLanguage.objects.create(
            language=self.repository.current_version().language,
            training_started_at=self.repository.current_version().training_started_at,
            training_end_at=self.repository.current_version().training_end_at,
            failed_at=self.repository.current_version().failed_at,
            use_analyze_char=self.repository.current_version().use_analyze_char,
            use_name_entities=self.repository.current_version().use_name_entities,
            use_competing_intents=self.repository.current_version().use_competing_intents,
            algorithm=self.repository.current_version().algorithm,
            repository_version=self.version,
            training_log=self.repository.current_version().training_log,
            last_update=self.repository.current_version().last_update,
            total_training_end=self.repository.current_version().total_training_end,
        )
        self.version_language.update_trainer(
            self.repository.current_version().get_bot_data.bot_data,
            self.repository.current_version().get_bot_data.rasa_version,
        )

    def request(self, version, token, data):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.patch(
            "/v2/repository/version/{}/".format(version.pk),
            json.dumps(data),
            content_type="application/json",
            **authorization_header,
        )
        response = RepositoryVersionViewSet.as_view({"patch": "update"})(
            request, pk=version.pk
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        self.assertEqual(self.version.is_default, False)
        response, content_data = self.request(
            self.version,
            self.owner_token,
            {
                "repository": str(self.repository.uuid),
                "id": self.version.pk,
                "name": "test",
                "is_default": True,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        version = RepositoryVersion.objects.get(pk=self.version.pk)

        self.assertEqual(version.is_default, True)
