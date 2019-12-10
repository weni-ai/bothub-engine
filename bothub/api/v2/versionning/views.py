from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from bothub.api.v2.versionning.serializers import RepositoryVersionSeralizer
from bothub.common.models import RepositoryVersion
from .filters import VersioningFilter


class VersioningViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = RepositoryVersion.objects.order_by("-is_default")
    serializer_class = RepositoryVersionSeralizer

    def list(self, request, *args, **kwargs):
        self.filter_class = VersioningFilter
        return super().list(request, *args, **kwargs)
