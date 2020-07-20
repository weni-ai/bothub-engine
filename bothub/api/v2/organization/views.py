from rest_framework import mixins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from bothub.api.v2.metadata import Metadata
from bothub.authentication.models import RepositoryOwner
from bothub.common.models import Organization, OrganizationAuthorization, Repository
from .serializers import OrganizationSeralizer, OrganizationAuthorizationSerializer
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
    MultipleFieldLookupMixin, mixins.ListModelMixin, GenericViewSet
):
    queryset = OrganizationAuthorization.objects.exclude(
        role=OrganizationAuthorization.ROLE_NOT_SETTED
    )
    serializer_class = OrganizationAuthorizationSerializer
    lookup_fields = ["repository__uuid", "user__nickname"]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        repository_uuid = self.kwargs.get("repository__uuid")
        user_nickname = self.kwargs.get("org__nickname")

        repository = get_object_or_404(Repository, uuid=repository_uuid)
        user = get_object_or_404(RepositoryOwner, nickname=user_nickname)

        obj = repository.get_user_authorization(user)

        self.check_object_permissions(self.request, obj)
        return obj
