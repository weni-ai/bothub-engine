import json
import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.test import TestCase
from django.test.client import MULTIPART_CONTENT
from rest_framework import status

from bothub.api.v2.repository.serializers import NewRepositorySerializer
from bothub.api.v2.repository.views import (
    RepositoriesContributionsViewSet,
    RepositoryEntitiesViewSet,
    NewRepositoryViewSet,
    RepositoryIntentViewSet,
    RepositoryTrainInfoViewSet,
    RepositoryExamplesBulkViewSet,
)
from bothub.api.v2.repository.views import RepositoriesViewSet
from bothub.api.v2.repository.views import RepositoryAuthorizationRequestsViewSet
from bothub.api.v2.repository.views import RepositoryAuthorizationViewSet
from bothub.api.v2.repository.views import RepositoryCategoriesView
from bothub.api.v2.repository.views import RepositoryExampleViewSet
from bothub.api.v2.repository.views import RepositoryViewSet
from bothub.api.v2.repository.views import RepositoryVotesViewSet
from bothub.api.v2.repository.views import SearchRepositoriesViewSet
from bothub.api.v2.tests.utils import create_user_and_token
from bothub.api.v2.versionning.views import RepositoryVersionViewSet
from bothub.common import languages
from bothub.common.models import (
    Repository,
    Organization,
    OrganizationAuthorization,
    RepositoryIntent,
    RepositoryVersion,
)
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RepositoryCategory
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryVote
from bothub.common.models import RequestRepositoryAuthorization


def get_valid_mockups(categories):
    return [
        {
            "name": "Repository 1",
            "slug": "repository-1",
            "description": "",
            "language": languages.LANGUAGE_EN,
            "categories": [category.pk for category in categories],
        },
        {
            "name": "Repository 2",
            "description": "",
            "language": languages.LANGUAGE_PT,
            "categories": [category.pk for category in categories],
        },
    ]


def get_invalid_mockups(categories):
    return [
        {
            "name": "",
            "slug": "repository-1",
            "language": languages.LANGUAGE_EN,
            "categories": [category.pk for category in categories],
        },
        {
            "name": "Repository 3",
            "language": "out",
            "categories": [category.pk for category in categories],
            "is_private": False,
        },
    ]


def create_repository_from_mockup(owner, categories, **mockup):
    r = Repository.objects.create(owner_id=owner.id, **mockup)
    r.current_version()
    for category in categories:
        r.categories.add(category)
    return r


class CreateRepositoryAPITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.user_token = create_user_and_token("user")
        self.category = RepositoryCategory.objects.create(name="Category 1")

    def request(self, data, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.post(
            "/v2/repository/repository-details/", data, **authorization_header
        )

        response = RepositoryViewSet.as_view({"post": "create"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        for mockup in get_valid_mockups([self.category]):
            response, content_data = self.request(mockup, self.owner_token)

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            repository = self.owner.repositories.get(uuid=content_data.get("uuid"))

            self.assertEqual(repository.name, mockup.get("name"))
            self.assertEqual(repository.language, mockup.get("language"))
            self.assertEqual(repository.is_private, False)

    def test_invalid_data(self):
        for mockup in get_invalid_mockups([self.category]):
            response, content_data = self.request(mockup, self.owner_token)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RetriveRepositoryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.category = RepositoryCategory.objects.create(name="Category 1")

        self.repositories = [
            create_repository_from_mockup(self.owner, **mockup)
            for mockup in get_valid_mockups([self.category])
        ]

    def request(self, repository, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.get(
            "/v2/repository/info/{}/{}/".format(
                repository.uuid, repository.current_version().repository_version.pk
            ),
            **authorization_header,
        )

        response = NewRepositoryViewSet.as_view({"get": "retrieve"})(
            request,
            repository__uuid=repository.uuid,
            pk=repository.current_version().repository_version.pk,
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        for repository in self.repositories:
            response, content_data = self.request(repository, self.owner_token)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_private_repository(self):
        for repository in self.repositories:
            response, content_data = self.request(repository)
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED
                if repository.is_private
                else status.HTTP_200_OK,
            )


class RetriveRepositoryTrainInfoTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.category = RepositoryCategory.objects.create(name="Category 1")

        self.repositories = [
            create_repository_from_mockup(self.owner, **mockup)
            for mockup in get_valid_mockups([self.category])
        ]

    def request(self, repository, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.get(
            "/v2/repository/train/info/{}/{}/".format(
                repository.uuid, repository.current_version().repository_version.pk
            ),
            **authorization_header,
        )

        response = RepositoryTrainInfoViewSet.as_view({"get": "retrieve"})(
            request,
            repository__uuid=repository.uuid,
            pk=repository.current_version().repository_version.pk,
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        for repository in self.repositories:
            response, content_data = self.request(repository, self.owner_token)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_private_repository(self):
        for repository in self.repositories:
            response, content_data = self.request(repository)
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED
                if repository.is_private
                else status.HTTP_200_OK,
            )


class UpdateRepositoryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.user_token = create_user_and_token("user")
        self.category = RepositoryCategory.objects.create(name="Category 1")

        self.repositories = [
            create_repository_from_mockup(self.owner, **mockup)
            for mockup in get_valid_mockups([self.category])
        ]

    def request(self, repository, data={}, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.patch(
            "/v2/repository/repository-details/{}/".format(repository.uuid),
            self.factory._encode_data(data, MULTIPART_CONTENT),
            MULTIPART_CONTENT,
            **authorization_header,
        )

        response = RepositoryViewSet.as_view({"patch": "update"})(
            request, uuid=repository.uuid, partial=True
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay_update_name(self):
        for repository in self.repositories:
            response, content_data = self.request(
                repository,
                {"name": "Repository {}".format(repository.uuid)},
                self.owner_token,
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized(self):
        for repository in self.repositories:
            response, content_data = self.request(
                repository,
                {"name": "Repository {}".format(repository.uuid)},
                self.user_token,
            )

            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RepositoryAuthorizationTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user, self.user_token = create_user_and_token()
        self.owner, self.owner_token = create_user_and_token("owner")
        self.category = RepositoryCategory.objects.create(name="Category 1")
        self.organization = Organization.objects.create(
            name="Organization 1", nickname="organization1"
        )

        self.repositories = [
            create_repository_from_mockup(self.owner.repository_owner, **mockup)
            for mockup in get_valid_mockups([self.category])
        ]

    def request(self, repository, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.get(
            "/v2/repository/info/{}/{}/".format(
                repository.uuid, repository.current_version().repository_version.pk
            ),
            **authorization_header,
        )

        response = NewRepositoryViewSet.as_view({"get": "retrieve"})(
            request,
            repository__uuid=repository.uuid,
            pk=repository.current_version().repository_version.pk,
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_authorization_without_user(self):
        for repository in self.repositories:
            # ignore private repositories
            if repository.is_private:
                continue
            response, content_data = self.request(repository)
            self.assertIsNone(content_data.get("authorization"))

    def test_authorization_with_user(self):
        for repository in self.repositories:
            user, user_token = (
                (self.owner, self.owner_token)
                if repository.is_private
                else (self.user, self.user_token)
            )
            response, content_data = self.request(repository, user_token)
            authorization = content_data.get("authorization")
            self.assertIsNotNone(authorization)
            self.assertEqual(
                authorization.get("uuid"),
                str(repository.get_user_authorization(user).uuid),
            )

    def test_authorization_permission_admin_in_organization(self):
        for repository in self.repositories:
            perm = OrganizationAuthorization.objects.create(
                user=self.user,
                organization=self.organization,
                role=OrganizationAuthorization.ROLE_ADMIN,
            )

            repo_auth = RepositoryAuthorization.objects.create(
                user=self.organization, repository=repository, role=3
            )
            user, user_token = (
                (self.owner, self.owner_token)
                if repository.is_private
                else (self.user, self.user_token)
            )
            response, content_data = self.request(repository, user_token)
            authorization = content_data.get("authorization")
            self.assertIsNotNone(authorization)
            self.assertEqual(
                authorization.get("level"), OrganizationAuthorization.ROLE_ADMIN
            )
            self.assertTrue(authorization.get("can_read"))
            self.assertTrue(authorization.get("can_contribute"))
            self.assertTrue(authorization.get("can_write"))
            self.assertTrue(authorization.get("can_translate"))
            self.assertTrue(authorization.get("is_admin"))
            self.assertEqual(len(authorization.get("organizations")), 1)
            perm.delete()
            response, content_data = self.request(repository, user_token)
            authorization = content_data.get("authorization")
            self.assertIsNotNone(authorization)
            self.assertEqual(
                authorization.get("level"), OrganizationAuthorization.ROLE_USER
            )

            repo_auth.delete()
            response, content_data = self.request(repository, user_token)
            authorization = content_data.get("authorization")
            self.assertIsNotNone(authorization)
            self.assertEqual(
                authorization.get("level"), OrganizationAuthorization.ROLE_USER
            )


class RepositoryAvailableRequestAuthorizationTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user, self.user_token = create_user_and_token()
        self.owner, self.owner_token = create_user_and_token("owner")

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

    def request(self, repository, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.get(
            "/v2/repository/info/{}/{}/".format(
                repository.uuid, repository.current_version().repository_version.pk
            ),
            **authorization_header,
        )

        response = NewRepositoryViewSet.as_view({"get": "retrieve"})(
            request,
            repository__uuid=repository.uuid,
            pk=repository.current_version().repository_version.pk,
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_owner_ever_false(self):
        response, content_data = self.request(self.repository, self.owner_token)
        available_request_authorization = content_data.get(
            "available_request_authorization"
        )
        self.assertFalse(available_request_authorization)

    def test_user_available(self):
        response, content_data = self.request(self.repository, self.user_token)
        available_request_authorization = content_data.get(
            "available_request_authorization"
        )
        self.assertTrue(available_request_authorization)

    def test_false_when_request(self):
        RequestRepositoryAuthorization.objects.create(
            user=self.user, repository=self.repository, text="r"
        )
        response, content_data = self.request(self.repository, self.user_token)
        available_request_authorization = content_data.get(
            "available_request_authorization"
        )
        self.assertFalse(available_request_authorization)


class IntentsInRepositorySerializerTestCase(TestCase):
    def setUp(self):
        self.owner, self.owner_token = create_user_and_token("owner")

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )
        RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=self.example_intent_1,
        )

    def test_count_1(self):
        repository_data = NewRepositorySerializer(
            self.repository.current_version().repository_version
        ).data
        intent = repository_data.get("intents")[0]
        self.assertEqual(intent.get("examples__count"), 1)

    def test_example_deleted(self):
        example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=self.example_intent_1,
        )
        repository_data = NewRepositorySerializer(
            self.repository.current_version().repository_version
        ).data
        intent = repository_data.get("intents")[0]
        self.assertEqual(intent.get("examples__count"), 2)
        example.delete()
        repository_data = NewRepositorySerializer(
            self.repository.current_version().repository_version
        ).data
        intent = repository_data.get("intents")[0]
        self.assertEqual(intent.get("examples__count"), 1)


class RepositoriesViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.owner, self.owner_token = create_user_and_token("owner")
        self.category_1 = RepositoryCategory.objects.create(name="Category 1")
        self.category_2 = RepositoryCategory.objects.create(name="Category 2")
        self.repositories = [
            create_repository_from_mockup(self.owner, **mockup)
            for mockup in get_valid_mockups([self.category_1])
        ]
        self.public_repositories = list(
            filter(lambda r: not r.is_private, self.repositories)
        )

    def request(self, data={}, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )
        request = self.factory.get("/v2/repositories/", data, **authorization_header)
        response = RepositoriesViewSet.as_view({"get": "list"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_count(self):
        public_repositories_length = len(self.public_repositories)
        response, content_data = self.request()
        self.assertEqual(content_data.get("count"), public_repositories_length)

    def test_name_filter(self):
        response, content_data = self.request(
            {"name": self.public_repositories[0].name}
        )
        self.assertEqual(content_data.get("count"), 1)
        response, content_data = self.request({"name": "abc"})
        self.assertEqual(content_data.get("count"), 0)

    def test_category_filter(self):
        response, content_data = self.request({"categories": [self.category_1.id]})
        self.assertEqual(content_data.get("count"), 2)
        response, content_data = self.request({"categories": [self.category_2.id]})
        self.assertEqual(content_data.get("count"), 0)


class RepositoriesLanguageFilterTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.owner, self.owner_token = create_user_and_token("owner")

        self.repository_en_1 = Repository.objects.create(
            owner=self.owner,
            name="Testing en_1",
            slug="test en_1",
            language=languages.LANGUAGE_EN,
        )
        self.repository_en_2 = Repository.objects.create(
            owner=self.owner,
            name="Testing en_2",
            slug="en_2",
            language=languages.LANGUAGE_EN,
        )
        self.repository_pt = Repository.objects.create(
            owner=self.owner,
            name="Testing pt",
            slug="pt",
            language=languages.LANGUAGE_PT,
        )

    def request(self, data={}, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )
        request = self.factory.get("/v2/repositories/", data, **authorization_header)
        response = RepositoriesViewSet.as_view({"get": "list"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_main_language(self):
        response, content_data = self.request({"language": languages.LANGUAGE_EN})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 2)
        response, content_data = self.request({"language": languages.LANGUAGE_PT})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 1)

    def test_example_language(self):
        language = languages.LANGUAGE_ES
        example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository_en_1.current_version(
                language
            ).repository_version,
        )
        example = RepositoryExample.objects.create(
            repository_version_language=self.repository_en_1.current_version(language),
            text="hi",
            intent=example_intent_1,
        )
        response, content_data = self.request({"language": language})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 1)
        example.delete()
        response, content_data = self.request({"language": language})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 0)

    def test_translated_example(self):
        language = languages.LANGUAGE_ES
        example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository_en_1.current_version(
                language
            ).repository_version,
        )
        example = RepositoryExample.objects.create(
            repository_version_language=self.repository_en_1.current_version(),
            text="hi",
            intent=example_intent_1,
        )
        translated = RepositoryTranslatedExample.objects.create(
            original_example=example, language=language, text="hola"
        )
        response, content_data = self.request({"language": language})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 1)
        translated.delete()
        response, content_data = self.request({"language": language})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 0)


class ListRepositoryVoteTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.repository_votes = RepositoryVote.objects.create(
            user=self.owner, repository=self.repository
        )

    def request(self, param, value, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token)}
        request = self.factory.get(
            "/v2/repository-votes/?{}={}".format(param, value), **authorization_header
        )
        response = RepositoryVotesViewSet.as_view({"get": "list"})(
            request, repository=self.repository.uuid
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_repository_okay(self):
        response, content_data = self.request(
            "repository", self.repository.uuid, self.owner_token.key
        )

        self.assertEqual(content_data["count"], 1)
        self.assertEqual(len(content_data["results"]), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_private_repository_okay(self):
        response, content_data = self.request("repository", self.repository.uuid, "")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_okay(self):
        response, content_data = self.request(
            "user", self.owner.nickname, self.owner_token.key
        )

        self.assertEqual(content_data["count"], 1)
        self.assertEqual(len(content_data["results"]), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_private_user_okay(self):
        response, content_data = self.request("user", self.owner.nickname, "")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class NewRepositoryVoteTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

    def request(self, data, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token)}
        request = self.factory.post(
            "/v2/repository-votes/",
            json.dumps(data),
            content_type="application/json",
            **authorization_header,
        )
        response = RepositoryVotesViewSet.as_view({"post": "create"})(
            request, repository=self.repository.uuid
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {"repository": str(self.repository.uuid)}, self.owner_token.key
        )
        self.assertEqual(content_data["user"], self.owner.id)
        self.assertEqual(content_data["repository"], str(self.repository.uuid))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_private_okay(self):
        response, content_data = self.request(
            {"repository": str(self.repository.uuid)}, ""
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DestroyRepositoryVoteTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.repository_votes = RepositoryVote.objects.create(
            user=self.owner, repository=self.repository
        )

    def request(self, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token)}
        request = self.factory.delete(
            "/v2/repository-votes/{}/".format(str(self.repository.uuid)),
            **authorization_header,
        )
        response = RepositoryVotesViewSet.as_view({"delete": "destroy"})(
            request, repository=self.repository.uuid
        )
        response.render()
        return response

    def test_okay(self):
        response = self.request(self.owner_token.key)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_private_okay(self):
        response = self.request("")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ListRepositoryContributionsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        text = "I can contribute"
        self.repository_request_auth = RequestRepositoryAuthorization.objects.create(
            user=self.user,
            repository=self.repository,
            approved_by=self.owner,
            text=text,
        )

        self.repository_auth = RepositoryAuthorization.objects.create(
            user=self.user, repository=self.repository, role=0
        )

    def request(self):
        request = self.factory.get(
            "/v2/repositories-contributions/?nickname={}".format(self.user.nickname)
        )
        response = RepositoriesContributionsViewSet.as_view({"get": "list"})(
            request, nickname=self.user.nickname
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data["count"], 1)
        self.assertEqual(len(content_data["results"]), 1)


class CategoriesTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.category = RepositoryCategory.objects.create(name="Category 1")
        self.business_category = RepositoryCategory.objects.create(
            name="Business", icon="business"
        )

    def request(self):
        request = self.factory.get("/v2/repository/categories/")
        response = RepositoryCategoriesView.as_view({"get": "list"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_default_category_icon(self):
        response, content_data = self.request()
        self.assertEqual(content_data[0].get("id"), self.category.id)
        self.assertEqual(content_data[0].get("icon"), "botinho")

    def test_custom_category_icon(self):
        response, content_data = self.request()
        self.assertEqual(content_data[1].get("id"), self.business_category.id)
        self.assertEqual(content_data[1].get("icon"), self.business_category.icon)


class SearchRepositoriesTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.user_token = create_user_and_token()

        self.category = RepositoryCategory.objects.create(name="ID")

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )
        self.repository.categories.add(self.category)

    def request(self, nickname):
        request = self.factory.get(
            "/v2/repository/search-repositories/?nickname={}".format(nickname)
        )
        response = SearchRepositoriesViewSet.as_view({"get": "list"})(
            request, nickname=nickname
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request("owner")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content_data.get("count"), 1)
        self.assertEqual(
            uuid.UUID(content_data.get("results")[0].get("uuid")), self.repository.uuid
        )

    def test_empty_with_user_okay(self):
        response, content_data = self.request("fake")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content_data.get("count"), 0)

    def test_empty_without_user_okay(self):
        response, content_data = self.request("")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content_data.get("count"), 0)


class ListAuthorizationTestCase(TestCase):
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

        self.user_auth = self.repository.get_user_authorization(self.user)
        self.user_auth.role = RepositoryAuthorization.ROLE_CONTRIBUTOR
        self.user_auth.save()

    def request(self, repository, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.get(
            "/v2/repository/authorizations/",
            {"repository": repository.uuid},
            **authorization_header,
        )
        response = RepositoryAuthorizationViewSet.as_view({"get": "list"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(self.repository, self.owner_token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(content_data.get("count"), 2)

        self.assertEqual(content_data.get("results")[0].get("user"), self.user.id)

    def test_user_forbidden(self):
        response, content_data = self.request(self.repository, self.user_token)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UpdateAuthorizationRoleTestCase(TestCase):
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

    def request(self, repository, token, user, data):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.patch(
            "/v2/repository/authorizations/{}/{}/".format(
                repository.uuid, user.nickname
            ),
            self.factory._encode_data(data, MULTIPART_CONTENT),
            MULTIPART_CONTENT,
            **authorization_header,
        )
        view = RepositoryAuthorizationViewSet.as_view({"patch": "update"})
        response = view(
            request, repository__uuid=repository.uuid, user__nickname=user.nickname
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            self.repository,
            self.owner_token,
            self.user,
            {"role": RepositoryAuthorization.ROLE_CONTRIBUTOR},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            content_data.get("role"), RepositoryAuthorization.ROLE_CONTRIBUTOR
        )

        user_authorization = self.repository.get_user_authorization(self.user)
        self.assertEqual(
            user_authorization.role, RepositoryAuthorization.ROLE_CONTRIBUTOR
        )

    def test_forbidden(self):
        response, content_data = self.request(
            self.repository,
            self.user_token,
            self.user,
            {"role": RepositoryAuthorization.ROLE_CONTRIBUTOR},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_t_set_your_role(self):
        response, content_data = self.request(
            self.repository,
            self.owner_token,
            self.owner,
            {"role": RepositoryAuthorization.ROLE_CONTRIBUTOR},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RepositoryAuthorizationRequestsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.admin, self.admin_token = create_user_and_token("admin")
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        RequestRepositoryAuthorization.objects.create(
            user=self.user, repository=self.repository, text="I can contribute"
        )

        admin_autho = self.repository.get_user_authorization(self.admin)
        admin_autho.role = RepositoryAuthorization.ROLE_ADMIN
        admin_autho.save()

    def request(self, data, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )
        request = self.factory.get(
            "/v2/repository/authorization-requests/", data, **authorization_header
        )
        response = RepositoryAuthorizationRequestsViewSet.as_view({"get": "list"})(
            request
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {"repository_uuid": self.repository.uuid}, self.owner_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 1)

    def test_admin_okay(self):
        response, content_data = self.request(
            {"repository_uuid": self.repository.uuid}, self.admin_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 1)

    def test_repository_uuid_empty(self):
        response, content_data = self.request({}, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(content_data.get("repository_uuid")), 1)

    def test_forbidden(self):
        response, content_data = self.request(
            {"repository_uuid": self.repository.uuid}, self.user_token
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RequestAuthorizationTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

    def request(self, data, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )
        request = self.factory.post(
            "/v2/repository/authorization-requests/", data, **authorization_header
        )
        response = RepositoryAuthorizationRequestsViewSet.as_view({"post": "create"})(
            request
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {"repository": self.repository.uuid, "text": "I can contribute"}, self.token
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_forbidden_two_requests(self):
        RequestRepositoryAuthorization.objects.create(
            user=self.user, repository=self.repository, text="I can contribute"
        )
        response, content_data = self.request(
            {"repository": self.repository.uuid, "text": "I can contribute"}, self.token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", content_data.keys())


class ReviewAuthorizationRequestTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.admin, self.admin_token = create_user_and_token("admin")
        self.user, self.user_token = create_user_and_token()

        repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.ra = RequestRepositoryAuthorization.objects.create(
            user=self.user, repository=repository, text="I can contribute"
        )

        admin_autho = repository.get_user_authorization(self.admin)
        admin_autho.role = RepositoryAuthorization.ROLE_ADMIN
        admin_autho.save()

    def request_approve(self, ra, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )
        request = self.factory.put(
            "/v2/repository/authorization-requests/{}/".format(ra.pk),
            self.factory._encode_data({}, MULTIPART_CONTENT),
            MULTIPART_CONTENT,
            **authorization_header,
        )
        response = RepositoryAuthorizationRequestsViewSet.as_view({"put": "update"})(
            request, pk=ra.pk
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def request_reject(self, ra, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )
        request = self.factory.delete(
            "/v2/repository/authorization-requests/{}/".format(ra.pk),
            **authorization_header,
        )
        response = RepositoryAuthorizationRequestsViewSet.as_view(
            {"delete": "destroy"}
        )(request, pk=ra.pk)
        response.render()
        return response

    def test_approve_okay(self):
        response, content_data = self.request_approve(self.ra, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("approved_by"), self.owner.id)

    def test_admin_approve_okay(self):
        response, content_data = self.request_approve(self.ra, self.admin_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("approved_by"), self.admin.id)

    def test_approve_twice(self):
        self.ra.approved_by = self.owner
        self.ra.save()
        response, content_data = self.request_approve(self.ra, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_forbidden(self):
        response, content_data = self.request_approve(self.ra, self.user_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reject_okay(self):
        response = self.request_reject(self.ra, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_reject_okay(self):
        response = self.request_reject(self.ra, self.admin_token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_reject_forbidden(self):
        response = self.request_reject(self.ra, self.user_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RepositoryExampleRetrieveTestCase(TestCase):
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

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )
        self.example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="my name is user",
            intent=self.example_intent_1,
        )
        self.example_entity = RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=11, end=18, entity="name"
        )

        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name="Testing Private",
            slug="private",
            language=languages.LANGUAGE_EN,
            is_private=True,
        )
        self.example_intent_2 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.private_repository.current_version().repository_version,
        )
        self.private_example = RepositoryExample.objects.create(
            repository_version_language=self.private_repository.current_version(),
            text="hi",
            intent=self.example_intent_2,
        )

    def request(self, example, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.get(
            "/v2/repository/example/{}/".format(example.id), **authorization_header
        )
        response = RepositoryExampleViewSet.as_view({"get": "retrieve"})(
            request, pk=example.id
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(self.example, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("id"), self.example.id)

    def test_forbidden(self):
        response, content_data = self.request(self.private_example, self.user_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_public(self):
        response, content_data = self.request(self.example, self.user_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("id"), self.example.id)

    def test_list_entities(self):
        response, content_data = self.request(self.example, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content_data.get("entities")), 1)

    def test_entity_has_label(self):
        response, content_data = self.request(self.example, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        entity = content_data.get("entities")[0]
        self.assertIn("group", entity.keys())

    def test_entity_has_valid_label(self):
        group = "subject"
        self.example_entity.entity.set_group("subject")
        self.example_entity.entity.save(update_fields=["group"])
        response, content_data = self.request(self.example, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        entity = content_data.get("entities")[0]
        self.assertIn("group", entity.keys())
        self.assertEqual(entity.get("group"), group)


class RepositoryExampleUploadTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

    def request(self, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        examples = b"""[
                    {
                        "text": "yes",
                        "language": "en",
                        "entities": [{
                            "label": "yes",
                            "entity": "_yes",
                            "start": 0,
                            "end": 3
                        }],
                        "intent": "greet"
                    },
                    {
                        "text": "alright",
                        "language": "en",
                        "entities": [{
                            "label": "yes",
                            "entity": "_yes",
                            "start": 0,
                            "end": 3
                        }],
                        "intent": "greet"
                    }
                ]"""

        uploaded_file = SimpleUploadedFile(
            "examples.json", examples, "multipart/form-data"
        )

        request = self.factory.post(
            "/v2/repository/example/upload_examples/",
            {
                "file": uploaded_file,
                "repository": str(self.repository.uuid),
                "repository_version": self.repository.current_version().repository_version.pk,
            },
            format="multipart",
            **authorization_header,
        )
        response = RepositoryExampleViewSet.as_view({"post": "upload_examples"})(
            request
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(self.owner_token)
        self.assertEqual(content_data.get("added"), 2)
        self.assertEqual(len(content_data.get("not_added")), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_permission_denied(self):
        response, content_data = self.request(self.user_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RepositoryExampleDestroyTestCase(TestCase):
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
        self.example_intent_1 = RepositoryIntent.objects.create(
            text="bias",
            repository_version=self.repository.current_version().repository_version,
        )
        self.example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=self.example_intent_1,
        )

        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name="Testing Private",
            slug="private",
            language=languages.LANGUAGE_EN,
            is_private=True,
        )
        self.example_intent_2 = RepositoryIntent.objects.create(
            text="bias",
            repository_version=self.private_repository.current_version().repository_version,
        )
        self.private_example = RepositoryExample.objects.create(
            repository_version_language=self.private_repository.current_version(),
            text="hi",
            intent=self.example_intent_2,
        )

    def request(self, example, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.delete(
            "/v2/repository/example/{}/".format(example.id), **authorization_header
        )
        response = RepositoryExampleViewSet.as_view({"delete": "destroy"})(
            request, pk=example.id
        )
        return response

    def test_okay(self):
        response = self.request(self.example, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_private_okay(self):
        response = self.request(self.private_example, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_forbidden(self):
        response = self.request(self.example, self.user_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_private_forbidden(self):
        response = self.request(self.private_example, self.user_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_already_deleted(self):
        self.example.delete()

        response = self.request(self.example, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class RepositoryExampleUpdateTestCase(TestCase):
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
        self.example_intent_1 = RepositoryIntent.objects.create(
            text="bias",
            repository_version=self.repository.current_version().repository_version,
        )
        self.example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent=self.example_intent_1,
        )

        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name="Testing Private",
            slug="private",
            language=languages.LANGUAGE_EN,
            is_private=True,
        )
        self.example_intent_2 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.private_repository.current_version().repository_version,
        )
        self.private_example = RepositoryExample.objects.create(
            repository_version_language=self.private_repository.current_version(),
            text="hi",
            intent=self.example_intent_2,
        )

    def request(self, example, token, data):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.patch(
            "/v2/repository/example/{}/".format(example.id),
            json.dumps(data),
            content_type="application/json",
            **authorization_header,
        )
        response = RepositoryExampleViewSet.as_view({"patch": "update"})(
            request, pk=example.id
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        text = "teste"
        intent = "teste1234"

        RepositoryIntent.objects.create(
            text=intent,
            repository_version=self.repository.current_version().repository_version,
        )

        response, content_data = self.request(
            self.example,
            self.owner_token,
            {
                "repository": str(self.repository.uuid),
                "text": text,
                "intent": intent,
                "entities": [],
                "repository_version": self.repository.current_version().repository_version.pk,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("text"), text)
        self.assertEqual(content_data.get("intent"), intent)

    def test_private_forbidden(self):
        response, content_data = self.request(
            self.private_example,
            self.user_token,
            {"text": "teste", "intent": "teste1234"},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class NewRepositoryExampleTestCase(TestCase):
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

    def request(self, token, data):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.post(
            "/v2/repository/example/",
            json.dumps(data),
            content_type="application/json",
            **authorization_header,
        )
        response = RepositoryExampleViewSet.as_view({"post": "create"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        text = "hi"
        intent = "greet"
        RepositoryIntent.objects.create(
            text=intent,
            repository_version=self.repository.current_version().repository_version,
        )
        response, content_data = self.request(
            self.owner_token,
            {
                "repository": str(self.repository.uuid),
                "language": languages.LANGUAGE_EN,
                "text": text,
                "intent": intent,
                "entities": [],
                "repository_version": self.repository.current_version().repository_version.pk,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(content_data.get("text"), text)
        self.assertEqual(content_data.get("intent"), intent)

    def test_okay_with_language(self):
        text = "hi"
        intent = "greet"
        RepositoryIntent.objects.create(
            text=intent,
            repository_version=self.repository.current_version().repository_version,
        )
        language = languages.LANGUAGE_PT
        response, content_data = self.request(
            self.owner_token,
            {
                "repository": str(self.repository.uuid),
                "text": text,
                "language": language,
                "intent": intent,
                "entities": [],
                "repository_version": self.repository.current_version().repository_version.pk,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(content_data.get("text"), text)
        self.assertEqual(content_data.get("intent"), intent)
        self.assertEqual(content_data.get("language"), language)

    def test_forbidden(self):
        example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )
        response, content_data = self.request(
            self.user_token,
            {
                "repository": str(self.repository.uuid),
                "text": "hi",
                "intent": example_intent_1.pk,
                "entities": [],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_repository_uuid_required(self):
        example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )
        response, content_data = self.request(
            self.owner_token,
            {"text": "hi", "intent": example_intent_1.pk, "entities": []},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_repository_does_not_exists(self):
        example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )
        response, content_data = self.request(
            self.owner_token,
            {
                "repository": str(uuid.uuid4()),
                "text": "hi",
                "intent": example_intent_1.pk,
                "entities": [],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("repository", content_data.keys())

    def test_invalid_repository_uuid(self):
        example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )
        response, content_data = self.request(
            self.owner_token,
            {
                "repository": "invalid",
                "text": "hi",
                "intent": example_intent_1.pk,
                "entities": [],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_entities(self):
        example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository.current_version().repository_version,
        )
        response, content_data = self.request(
            self.owner_token,
            {
                "repository": str(self.repository.uuid),
                "language": languages.LANGUAGE_EN,
                "text": "my name is user",
                "intent": example_intent_1.pk,
                "entities": [{"start": 11, "end": 18, "entity": "name"}],
                "repository_version": self.repository.current_version().repository_version.pk,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(content_data.get("entities")), 1)

    def test_exists_example(self):
        text = "hi"
        intent = "greet"
        example_intent_1 = RepositoryIntent.objects.create(
            text=intent,
            repository_version=self.repository.current_version().repository_version,
        )
        response_created, content_data_created = self.request(
            self.owner_token,
            {
                "repository": str(self.repository.uuid),
                "text": text,
                "intent": example_intent_1.pk,
                "language": languages.LANGUAGE_EN,
                "entities": [],
                "repository_version": self.repository.current_version().repository_version.pk,
            },
        )

        self.assertEqual(response_created.status_code, status.HTTP_201_CREATED)

        response, content_data = self.request(
            self.owner_token,
            {
                "repository": str(self.repository.uuid),
                "language": languages.LANGUAGE_EN,
                "text": text,
                "intent": example_intent_1.pk,
                "entities": [],
                "repository_version": self.repository.current_version().repository_version.pk,
            },
        )

        self.assertEqual(
            content_data.get("detail"), "Intention and Sentence already exists"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_intent_or_entity_required(self):
        response, content_data = self.request(
            self.owner_token,
            {
                "repository": str(self.repository.uuid),
                "text": "hi",
                "intent": "",
                "entities": [],
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_entity_with_special_char(self):
        response, content_data = self.request(
            self.owner_token,
            {
                "repository": str(self.repository.uuid),
                "text": "my name is user",
                "intent": "",
                "entities": [{"start": 11, "end": 18, "entity": "nam&"}],
                "repository_version": self.repository.current_version().repository_version.pk,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(content_data.get("entities")), 1)

    def test_intent_with_special_char(self):
        response, content_data = self.request(
            self.owner_token,
            {
                "repository": str(self.repository.uuid),
                "text": "my name is user",
                "intent": "nam$s",
                "entities": [],
                "repository_version": self.repository.current_version().repository_version.pk,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(content_data.get("intent")), 1)


class RetrieveRepositoryTestCase(TestCase):
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

        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name="Testing Private",
            slug="private",
            language=languages.LANGUAGE_EN,
            is_private=True,
        )

    def request(self, repository, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.get(
            "/v2/repository/info/{}/{}/".format(
                str(repository.uuid), repository.current_version().repository_version.pk
            ),
            **authorization_header,
        )
        response = NewRepositoryViewSet.as_view({"get": "retrieve"})(
            request,
            repository__uuid=repository.uuid,
            pk=repository.current_version().repository_version.pk,
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_allowed_in_public(self):
        # owner
        response, content_data = self.request(self.repository, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # secondary user
        response, content_data = self.request(self.repository, self.user_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_allowed_in_private(self):
        # owner
        response, content_data = self.request(self.private_repository, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_forbidden_in_private(self):
        # secondary user
        response, content_data = self.request(self.private_repository, self.user_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_languages_status(self):
        authorization_header = {
            "HTTP_AUTHORIZATION": "Token {}".format(self.user_token.key)
        }
        request = self.factory.get(
            "/v2/repository/repository-details/{}/languagesstatus/".format(
                self.repository.uuid
            ),
            **authorization_header,
        )
        response = RepositoryViewSet.as_view({"get": "languagesstatus"})(
            request, uuid=self.repository.uuid
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_available_request_authorization(self):
        response, content_data = self.request(self.repository, self.user_token)
        self.assertTrue(content_data.get("available_request_authorization"))

    def test_owner_not_available_request_authorization(self):
        response, content_data = self.request(self.repository, self.owner_token)
        self.assertFalse(content_data.get("available_request_authorization"))

    def test_user_not_available_request_authorization(self):
        authorization = self.repository.get_user_authorization(self.user)
        authorization.role = RepositoryAuthorization.ROLE_USER
        authorization.save()
        response, content_data = self.request(self.repository, self.user_token)
        self.assertFalse(content_data.get("available_request_authorization"))

    def test_requested_not_available_request_authorization(self):
        RequestRepositoryAuthorization.objects.create(
            user=self.user, repository=self.repository, text="I can contribute"
        )
        response, content_data = self.request(self.repository, self.user_token)
        self.assertFalse(content_data.get("available_request_authorization"))

    def test_none_request_authorization(self):
        response, content_data = self.request(self.repository, self.user_token)
        self.assertIsNone(content_data.get("request_authorization"))

    def test_request_authorization(self):
        text = "I can contribute"
        request = RequestRepositoryAuthorization.objects.create(
            user=self.user, repository=self.repository, text=text
        )
        response, content_data = self.request(self.repository, self.user_token)
        request_authorization = content_data.get("request_authorization")
        self.assertEqual(request_authorization.get("id"), request.id)
        self.assertEqual(request_authorization.get("text"), text)


class TrainRepositoryTestCase(TestCase):
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

    def request(self, repository, token, data):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.post(
            "/v2/repository/repository-details/{}/train/".format(str(repository.uuid)),
            data,
            **authorization_header,
        )
        response = RepositoryViewSet.as_view({"post": "train"})(
            request, uuid=repository.uuid
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_permission_denied(self):
        response, content_data = self.request(self.repository, self.user_token, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AnalyzeRepositoryTestCase(TestCase):
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
        self.private_repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="private",
            language=languages.LANGUAGE_EN,
            is_private=True,
        )

    def request(self, repository, token, data):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.post(
            "/v2/repository/repository-details/{}/analyze/".format(
                str(repository.uuid)
            ),
            data,
            **authorization_header,
        )
        response = RepositoryViewSet.as_view({"post": "analyze"})(
            request, uuid=repository.uuid
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_permission_denied_in_private_repository(self):
        response, content_data = self.request(
            self.private_repository,
            self.user_token,
            {"language": "en", "text": "My name is Douglas"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_language_required(self):
        response, content_data = self.request(
            self.repository,
            self.owner_token,
            {"language": "", "text": "My name is Douglas"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("language", content_data.keys())

    def test_text_required(self):
        response, content_data = self.request(
            self.repository, self.owner_token, {"language": "en", "text": ""}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("text", content_data.keys())


class VersionsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )
        current_version = self.repository.current_version()
        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet", repository_version=current_version.repository_version
        )
        RepositoryExample.objects.create(
            repository_version_language=current_version,
            text="my name is Douglas",
            intent=self.example_intent_1,
        )
        RepositoryExample.objects.create(
            repository_version_language=current_version,
            text="my name is John",
            intent=self.example_intent_1,
        )
        current_version.start_training(self.owner)

    def request(self, data, token=None):
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
            {"repository": str(self.repository.uuid)}, self.owner_token
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 1)

    def test_not_authenticated(self):
        response, content_data = self.request({"repository": str(self.repository.uuid)})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_without_repository(self):
        response, content_data = self.request({}, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RepositoryEntitiesTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.user_token = create_user_and_token()

        self.entity_value = "user"

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )
        self.repository_version = self.repository.current_version().repository_version
        self.example_intent_1 = RepositoryIntent.objects.create(
            text="bias", repository_version=self.repository_version
        )
        self.example = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="my name is user",
            intent=self.example_intent_1,
        )
        self.example_entity = RepositoryExampleEntity.objects.create(
            repository_example=self.example, start=11, end=18, entity=self.entity_value
        )
        self.example_entity.entity.set_group("name")
        self.example_entity.entity.save()

    def request(self, data, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.get(
            "/v2/repository/entities/", data=data, **authorization_header
        )
        response = RepositoryEntitiesViewSet.as_view({"get": "list"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {
                "repository_uuid": self.repository.uuid,
                "repository_version": self.repository_version.pk,
            },
            self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 1)

        response, content_data = self.request(
            {
                "repository_uuid": self.repository.uuid,
                "repository_version": self.repository_version.pk,
                "value": self.entity_value,
            },
            self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 1)

        response, content_data = self.request(
            {
                "repository_uuid": self.repository.uuid,
                "repository_version": self.repository_version.pk,
                "value": "other",
            },
            self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("count"), 0)


class UpdateRepositoryIntentTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.user_token = create_user_and_token("user")

        self.repository = Repository.objects.create(
            owner=self.owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )
        self.repository_version = self.repository.current_version().repository_version

    def request(self, id, data={}, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.patch(
            "/v2/repository/intent/{}/".format(id),
            self.factory._encode_data(data, MULTIPART_CONTENT),
            MULTIPART_CONTENT,
            **authorization_header,
        )

        response = RepositoryIntentViewSet.as_view({"patch": "update"})(
            request, pk=id, partial=True
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay_update_text(self):
        intent = RepositoryIntent.objects.create(
            repository_version=self.repository_version, text="positive"
        )
        response, content_data = self.request(
            intent.pk, {"text": "negative"}, self.owner_token
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data.get("text"), "negative")
        self.assertEqual(
            content_data.get("repository_version"), self.repository_version.pk
        )

    def test_unauthorized(self):
        intent = RepositoryIntent.objects.create(
            repository_version=self.repository_version, text="positive"
        )
        response, content_data = self.request(
            intent.pk, {"text": "negative"}, self.user_token
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RepositoryExamplesBulkTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.user_token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
        )

        self.data = [
            {
                "repository": str(self.repository.uuid),
                "text": "alright",
                "intent": "affirmative",
                "language": "en",
                "entities": [{"label": "yes", "entity": "_yes", "start": 0, "end": 3}],
                "repository_version": self.repository.current_version().repository_version.pk,
            },
            {
                "repository": str(self.repository.uuid),
                "text": "yes",
                "intent": "affirmative",
                "language": "en",
                "entities": [{"label": "yes", "entity": "_yes", "start": 0, "end": 3}],
                "repository_version": self.repository.current_version().repository_version.pk,
            },
        ]

    def request(self, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.post(
            "/v2/repository/example-bulk/",
            data=json.dumps(self.data),
            content_type="application/json",
            **authorization_header,
        )
        response = RepositoryExamplesBulkViewSet.as_view({"post": "create"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(self.owner_token)
        for count, content in enumerate(content_data):
            self.assertEqual(
                content.get("repository_version"),
                self.data[count].get("repository_version"),
            )
            self.assertEqual(content.get("text"), self.data[count].get("text"))
            self.assertEqual(content.get("intent"), self.data[count].get("intent"))
            self.assertEqual(content.get("language"), self.data[count].get("language"))
            self.assertNotEqual(
                content.get("entities"), self.data[count].get("entities")
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_null_data(self):
        self.data = {}
        response, content_data = self.request(self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_first_invalid_data(self):
        self.data = [
            {
                "repository": str(self.repository.uuid),
                "text": None,
                "intent": None,
                "language": None,
                "entities": [{"label": "yes", "entity": "_yes", "start": 0, "end": 0}],
                "repository_version": self.repository.current_version().repository_version.pk,
            },
            {
                "repository": str(self.repository.uuid),
                "text": "yes",
                "intent": "affirmative",
                "language": "en",
                "entities": [{"label": "yes", "entity": "_yes", "start": 0, "end": 3}],
                "repository_version": self.repository.current_version().repository_version.pk,
            },
        ]
        response, content_data = self.request(self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_second_invalid_data(self):
        self.data = [
            {
                "repository": str(self.repository.uuid),
                "text": "yes",
                "intent": "affirmative",
                "language": "en",
                "entities": [{"label": "yes", "entity": "_yes", "start": 0, "end": 3}],
                "repository_version": self.repository.current_version().repository_version.pk,
            },
            {
                "repository": str(self.repository.uuid),
                "text": None,
                "intent": None,
                "language": None,
                "entities": [{"label": "yes", "entity": "_yes", "start": 0, "end": 0}],
                "repository_version": self.repository.current_version().repository_version.pk,
            },
        ]
        response, content_data = self.request(self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_string_data(self):
        self.data = """[{
                "repository": str(self.repository.uuid),
                "text": "yes",
                "intent": "affirmative",
                "language": "en",
                "entities": [{"label": "yes", "entity": "_yes", "start": 0, "end": 3}],
                "repository_version": self.repository.current_version().repository_version.pk,
            },
            {
                "repository": str(self.repository.uuid),
                "text": None,
                "intent": None,
                "language": None,
                "entities": [{"label": "yes", "entity": "_yes", "start": 0, "end": 0}],
                "repository_version": self.repository.current_version().repository_version.pk,
            }]"""

        response, content_data = self.request(self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_one_into_array_data(self):
        self.data = [
            {
                "repository": str(self.repository.uuid),
                "text": "alright",
                "intent": "affirmative",
                "language": "en",
                "entities": [{"label": "yes", "entity": "_yes", "start": 0, "end": 3}],
                "repository_version": self.repository.current_version().repository_version.pk,
            }
        ]
        response, content_data = self.request(self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_one_without_array_data(self):
        self.data = {
            "repository": str(self.repository.uuid),
            "text": "alright",
            "intent": "affirmative",
            "language": "en",
            "entities": [{"label": "yes", "entity": "_yes", "start": 0, "end": 3}],
            "repository_version": self.repository.current_version().repository_version.pk,
        }
        response, content_data = self.request(self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_permission_denied(self):
        response = self.request(self.user_token)
        self.assertEqual(response[0].status_code, status.HTTP_403_FORBIDDEN)


class EvaluateAutomaticTestCase(TestCase):
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

        self.repository_version = RepositoryVersion.objects.create(
            repository=self.repository, name="test"
        )

    def request(self, repository, data={}, token=None):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}

        request = self.factory.post(
            "/v2/repository/repository-details/{}/automatic_evaluate/".format(
                str(repository.uuid)
            ),
            data,
            **authorization_header,
        )

        response = RepositoryViewSet.as_view({"post": "automatic_evaluate"})(
            request, uuid=repository.uuid
        )

        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_permission_denied(self):
        response, content_data = self.request(self.repository, {}, self.user_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_data(self):
        data = {"repository_version": self.repository_version.pk}
        response, content_data = self.request(self.repository, data, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CheckCanEvaluateAutomaticTestCase(TestCase):
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

        self.repository_version = RepositoryVersion.objects.create(
            repository=self.repository, name="test"
        )

    def request(self, repository, data={}, token=None):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}

        request = self.factory.get(
            "/v2/repository/repository-details/{}/check_can_automatic_evaluate/".format(
                str(repository.uuid)
            ),
            data,
            **authorization_header,
        )

        response = RepositoryViewSet.as_view({"get": "check_can_automatic_evaluate"})(
            request, uuid=repository.uuid
        )

        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_permission_denied(self):
        response, content_data = self.request(self.repository, {}, self.user_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_data(self):
        data = {}
        response, content_data = self.request(self.repository, data, self.owner_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cant_evaluate_automatic(self):
        data = {"language": self.repository.language}
        response, content_data = self.request(self.repository, data, self.owner_token)
        self.assertFalse(content_data.get("can_run_evaluate_automatic"))
        self.assertEqual(len(content_data.get("messages")), 1)

    def test_can_evaluate_automatic(self):
        for i in range(0, 2):
            intent_ = RepositoryIntent.objects.create(
                text=f"test-{i}",
                repository_version=self.repository.current_version().repository_version,
            )
            for j in range(0, 20):
                RepositoryExample.objects.create(
                    repository_version_language=self.repository.current_version(),
                    text=f"hi-{j}",
                    intent=intent_,
                )
        data = {"language": self.repository.language}
        response, content_data = self.request(self.repository, data, self.owner_token)
        self.assertTrue(content_data.get("can_run_evaluate_automatic"))
        self.assertEqual(len(content_data.get("messages")), 0)
