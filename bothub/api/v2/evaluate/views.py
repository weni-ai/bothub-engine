from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter
from rest_framework.filters import OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from bothub.common.models import RepositoryEvaluate

from ..metadata import Metadata
from .serializers import RepositoryEvaluateSerializer
from .filters import EvaluatesFilter
from .permissions import RepositoryEvaluatePermission


class EvaluateViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    """
    Manager evaluate (tests).
    """
    queryset = RepositoryEvaluate.objects
    serializer_class = RepositoryEvaluateSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        RepositoryEvaluatePermission,
    ]
    metadata_class = Metadata

    def list(self, request, *args, **kwargs):
        self.filter_class = EvaluatesFilter
        self.filter_backends = [
            OrderingFilter,
            SearchFilter,
            DjangoFilterBackend,
        ]
        self.search_fields = [
            '$text',
            '^text',
            '=text',
        ]
        self.ordering_fields = [
            'created_at',
        ]

        return super().list(request, *args, **kwargs)
