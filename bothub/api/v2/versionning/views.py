from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from bothub.api.v2.versionning.serializers import RepositoryVersionSeralizer
from bothub.common.models import RepositoryUpdate
from .filters import VersioningFilter


class VersioningViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = RepositoryUpdate.objects.order_by('-selected')
    serializer_class = RepositoryVersionSeralizer
    filter_class = VersioningFilter
    # filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    # search_fields = ["$text", "^text", "=text"]
