from django_grpc_framework.test import RPCTransactionTestCase

from bothub.api.v2.tests.utils import create_user_and_token
from bothub.authentication.models import User
from bothub.common.models import Organization, OrganizationAuthorization
from bothub.protos.inteligence import authentication_pb2_grpc, authentication_pb2


class UserServiceTest(RPCTransactionTestCase):

    WRONG_ID = -1
    WRONG_EMAIL = "wrong@email.com"

    def setUp(self):
        self.user, self.user_token = create_user_and_token("user")

        self.organization = Organization.objects.create(name="Weni")

        self.organization.organization_authorizations.create(
            user=self.user, role=OrganizationAuthorization.ROLE_ADMIN
        )

        super().setUp()

        self.user_permission_stub = authentication_pb2_grpc.UserPermissionControllerStub(
            self.channel
        )
        self.user_stub = authentication_pb2_grpc.UserControllerStub(self.channel)

    def test_user_retrieve(self):
        response = self.user_retrieve_request(email=self.user.email)

        self.assertEquals(response.id, self.user.id)
        self.assertEquals(response.nickname, self.user.nickname)
        self.assertEquals(response.email, self.user.email)
        self.assertEquals(response.name, self.user.name)

    def test_user_permission_update(self):
        org = Organization.objects.first()
        user = User.objects.first()

        update_response = self.user_permission_update_request(
            org_id=org.id,
            user_email=user.email,
            permission=OrganizationAuthorization.ROLE_ADMIN,
        )
        retrieve_response = self.user_permission_retrieve_request(
            org_id=org.id, org_user_email=user.email
        )

        self.assertEquals(update_response, retrieve_response)

    def test_user_permission_remove(self):

        self.user_permission_update_request(
            org_id=self.organization.id,
            user_email=self.user.email,
            permission=OrganizationAuthorization.ROLE_USER,
        )
        retrieve_response = self.user_permission_retrieve_request(
            org_id=self.organization.id, org_user_email=self.user.email
        )

        self.user_permission_remove_request(
            org_id=self.organization.id,
            user_email=self.user.email,
            permission=OrganizationAuthorization.ROLE_USER,
        )
        retrieve_response_removed = self.user_permission_retrieve_request(
            org_id=self.organization.id, org_user_email=self.user.email
        )
        self.assertNotEquals(retrieve_response.role, retrieve_response_removed.role)

    def user_permission_retrieve_request(self, **kwargs):
        return self.user_permission_stub.Retrieve(
            authentication_pb2.UserPermissionRetrieveRequest(**kwargs)
        )

    def user_permission_update_request(self, **kwargs):
        return self.user_permission_stub.Update(
            authentication_pb2.UserPermissionUpdateRequest(**kwargs)
        )

    def user_permission_remove_request(self, **kwargs):
        return self.user_permission_stub.Remove(
            authentication_pb2.UserPermissionUpdateRequest(**kwargs)
        )

    def user_retrieve_request(self, **kwargs):
        return self.user_stub.Retrieve(authentication_pb2.UserRetrieveRequest(**kwargs))
