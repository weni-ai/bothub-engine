from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from bothub.api.v2.example.serializers import RepositoryExampleSerializer
from bothub.api.v2.translator.filters import (
    TranslatorExamplesFilter,
    RepositoryTranslatorFilter,
)
from bothub.api.v2.translator.permissions import (
    RepositoryExampleTranslatorPermission,
    RepositoryTranslatorPermission,
)
from bothub.api.v2.translator.serializers import (
    RepositoryTranslatedExampleTranslatorSerializer,
    RepositoryTranslatorSerializer,
)
from bothub.authentication.authorization import TranslatorAuthentication
from bothub.common.models import (
    RepositoryExample,
    RepositoryTranslatedExample,
    RepositoryTranslator,
)


class RepositoryTranslatorViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    """
    Manage all external translators
    """

    queryset = RepositoryTranslator.objects
    serializer_class = RepositoryTranslatorSerializer
    permission_classes = [IsAuthenticated, RepositoryTranslatorPermission]

    def list(self, request, *args, **kwargs):
        self.filter_class = RepositoryTranslatorFilter
        return super().list(request, *args, **kwargs)


class TranslatorExamplesViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    filter_class = TranslatorExamplesFilter
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    search_fields = ["$text", "^text", "=text"]
    ordering_fields = ["created_at"]
    authentication_classes = [TranslatorAuthentication]
    permission_classes = [RepositoryExampleTranslatorPermission]

    def get_queryset(self, *args, **kwargs):
        if getattr(self, "swagger_fake_view", False):
            # queryset just for schema generation metadata
            return RepositoryExample.objects.none()
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=self.request.auth.repository_version_language.repository_version,
            repository_version_language__language=self.request.auth.repository_version_language.repository_version.repository.language,
        )
        return queryset


class RepositoryTranslationTranslatorExampleViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = RepositoryTranslatedExample.objects
    serializer_class = RepositoryTranslatedExampleTranslatorSerializer
    authentication_classes = [TranslatorAuthentication]

    def get_queryset(self, *args, **kwargs):
        if getattr(self, "swagger_fake_view", False):
            # queryset just for schema generation metadata
            return RepositoryTranslatedExample.objects.none()
        queryset = RepositoryTranslatedExample.objects.filter(
            repository_version_language=self.request.auth.repository_version_language
        )
        return queryset
