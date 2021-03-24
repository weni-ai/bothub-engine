import grpc
from django_grpc_framework import generics, mixins
from google.protobuf import empty_pb2

from bothub import utils
from bothub.api.grpc.organization.serializers import (
    OrgProtoSerializer,
    OrgCreateProtoSerializer,
    OrgUpdateProtoSerializer,
)
from bothub.authentication.models import User, RepositoryOwner
from bothub.common.models import Organization, OrganizationAuthorization


class OrgService(mixins.ListModelMixin, generics.GenericService):
    def List(self, request, context):

        user = utils.get_user(self, request.user_email)

        serializer = OrgProtoSerializer(user.get_user_organizations, many=True)

        for msg in serializer.message:
            yield msg

    def Create(self, request, context):
        user, created = User.objects.get_or_create(
            email=request.user_email, defaults={"nickname": request.user_nickname}
        )

        serializer = OrgCreateProtoSerializer(message=request)
        serializer.is_valid(raise_exception=True)

        validated_data = {
            "name": serializer.validated_data.get("name"),
            "nickname": utils.organization_unique_slug_generator(
                serializer.validated_data.get("name"), RepositoryOwner
            ),
            "description": "",
            "locale": "",
        }

        org = Organization.objects.create(**validated_data)

        org.organization_authorizations.create(
            user=user, role=OrganizationAuthorization.ROLE_ADMIN
        )

        org_serializer = OrgProtoSerializer(org)

        return org_serializer.message

    def Destroy(self, request, context):
        org = utils.get_organization(self, request.id)
        user = utils.get_user(self, request.user_email)

        perm = org.organization_authorizations.get(user=user)
        if perm.is_admin:
            org.delete()
            return empty_pb2.Empty()
        self.context.abort(grpc.StatusCode.PERMISSION_DENIED)

    def Update(self, request, context):
        serializer = OrgUpdateProtoSerializer(message=request)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return serializer.message
