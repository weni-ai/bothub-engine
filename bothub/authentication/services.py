from django_grpc_framework import mixins

from bothub.api.grpc.user.serializers import (
    UserProtoSerializer,
    UserPermissionProtoSerializer,
)
from bothub.authentication.models import User
from bothub.common.models import Organization
from bothub.utils import AbstractUserService


class UserService(AbstractUserService, mixins.RetrieveModelMixin):
    serializer_class = UserProtoSerializer

    def get_user_object(self, email: str) -> User:
        return self._get_object(User, email, query_parameter="email")

    def get_object(self):
        return self.get_user_object(self.request.email)


class UserPermissionService(
    AbstractUserService, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    def Retrieve(self, request, context):
        org = self.get_org_object(request.org_id)
        user = self.get_user_object(request.user_id)

        permissions = self.get_user_permissions(org, user)

        serializer = UserPermissionProtoSerializer(permissions)

        return serializer.message

    def Update(self, request, context):
        org = self.get_org_object(request.org_id)
        user = self.get_user_object(request.user_id)

        self.set_user_permission(org, user, request.permission)

        permissions = self.get_user_permissions(org, user)
        serializer = UserPermissionProtoSerializer(permissions)

        return serializer.message

    def Remove(self, request, context):
        org = self.get_org_object(request.org_id)
        user = self.get_user_object(request.user_id)

        self.remove_user_permission(org, user, request.permission)

        permissions = self.get_user_permissions(org, user)
        serializer = UserPermissionProtoSerializer(permissions)

        return serializer.message

    def remove_user_permission(self, org: Organization, user: User, permission: str):
        permissions = self.get_user_permissions(org, user)
        permissions.delete()

    def set_user_permission(self, org: Organization, user: User, permission: int):
        perm, created = org.organization_authorizations.get_or_create(
            user=user, organization=org
        )
        perm.role = permission
        perm.save(update_fields=["role"])

    def get_user_permissions(self, org: Organization, user: User) -> dict:
        return org.organization_authorizations.filter(user=user).first()
