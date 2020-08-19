import json

from django.test import RequestFactory
from django.test import TestCase
from rest_framework import status

from bothub.common import languages
from bothub.common.models import (
    Repository,
    RepositoryExampleEntity,
    RepositoryEntityGroup, RepositoryIntent,
)
from bothub.common.models import (
    RepositoryExample,
    RepositoryVersion,
    RepositoryVersionLanguage,
)
from .utils import create_user_and_token
from ..groups.views import RepositoryEntityGroupViewSet


class NewGroupTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.token = create_user_and_token()

        self.repository = Repository.objects.create(
            owner=self.owner.repository_owner,
            name="Testing",
            slug="test",
            language=languages.LANGUAGE_EN,
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

        self.example_1 = RepositoryExample.objects.create(
            repository_version_language=self.repository_version_language,
            text="hi",
            intent=self.example_intent_1,
        )

    def request(self, data, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.post(
            "/v2/repository/entity/group/",
            json.dumps(data),
            content_type="application/json",
            **authorization_header,
        )
        response = RepositoryEntityGroupViewSet.as_view({"post": "create"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {
                "repository": str(self.repository.uuid),
                "repository_version": self.repository_version.pk,
                "value": "group_name",
            },
            self.owner_token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_okay_with_sentence(self):
        response, content_data = self.request(
            {
                "repository": str(self.repository.uuid),
                "repository_version": self.repository_version.pk,
                "value": "group_name",
            },
            self.owner_token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        entity_1 = RepositoryExampleEntity.objects.create(
            repository_example=self.example_1, start=0, end=0, entity="hi"
        )
        entity_1.entity.set_group("group_name")
        entity_1.entity.save()
        self.assertEqual(entity_1.entity.group.value, "group_name")
        self.assertEqual(entity_1.entity.group.pk, content_data.get("id"))
        self.assertEqual(
            entity_1.entity.group.repository_version.pk,
            content_data.get("repository_version"),
        )


class GroupDestroyTestCase(TestCase):
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

        self.repository_version = RepositoryVersion.objects.create(
            repository=self.repository, name="test"
        )

        self.repository_version_language = RepositoryVersionLanguage.objects.create(
            repository_version=self.repository_version,
            language="en",
            algorithm="neural_network_internal",
        )

        self.group = RepositoryEntityGroup.objects.create(
            repository_version=self.repository_version, value="group_name"
        )

        self.example_intent_1 = RepositoryIntent.objects.create(
            text="greet",
            repository_version=self.repository_version
        )

        self.example_1 = RepositoryExample.objects.create(
            repository_version_language=self.repository_version_language,
            text="test",
            intent=self.example_intent_1,
        )

        self.entity_1 = RepositoryExampleEntity.objects.create(
            repository_example=self.example_1, start=0, end=0, entity="hi"
        )
        self.entity_1.entity.set_group("group_name")
        self.entity_1.entity.save()

    def request(self, token):
        authorization_header = {"HTTP_AUTHORIZATION": "Token {}".format(token.key)}
        request = self.factory.delete(
            f"/v2/repository/entity/group/{self.group.pk}/", **authorization_header
        )
        response = RepositoryEntityGroupViewSet.as_view({"delete": "destroy"})(
            request, pk=self.group.pk
        )
        return response

    def test_okay(self):
        response = self.request(self.owner_token)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        entity = RepositoryExampleEntity.objects.filter(pk=self.entity_1.pk)

        self.assertEqual(entity.first().pk, self.entity_1.pk)
        self.assertEqual(entity.first().entity.group, None)
        self.assertEqual(entity.count(), 1)
