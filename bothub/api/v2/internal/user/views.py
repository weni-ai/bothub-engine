from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

from bothub.authentication.models import User
from bothub.common.models import Organization, OrganizationAuthorization
from bothub.api.v2.internal.user.serializers import (
    UserPermissionSerializer,
    UserSerializer,
    UserLanguageSerializer,
)
from bothub import utils


class UserPermissionViewSet(GenericViewSet):
    queryset = OrganizationAuthorization.objects.all()
    serializer_class = UserPermissionSerializer

    @action(detail=True, methods=["get"])
    def retrieve(self, request, **kwargs):
        user, org = utils.get_user_and_organization(
            request.query_params.get("user_email", None),
            request.query_params.get("org_id", None),
        )
        permissions = self._get_user_permissions(org, user)
        serializer = UserPermissionSerializer(permissions)

        return Response(serializer.data)

    @action(detail=True, methods=["put"])
    def update(self, request, **kwargs):
        user, org = utils.get_user_and_organization(
            request.query_params.get("user_email", None),
            request.query_params.get("org_id", None),
        )

        org.set_user_permission(user=user, permission=request.data.get("role", None))

        permissions = self._get_user_permissions(org, user)
        serializer = UserPermissionSerializer(permissions)

        return Response(serializer.data)

    @action(detail=True, methods=["delete"])
    def remove(self, request, **kwargs):
        user, org = utils.get_user_and_organization(
            request.query_params.get("user_email", None),
            request.query_params.get("org_id", None),
        )

        self._get_user_permissions(org, user).delete()

        permissions = self._get_user_permissions(org, user)
        serializer = UserPermissionSerializer(permissions)

        return Response(serializer.data)

    def _get_user_permissions(self, org: Organization, user: User) -> dict:
        return org.organization_authorizations.filter(user=user).first()


class UserViewSet(GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects

    @action(detail=True, methods=["get"])
    def retrive(self, request, **kwargs):
        user, created = User.objects.get_or_create(
            email=self.request.query_params.get("user_email"),
            defaults={"nickname": self.request.query_params.get("user_email")},
        )

        return Response(UserSerializer(user).data)


class UserLanguageViewSet(GenericViewSet):
    serializer_class = UserLanguageSerializer
    queryset = User.objects

    @action(detail=True, methods=["put"])
    def update(self, request, **kwargs):
        user, created = User.objects.get_or_create(
            email=request.query_params.get("user_email"),
            defaults={"nickname": request.query_params.get("user_email")},
        )
        serializer = UserLanguageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.language = request.data["language"]
        user.save()
        return Response(UserLanguageSerializer(user).data)
