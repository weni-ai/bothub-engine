from django_grpc_framework import mixins, generics

from bothub import utils
from bothub.api.grpc.user.serializers import (
    UserProtoSerializer,
    UserPermissionProtoSerializer,
)
from bothub.authentication.models import User
from bothub.common.models import Organization


class UserPermissionService(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.GenericService,
):
    def Retrieve(self, request, context):
        permissions = self.get_user_permissions(
            utils.get_organization(self, request.org_id),
            utils.get_user(self, request.org_user_email),
        )

        serializer = UserPermissionProtoSerializer(permissions)

        return serializer.message

    def Update(self, request, context):
        org = utils.get_organization(self, request.org_id)
        user = utils.get_user(self, request.user_email)

        self.set_user_permission(org, user, request.permission)

        permissions = self.get_user_permissions(org, user)
        serializer = UserPermissionProtoSerializer(permissions)

        return serializer.message

    def Remove(self, request, context):
        org = utils.get_organization(self, request.org_id)
        user = utils.get_user(self, request.user_email)

        self.get_user_permissions(org, user).delete()

        permissions = self.get_user_permissions(org, user)
        serializer = UserPermissionProtoSerializer(permissions)

        return serializer.message

    def set_user_permission(self, org: Organization, user: User, permission: int):
        perm, created = org.organization_authorizations.get_or_create(
            user=user, organization=org
        )
        perm.role = permission
        perm.save(update_fields=["role"])

    def get_user_permissions(self, org: Organization, user: User) -> dict:
        return org.organization_authorizations.filter(user=user).first()


class UserService(mixins.RetrieveModelMixin, generics.GenericService):
    serializer_class = UserProtoSerializer
    queryset = User.objects
    lookup_field = "email"
