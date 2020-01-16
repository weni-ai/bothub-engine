from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.filters import SearchFilter
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from bothub.api.v2.metadata import Metadata
from bothub.api.v2.versionning.permissions import RepositoryVersionHasPermission
from bothub.api.v2.versionning.serializers import RepositoryVersionSeralizer
from bothub.common.models import RepositoryVersion
from .filters import VersioningFilter


class RepositoryVersionViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = RepositoryVersion.objects.order_by("-is_default")
    serializer_class = RepositoryVersionSeralizer
    permission_classes = [IsAuthenticated, RepositoryVersionHasPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    search_fields = ["$name", "^name", "=name"]
    metadata_class = Metadata

    def list(self, request, *args, **kwargs):
        self.filter_class = VersioningFilter

        return super().list(request, *args, **kwargs)
