import json
from bothub.authentication.models import User

from django.test import tag
from django.test import RequestFactory
from django.test import TestCase
from rest_framework import status

from bothub.api.v2.internal.user.views import (
    UserPermissionViewSet,
    UserViewSet,
    UserLanguageViewSet,
)
from bothub.api.v2.tests.utils import create_user_and_token
from bothub.common.models import (
    Organization,
    OrganizationAuthorization,
    RepositoryCategory,
)


class InternalUserTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.moduser, self.moduser_token = create_user_and_token("module", module=True)
        self.owner, self.owner_token = create_user_and_token("owner")
        self.user, self.user_token = create_user_and_token("user")
        self.category = RepositoryCategory.objects.create(name="Category 1")
        self.org = Organization.objects.create(
            name="Organization 1", nickname="organization1"
        )
        OrganizationAuthorization.objects.create(
            user=self.owner,
            organization=self.org,
            role=OrganizationAuthorization.ROLE_ADMIN,
        )
        OrganizationAuthorization.objects.create(
            user=self.user,
            organization=self.org,
            role=OrganizationAuthorization.ROLE_CONTRIBUTOR,
        )


@tag("internal")
class InternalUserPermissionRetrieveTestCase(InternalUserTestCase):
    def request(self, params, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.get(
            "/v2/internal/user/permission", params, **authorization_header
        )
        response = UserPermissionViewSet.as_view({"get": "retrieve"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(
            {"user_email": self.owner.email, "org_id": self.org.pk},
            token=self.moduser_token,
        )
        self.assertEqual(content_data["role"], OrganizationAuthorization.ROLE_ADMIN)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_ok(self):
        response, content_data = self.request(
            {"user_email": self.owner.email, "org_id": self.org.pk},
            token=self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@tag("internal")
class InternalUserPermissionUpdateTestCase(InternalUserTestCase):
    def request(self, params, user_email, org_id, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )
        authorization_header["content_type"] = "application/json"

        request = self.factory.put(
            f"/v2/internal/user/permission?user_email={user_email}&org_id={org_id}",
            params,
            **authorization_header,
        )
        response = UserPermissionViewSet.as_view({"put": "update"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(
            {"role": OrganizationAuthorization.ROLE_CONTRIBUTOR},
            user_email=self.owner.email,
            org_id=self.org.pk,
            token=self.moduser_token,
        )
        auth = OrganizationAuthorization.objects.get(
            user=self.owner, organization=self.org
        )
        self.assertEqual(
            content_data["role"], OrganizationAuthorization.ROLE_CONTRIBUTOR
        )
        self.assertEqual(content_data["role"], auth.role)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_ok(self):
        response, content_data = self.request(
            {"role": OrganizationAuthorization.ROLE_CONTRIBUTOR},
            user_email=self.owner.email,
            org_id=self.org.pk,
            token=self.owner_token,
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@tag("internal")
class InternalUserPermissionDeleteTestCase(InternalUserTestCase):
    def request(self, user_email, org_id, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )
        authorization_header["content_type"] = "application/json"

        request = self.factory.delete(
            f"/v2/internal/user/permission?user_email={user_email}&org_id={org_id}",
            {},
            **authorization_header,
        )
        response = UserPermissionViewSet.as_view({"delete": "destroy"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(
            user_email=self.owner.email, org_id=self.org.pk, token=self.moduser_token
        )
        self.assertEqual(content_data["role"], None)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_ok(self):
        response, content_data = self.request(
            user_email=self.owner.email, org_id=self.org.pk, token=self.owner_token
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@tag("internal")
class InternalUserRetrieveTestCase(InternalUserTestCase):
    def request(self, params, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.get("/v2/internal/user", params, **authorization_header)
        response = UserViewSet.as_view({"get": "retrieve"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(
            {"user_email": self.owner.email}, token=self.moduser_token
        )
        self.assertEqual(content_data["email"], self.owner.email)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_ok(self):
        response, content_data = self.request(
            {"user_email": self.owner.email}, token=self.owner_token
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@tag("internal")
class InternalUserLanguageUpdateTestCase(InternalUserTestCase):
    def request(self, params, user_email, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )
        authorization_header["content_type"] = "application/json"

        request = self.factory.put(
            f"/v2/internal/user/language?user_email={user_email}",
            params,
            **authorization_header,
        )
        response = UserLanguageViewSet.as_view({"put": "update"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_ok(self):
        response, content_data = self.request(
            {"language": "es"}, user_email=self.owner.email, token=self.moduser_token
        )
        user = User.objects.get(email=self.owner.email)
        self.assertEqual(content_data["language"], user.language)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_ok(self):
        response, content_data = self.request(
            {"language": "es"}, user_email=self.owner.email, token=self.owner_token
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
