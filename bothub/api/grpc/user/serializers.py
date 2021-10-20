from django_grpc_framework import proto_serializers
from rest_framework import serializers

from bothub.authentication.models import User
from weni.protobuf.intelligence import authentication_pb2


class UserProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = User
        proto_class = authentication_pb2.User
        fields = [
            "id",
            "email",
            "nickname",
            "name",
            "language",
            "joined_at",
            "is_active",
            "is_superuser",
        ]


class UserPermissionProtoSerializer(proto_serializers.ProtoSerializer):
    role = serializers.IntegerField()

    class Meta:
        proto_class = authentication_pb2.Permission


class UserLanguageProtoSerializer(proto_serializers.ModelProtoSerializer):
    class Meta:
        model = User
        proto_class = authentication_pb2.User
        fields = ["language"]
        read_only = [
            "id",
            "email",
            "nickname",
            "name",
            "joined_at",
            "is_active",
            "is_superuser",
        ]
