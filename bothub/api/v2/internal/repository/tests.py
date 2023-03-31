import json

from django.test import tag
from django.test import RequestFactory
from django.test import TestCase
from rest_framework import status

from bothub.api.v2.internal.repository.views import InternalRepositoriesViewSet
from bothub.api.v2.tests.utils import create_user_and_token
from bothub.common.models import Organization, OrganizationAuthorization
from bothub.common.models import RepositoryCategory

from bothub.api.v2.tests.utils import get_valid_mockups, create_repository_from_mockup


class InternalRepositoryTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.moduser, self.moduser_token = create_user_and_token("module", module=True)
        self.owner, self.owner_token = create_user_and_token("owner")
        self.category = RepositoryCategory.objects.create(name="Category 1")
        self.org = Organization.objects.create(
            name="Organization 1", nickname="organization1"
        )
        OrganizationAuthorization.objects.create(
            user=self.owner,
            organization=self.org,
            role=OrganizationAuthorization.ROLE_ADMIN,
        )
        self.repositories = [
            create_repository_from_mockup(self.org, **mockup)
            for mockup in get_valid_mockups([self.category])
        ]
        for rep in self.repositories:
            rep.get_user_authorization(self.org)

        self.repository_auth = self.repositories[0].get_user_authorization(self.owner)


@tag("internal")
class InternalRepositoryListTestCase(InternalRepositoryTestCase):
    def request(self, params, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.get(
            "/v2/internal/repository/", params, **authorization_header
        )
        response = InternalRepositoriesViewSet.as_view({"get": "list"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(
            {"name": "Repository 1", "org_id": self.org.id}, self.moduser_token
        )
        self.assertEqual(content_data["count"], 1)
        self.assertEqual(len(content_data["results"]), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_return_all_repos(self):
        response, content_data = self.request(
            {"org_id": self.org.id}, self.moduser_token
        )

        self.assertEqual(content_data["count"], 2)
        self.assertEqual(len(content_data["results"]), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fail_module(self):
        response, content_data = self.request({"org_id": self.org.pk}, self.owner_token)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@tag("internal")
class InternalRepositoryRetrieveAuthorizationTestCase(InternalRepositoryTestCase):
    def request(self, params, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )
        request = self.factory.get(
            "/v2/internal/repository/RetrieveAuthorization/",
            params,
            **authorization_header,
        )
        response = InternalRepositoriesViewSet.as_view(
            {"get": "retrieve_authorization"}
        )(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok_repository_1(self):
        response, content_data = self.request(
            {"repository_authorization": self.repository_auth.pk}, self.moduser_token
        )
        self.assertEqual(content_data["name"], "Repository 1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_ok(self):
        response, content_data = self.request(
            {"repository_authorization": self.repository_auth.pk}, self.owner_token
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
