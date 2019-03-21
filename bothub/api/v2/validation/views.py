from django.utils.translation import gettext as _

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import APIException
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from bothub.common.models import RepositoryValidation

from .serializers import RepositoryValidationSerializer
from .serializers import NewRepositoryValidationSerializer
from .permissions import RepositoryValidationPermission
from .filters import ValidationFilter


class NewValidationViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    """
    Create new repository validation.
    """
    queryset = RepositoryValidation.objects
    serializer_class = NewRepositoryValidationSerializer
    permission_classes = [IsAuthenticated]


class ListValidationViewSet(
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    """
    Manager repository validation.

    retrieve:
    Get repository validation data.

    delete:
    Delete repository validation.
    """
    queryset = RepositoryValidation.objects
    serializer_class = RepositoryValidationSerializer
    permission_classes = [
        RepositoryValidationPermission,
    ]

    def perform_destroy(self, obj):
        if obj.deleted_in:
            raise APIException(_('Example already deleted'))
        obj.delete()


class ListValidationsViewSet(
        mixins.ListModelMixin,
        GenericViewSet):
    queryset = RepositoryValidation.objects
    serializer_class = RepositoryValidationSerializer
    filter_class = ValidationFilter
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
    permission_classes = [
        RepositoryValidationPermission,
    ]
