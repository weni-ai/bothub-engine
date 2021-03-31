from django_grpc_framework.test import RPCTransactionTestCase

from bothub.api.v2.tests.utils import create_user_and_token
from bothub.common import languages
from bothub.common.models import Repository, Organization, OrganizationAuthorization
from bothub.protos import repository_pb2_grpc, repository_pb2


class RepositoryServiceTestCase(RPCTransactionTestCase):
    def setUp(self):
        super().setUp()
        self.stub = repository_pb2_grpc.RepositoryControllerStub(self.channel)

        self.user, self.user_token = create_user_and_token("user")

        self.organization = Organization.objects.create(name="Weni")

        self.organization.organization_authorizations.create(
            user=self.user, role=OrganizationAuthorization.ROLE_ADMIN
        )

        self.repository = Repository.objects.create(
            name="Repository",
            language=languages.LANGUAGE_PT,
            owner=self.organization.repository_owner
        )

    def test_list(self):
        response_grpc = self.stub.List(repository_pb2.RepositoryListRequest())
        repositories_from_response_grpc = [repository_ for repository_ in response_grpc]

        self.assertEqual(len(repositories_from_response_grpc), 1)
        self.assertTrue(repositories_from_response_grpc[0].name, self.repository.name)

    def test_list_with_filter_by_owner_id(self):
        response_grpc = self.stub.List(repository_pb2.RepositoryListRequest(
            owner_id=self.organization.repository_owner.pk
        ))
        repositories_from_response_grpc = [repository_ for repository_ in response_grpc]

        self.assertEqual(len(repositories_from_response_grpc), 1)
        self.assertTrue(repositories_from_response_grpc[0].name, self.repository.name)

        response_grpc = self.stub.List(repository_pb2.RepositoryListRequest(
            owner_id=100
        ))
        repositories_from_response_grpc = [repository_ for repository_ in response_grpc]

        self.assertEqual(len(repositories_from_response_grpc), 0)
