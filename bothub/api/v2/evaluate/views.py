from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter
from rest_framework.filters import OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from bothub.common.models import RepositoryEvaluate

from ..metadata import Metadata
from .serializers import RepositoryEvaluateSerializer
# from .permissions import RepositoryPermission
from .filters import EvaluatesFilter


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
        # RepositoryPermission,
    ]
    filter_class = EvaluatesFilter
    filter_backends = [
        OrderingFilter,
        SearchFilter,
        DjangoFilterBackend,
    ]
    search_fields = [
        '$text',
        '^text',
        '=text',
    ]
    ordering_fields = [
        'created_at',
    ]
    metadata_class = Metadata
