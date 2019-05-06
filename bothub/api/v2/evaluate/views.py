from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter
from rest_framework.filters import OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from bothub.common.models import RepositoryEvaluate
from bothub.common.models import RepositoryEvaluateResult

from ..metadata import Metadata
from .serializers import RepositoryEvaluateSerializer
from .serializers import RepositoryEvaluateResultVersionsSerializer
from .serializers import RepositoryEvaluateResultSerializer

from .filters import EvaluatesFilter
from .filters import EvaluateResultsFilter
from .filters import EvaluateResultFilter

from .permissions import RepositoryEvaluatePermission
from .permissions import RepositoryEvaluateResultPermission


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


class ResultsListViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        GenericViewSet):

    queryset = RepositoryEvaluateResult.objects
    serializer_class = RepositoryEvaluateResultVersionsSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        RepositoryEvaluateResultPermission,
    ]
    filter_class = EvaluateResultsFilter
    filter_backends = [
        OrderingFilter,
        DjangoFilterBackend,
    ]
    ordering_fields = [
        'created_at',
    ]

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = RepositoryEvaluateResultSerializer
        self.filter_class = EvaluateResultFilter
        return super().retrieve(request, *args, **kwargs)
