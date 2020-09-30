from django.db.models import Count, Q
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
        queryset = (
            RepositoryExample.objects.filter(
                repository_version_language__repository_version=self.request.auth.repository_version_language.repository_version,
                repository_version_language__language=self.request.auth.repository_version_language.repository_version.repository.language,
            )
            .annotate(
                translation_count=Count(
                    "translations",
                    filter=Q(
                        translations__language=self.request.auth.repository_version_language.language
                    ),
                )
            )
            .filter(translation_count=0)
        )
        return queryset


class RepositoryTranslationTranslatorExampleViewSet(
    mixins.CreateModelMixin, GenericViewSet
):
    queryset = RepositoryTranslatedExample.objects
    serializer_class = RepositoryTranslatedExampleTranslatorSerializer
    authentication_classes = [TranslatorAuthentication]

    def get_queryset(self, *args, **kwargs):
        queryset = RepositoryTranslatedExample.objects.filter(
            repository_version_language=self.request.auth.repository_version_language
        )
        return queryset
