import grpc
from google.protobuf import empty_pb2
from django_grpc_framework.services import Service
from bothub.common.models import Repository
from bothub.api.grpc.repository.serializers import RepositoryProtoSerializer


class RepositoryService(Service):
    def List(self, request, context):
        clientes = Repository.objects.all()
        print(clientes)
        serializer = RepositoryProtoSerializer(clientes, many=True)
        for msg in serializer.message:
            yield msg
