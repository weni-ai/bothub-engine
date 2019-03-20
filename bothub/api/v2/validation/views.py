from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from bothub.common.models import RepositoryValidation

from .serializers import RepositoryValidationSerializer
from .permissions import RepositoryValidationPermission
from .filters import ValidationFilter


class ValidationViewSet(
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
