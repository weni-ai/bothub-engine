import json

from django.test import RequestFactory
from django.test import TestCase
from rest_framework import status

from bothub.api.v2.organization.views import OrganizationViewSet
from bothub.api.v2.tests.utils import create_user_and_token
from bothub.common.models import Organization, OrganizationAuthorization


class NewOrganizationAPITestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.owner, self.owner_token = create_user_and_token("owner")

    def request(self, data, token=None):
        authorization_header = (
            {"HTTP_AUTHORIZATION": "Token {}".format(token.key)} if token else {}
        )

        request = self.factory.post(
            "/v2/org/organization/", data, **authorization_header
        )

        response = OrganizationViewSet.as_view({"post": "create"})(request)
        response.render()
        content_data = json.loads(response.content)
        return (response, content_data)

    def test_okay(self):
        response, content_data = self.request(
            {
                "name": "Organization 1",
                "nickname": "organization1",
                "locale": "Brazil",
                "description": "This organization is very good",
            },
            self.owner_token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        organization = Organization.objects.get(pk=content_data.get("id"))

        self.assertEqual(organization.name, "Organization 1")
        self.assertEqual(organization.nickname, "organization1")
        self.assertEqual(organization.locale, "Brazil")
        self.assertEqual(organization.description, "This organization is very good")

        organization_authorization = OrganizationAuthorization.objects.filter(
            organization=organization, user=self.owner
        )

        self.assertEqual(organization_authorization.count(), 1)
        self.assertEqual(
            organization_authorization.first().role,
            OrganizationAuthorization.ROLE_ADMIN,
        )
