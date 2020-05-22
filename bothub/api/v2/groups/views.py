from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from bothub.api.v2.metadata import Metadata
from bothub.api.v2.groups.serializers import RepositoryEntityGroupSeralizer
from bothub.common.models import RepositoryEntity


class RepositoryEntityViewSet(
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = RepositoryEntity.objects
    serializer_class = RepositoryEntityGroupSeralizer
    # permission_classes = [IsAuthenticated, RepositoryVersionHasPermission]
    # filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    # search_fields = ["$name", "^name", "=name"]
    metadata_class = Metadata
