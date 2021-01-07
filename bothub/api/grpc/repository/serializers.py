from django_grpc_framework import proto_serializers

from bothub.common.models import Repository
from bothub.protos import common_pb2


class RepositoryProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = Repository
        proto_class = common_pb2.Repository
        fields = ["uuid", "name", "slug", "language"]

