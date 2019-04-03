from django.utils.translation import gettext as _

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import APIException
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from bothub.common.models import RepositoryValidation

from .serializers import RepositoryValidationSerializer
from .permissions import RepositoryValidationPermission
from .filters import ValidationFilter


class ValidationViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    """
    Manager repository validation.

    create:
    Create new repository validation.

    retrieve:
    Get repository validation data.

    update:
    Update example translation.

    partial_update:
    Update, partially, example translation.

    delete:
    Delete repository validation.
    """
    queryset = RepositoryValidation.objects
    serializer_class = RepositoryValidationSerializer
    permission_classes = [
        IsAuthenticated,
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
