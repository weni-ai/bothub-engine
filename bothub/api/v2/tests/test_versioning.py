import json

from django.test import RequestFactory
from django.test import TestCase
from rest_framework import status

from bothub.api.v2.tests.utils import create_user_and_token
from bothub.api.v2.versionning.views import VersioningViewSet
from bothub.common import languages
from bothub.common.models import (
    Repository,
    RepositoryExample,
    RepositoryExampleEntity,
    RepositoryVersionLanguage,
    RepositoryVersion,
)


class CloneRepositoryAPITestCase(TestCase):
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

        self.example_1 = RepositoryExample.objects.create(
            repository_version_language=self.repository.current_version(),
            text="hi",
            intent="greet",
        )
        self.entity_1 = RepositoryExampleEntity.objects.create(
            repository_example=self.example_1, start=0, end=0, entity="hi"
        )
        self.entity_1.entity.set_label("greet")
        self.entity_1.entity.save()

    def request(self, data, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.post(
            "/v2/repository/version/", data, **authorization_header
        )

        response = VersioningViewSet.as_view({"post": "create"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {
                "repository": str(self.repository.pk),
                "id": int(self.repository.current_version().pk),
            },
            self.owner_token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        version = RepositoryVersion.objects.filter(
            pk=content_data.get("id"), repository=self.repository
        )

        self.assertEqual(version.count(), 1)

        version_language = RepositoryVersionLanguage.objects.filter(
            repository_version=version.first(), language=languages.LANGUAGE_EN
        )

        self.assertEqual(version_language.count(), 1)

        example = RepositoryExample.objects.filter(
            repository_version_language=version_language.first()
        ).first()

        self.assertEqual(example.text, self.example_1.text)
        self.assertEqual(example.intent, self.example_1.intent)
