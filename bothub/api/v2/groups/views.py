from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from bothub.api.v2.groups.permissions import RepositoryEntityGroupHasPermission
from bothub.api.v2.groups.serializers import RepositoryEntityGroupSeralizer
from bothub.api.v2.metadata import Metadata
from bothub.common.models import RepositoryEntityGroup


class RepositoryEntityGroupViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, GenericViewSet
):
    queryset = RepositoryEntityGroup.objects
    serializer_class = RepositoryEntityGroupSeralizer
    permission_classes = [IsAuthenticated, RepositoryEntityGroupHasPermission]
    metadata_class = Metadata
