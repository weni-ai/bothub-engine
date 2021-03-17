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


class OrgService(generics.GenericService, mixins.ListModelMixin):
    def List(self, request, context):

        user = self.get_user(request)
        orgs = self.get_orgs(user)

        serializer = OrgProtoSerializer(orgs, many=True)

        for msg in serializer.message:
            yield msg

    def Create(self, request, context):
        user, created = User.objects.get_or_create(
            email=request.user_email,
            defaults={'nickname': request.user_nickname},
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
        org = self.get_org_object(request.id)
        user = self.get_user_object(request.user_email)

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

    def get_org_object(self, pk: int) -> Organization:
        try:
            return Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            self.context.abort(
                grpc.StatusCode.NOT_FOUND, f"{Organization.__name__}: {pk} not found!"
            )

    def get_user_object(self, email: str) -> User:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            self.context.abort(
                grpc.StatusCode.NOT_FOUND, f"{User.__name__}: {str} not found!"
            )

    def get_user(self, request):
        user_email = request.user_email

        if not user_email:
            self.context.abort(grpc.StatusCode.NOT_FOUND, "Email cannot be null")

        try:
            return User.objects.get(email=request.user_email)
        except User.DoesNotExist:
            self.context.abort(
                grpc.StatusCode.NOT_FOUND, f"User:{request.user_email} not found!"
            )

    def get_orgs(self, user: User):
        return Organization.objects.filter(
            pk__in=user.organization_user_authorization.exclude(
                role=OrganizationAuthorization.LEVEL_NOTHING
            ).values_list("organization", flat=True)
        )
