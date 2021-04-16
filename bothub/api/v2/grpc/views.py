from rest_framework.response import Response
from rest_framework.views import APIView

from bothub.api.grpc.connect_grpc_client import ConnectGRPCClient
from bothub.api.v2.repository.serializers import RepositorySerializer
from bothub.common.models import Repository


class GRPCListRepositoriesConnectView(APIView):
    def get(self, request, project_uuid):
        grpc_client = ConnectGRPCClient()
        authorizations = grpc_client.list_authorizations(project_uuid=project_uuid)

        repositories = Repository.objects.filter(
            authorizations__uuid__in=authorizations
        )

        serialized_data = RepositorySerializer(repositories, many=True)
        return Response(serialized_data.data)
