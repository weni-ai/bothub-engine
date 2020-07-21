from rest_framework import mixins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import PermissionDenied

from bothub.api.v2.metadata import Metadata
from bothub.authentication.models import RepositoryOwner, User
from bothub.common.models import Organization, OrganizationAuthorization, Repository
from .filters import OrganizationAuthorizationFilter
from .permissions import OrganizationAdminManagerAuthorization
from .serializers import (
    OrganizationSeralizer,
    OrganizationAuthorizationSerializer,
    OrganizationAuthorizationRoleSerializer,
)
from ..mixins import MultipleFieldLookupMixin


class OrganizationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSeralizer
    permission_classes = [IsAuthenticated]  # , OrganizationHasPermission]
    lookup_field = "nickname"
    metadata_class = Metadata


class OrganizationProfileViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    """
    Get organization profile
    """

    serializer_class = OrganizationSeralizer
    queryset = Organization.objects
    lookup_field = "nickname"


class OrganizationAuthorizationViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = OrganizationAuthorization.objects.exclude(
        role=OrganizationAuthorization.ROLE_NOT_SETTED
    )
    serializer_class = OrganizationAuthorizationSerializer
    filter_class = OrganizationAuthorizationFilter
    permission_classes = [IsAuthenticated]
    lookup_fields = ["organization_nickname", "user__nickname"]

    def get_object(self):
        organization = get_object_or_404(
            Organization, nickname=self.kwargs.get("organization_nickname")
        )
        user = get_object_or_404(User, nickname=self.kwargs.get("user__nickname"))

        obj = organization.get_organization_authorization(user)

        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, *args, **kwargs):
        self.filter_class = None
        self.serializer_class = OrganizationAuthorizationRoleSerializer
        self.permission_classes = [
            IsAuthenticated,
            OrganizationAdminManagerAuthorization,
        ]
        response = super().update(*args, **kwargs)
        self.get_object()
        return response

    def destroy(self, request, *args, **kwargs):
        self.filter_class = None
        self.serializer_class = OrganizationAuthorizationRoleSerializer
        self.permission_classes = [
            IsAuthenticated,
            OrganizationAdminManagerAuthorization,
        ]
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        user = self.kwargs.get("user__nickname")

        if self.request.user.nickname == user:
            raise PermissionDenied(_("You cannot delete your own user."))

        return super().perform_destroy(instance)
