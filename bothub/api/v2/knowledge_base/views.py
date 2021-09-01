from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet

from .filters import QAKnowledgeBaseFilter, QAtextFilter
from .permissions import QAKnowledgeBasePermission, QAtextPermission
from .serializers import QAKnowledgeBaseSerializer, QAtextSerializer
from bothub.common.models import QAKnowledgeBase, QAtext


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
