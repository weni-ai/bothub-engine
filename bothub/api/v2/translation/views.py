from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework import permissions
from bothub.common.models import RepositoryTranslatedExample

from bothub.api.v2.translation.permissions import \
    RepositoryTranslatedExamplePermission
from bothub.api.v2.translation.serializers import \
    RepositoryTranslatedExampleSerializer
from bothub.api.v2.translation.filters import TranslationsFilter


class RepositoryTranslatedExampleViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    """
    Manager example translation.

    list:
    Get example translation data.

    retrieve:
    Get example translation data.

    update:
    Update example translation.

    partial_update:
    Update, partially, example translation.

    delete:
    Delete example translation.
    """
    queryset = RepositoryTranslatedExample.objects
    serializer_class = RepositoryTranslatedExampleSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        RepositoryTranslatedExamplePermission,
    ]

    def create(self, request, *args, **kwargs):
        self.permission_classes = [permissions.IsAuthenticated]
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.queryset = RepositoryTranslatedExample.objects.all()
        self.filter_class = TranslationsFilter
        return super().list(request, *args, **kwargs)
