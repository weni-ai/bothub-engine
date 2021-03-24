from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet

from .filters import QAKnowledgeBaseFilter, QAContextFilter
from .permissions import QAKnowledgeBasePermission, QAContextPermission
from .serializers import QAKnowledgeBaseSerializer, QAContextSerializer
from bothub.common.models import QAKnowledgeBase, QAContext


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


class QAContextViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = QAContext.objects.all()
    serializer_class = QAContextSerializer
    filter_class = QAContextFilter
    permission_classes = [permissions.IsAuthenticated, QAContextPermission]
