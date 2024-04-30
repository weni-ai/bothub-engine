from django.test import TestCase, RequestFactory

from bothub.common.models import Organization, RepositoryCategory, OrganizationAuthorization
from bothub.api.v2.tests.utils import create_user_and_token


from bothub.authorizations.usecases.dto import OrgAuthDTO
from bothub.authorizations.usecases import AuthorizationsUsecase


class UseCaseTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.moduser, self.moduser_token = create_user_and_token("module", module=True)
        self.user, self.user_token = create_user_and_token("user")
        self.category = RepositoryCategory.objects.create(name="Category 1")
        self.org = Organization.objects.create(
            name="Organization 1", nickname="organization1"
        )
        self.usecase = AuthorizationsUsecase()

    def test_create(self):
        role = 3
        org_id = self.org.id
        user_email = self.user.email
        org_auth_dto = OrgAuthDTO(
            user=user_email,
            role=role,
            org_id=org_id
        )

        created: bool
        org_auth: OrganizationAuthorization

        created, org_auth = self.usecase.dispatch("create")(org_auth_dto)

        self.assertIsInstance(org_auth, OrganizationAuthorization)
        self.assertTrue(created)
        self.assertEquals(org_auth.user.email, user_email)

    def test_update(self):
        OrganizationAuthorization.objects.create(
            organization=self.org,
            user=self.user,
            role=3
        )

        role = 2
        org_id = self.org.id
        user_email = self.user.email
        org_auth_dto = OrgAuthDTO(
            user=user_email,
            role=role,
            org_id=org_id
        )
        org_auth: OrganizationAuthorization

        org_auth = self.usecase.dispatch("update")(org_auth_dto)

        self.assertIsInstance(org_auth, OrganizationAuthorization)
        self.assertEquals(org_auth.role, role)

    def test_delete(self):
        self.org.organization_authorizations.create(user=self.user, role=3)
        role = 2
        org_id = self.org.id
        user_email = self.user.email
        org_auth_dto = OrgAuthDTO(
            user=user_email,
            role=role,
            org_id=org_id
        )

        self.usecase.dispatch("delete")(org_auth_dto)

        with self.assertRaises(OrganizationAuthorization.DoesNotExist):
            OrganizationAuthorization.objects.get(user=self.user, organization=self.org)

