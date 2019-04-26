from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.filters import SearchFilter

from bothub.common.models import RepositoryEvaluate

from ..metadata import Metadata
from .serializers import RepositoryEvaluateSerializer
# from .permissions import RepositoryPermission
# from .filters import RepositoriesFilter


class EvaluateViewSet(
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
    metadata_class = Metadata
