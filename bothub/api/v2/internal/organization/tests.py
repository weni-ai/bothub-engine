import json

from django.test import tag
from django.test import RequestFactory
from django.test import TestCase
from rest_framework import status

from bothub.api.v2.internal.organization.views import InternalOrganizationViewSet
from bothub.api.v2.tests.utils import create_user_and_token
from bothub.common.models import (
    Organization,
    OrganizationAuthorization,
    RepositoryCategory,
)
from bothub.api.v2.tests.utils import get_valid_mockups, create_repository_from_mockup


class InternalOrganizationTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.moduser, self.moduser_token = create_user_and_token("module", module=True)
        self.owner, self.owner_token = create_user_and_token("owner")
        self.category = RepositoryCategory.objects.create(name="Category 1")
        self.org = Organization.objects.create(
            name="Organization 1", nickname="organization1"
        )
        self.org_2 = Organization.objects.create(
            name="Organization 2", nickname="organization2"
        )
        OrganizationAuthorization.objects.create(
            user=self.owner,
            organization=self.org,
            role=OrganizationAuthorization.ROLE_ADMIN,
        )
        OrganizationAuthorization.objects.create(
            user=self.owner,
            organization=self.org_2,
            role=OrganizationAuthorization.ROLE_ADMIN,
        )
        self.repositories = [
            create_repository_from_mockup(self.org, **mockup)
            for mockup in get_valid_mockups([self.category])
        ]
        for rep in self.repositories:
            rep.get_user_authorization(self.org)

        self.repository_auth = self.repositories[0].get_user_authorization(self.owner)


def auth_header(token):
    authorization_header = (
        {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
    )
    authorization_header["content_type"] = "application/json"

    return authorization_header


@tag("internal")
class InternalOrganizationListTestCase(InternalOrganizationTestCase):
    def request(self, params, token=None):
        authorization_header = auth_header(token)

        request = self.factory.get(
            "/v2/internal/organization/", params, **authorization_header
        )
        response = InternalOrganizationViewSet.as_view({"get": "list"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(
            {"user_email": self.owner.email},
            self.moduser_token,
        )
        self.assertEqual(len(content_data), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_ok(self):
        response, content_data = self.request(
            {"user_email": self.owner.email},
            self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@tag("internal")
class InternalOrganizationCreateTestCase(InternalOrganizationTestCase):
    def request(self, data, token=None):
        authorization_header = auth_header(token)

        request = self.factory.post(
            "/v2/internal/organization/", data, **authorization_header
        )

        response = InternalOrganizationViewSet.as_view({"post": "create"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(
            {"user_email": self.owner.email, "organization_name": "org3"},
            self.moduser_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        organization = Organization.objects.get(pk=content_data.get("id"))
        self.assertEqual(organization.name, "org3")
        organization_authorization = OrganizationAuthorization.objects.filter(
            organization=organization, user=self.owner
        )
        self.assertEqual(organization_authorization.count(), 1)
        self.assertEqual(
            organization_authorization.first().role,
            OrganizationAuthorization.ROLE_ADMIN,
        )

    def test_not_ok(self):
        response, content_data = self.request(
            {"user_email": self.owner.email, "organization_name": "org3"},
            self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@tag("internal")
class InternalOrganizationDestroyTestCase(InternalOrganizationTestCase):
    def request(self, email, id, token=None):
        authorization_header = auth_header(token)

        request = self.factory.delete(
            f"/v2/internal/organization/?user_email={email}", **authorization_header
        )

        response = InternalOrganizationViewSet.as_view({"delete": "destroy"})(
            request, pk=id
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(
            self.owner.email,
            self.org_2.id,
            self.moduser_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        organization = Organization.objects.filter(pk=self.org_2.pk)
        self.assertEqual(organization.count(), 0)

    def test_not_ok(self):
        response, content_data = self.request(
            self.owner.email,
            self.org_2.id,
            self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@tag("internal")
class InternalOrganizationUpdateTestCase(InternalOrganizationTestCase):
    def request(self, data, email, id, token=None):
        authorization_header = auth_header(token)

        request = self.factory.put(
            f"/v2/internal/organization/?user_email={email}",
            data,
            **authorization_header,
        )
        response = InternalOrganizationViewSet.as_view({"put": "update"})(
            request, pk=id
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(
            {"name": "org222"},
            self.owner.email,
            self.org_2.id,
            self.moduser_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        organization = Organization.objects.get(pk=self.org_2.pk)

        self.assertEqual(organization.name, "org222")

    def test_not_ok(self):
        response, content_data = self.request(
            {"name": "org222"},
            self.owner.email,
            self.org_2.id,
            self.owner_token,
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@tag("internal")
class InternalOrganizationRetrieveTestCase(InternalOrganizationTestCase):
    def request(self, email, id, token=None):
        authorization_header = auth_header(token)

        request = self.factory.get(
            f"/v2/internal/organization/?user_email={email}", **authorization_header
        )
        response = InternalOrganizationViewSet.as_view({"get": "retrieve"})(
            request, pk=id
        )
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(
            self.owner.email,
            self.org.id,
            self.moduser_token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(content_data["repositories_count"], 2)

    def test_not_ok(self):
        response, content_data = self.request(
            self.owner.email,
            self.org.id,
            self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
