from django.utils.decorators import method_decorator

from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema

from bothub.common.models import QAKnowledgeBase, QAtext
from .filters import QAKnowledgeBaseFilter, QAtextFilter
from .permissions import QAKnowledgeBasePermission, QAtextPermission
from .serializers import QAKnowledgeBaseSerializer, QAtextSerializer


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "repository_uuid",
                openapi.IN_QUERY,
                description="Repository's UUID",
                required=True,
                type=openapi.TYPE_STRING,
                format="uuid",
            ),
        ]
    ),
)
class QAKnowledgeBaseViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = QAKnowledgeBase.objects.all()
    serializer_class = QAKnowledgeBaseSerializer
    filter_class = QAKnowledgeBaseFilter
    permission_classes = [permissions.IsAuthenticated, QAKnowledgeBasePermission]


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "repository_uuid",
                openapi.IN_QUERY,
                description="Repository's UUID",
                required=True,
                type=openapi.TYPE_STRING,
                format="uuid",
            ),
        ]
    ),
)
class QAtextViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = QAtext.objects.all()
    serializer_class = QAtextSerializer
    filter_class = QAtextFilter
    permission_classes = [permissions.IsAuthenticated, QAtextPermission]
