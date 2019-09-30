from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from bothub.common.models import RepositoryExample

from bothub.api.v2.examples.serializers import RepositoryExampleSerializer
from bothub.api.v2.examples.permissions import RepositoryExamplePermission
from .filters import ExamplesFilter


class ExamplesViewSet(
        mixins.ListModelMixin,
        GenericViewSet):
    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    filter_class = ExamplesFilter
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
        RepositoryExamplePermission,
    ]
