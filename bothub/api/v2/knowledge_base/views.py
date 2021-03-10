from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet

from .serializers import QAKnowledgeBaseSerializer
from bothub.common.models import QAKnowledgeBase


class QAKnowledgeBaseViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = QAKnowledgeBase.objects.all()
    serializer_class = QAKnowledgeBaseSerializer
    permission_classes = [permissions.IsAuthenticated]
