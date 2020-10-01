from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, APIException
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
from bothub.celery import app as celery_app
from bothub.common import languages
from bothub.common.models import (
    RepositoryExample,
    RepositoryTranslatedExample,
    RepositoryTranslator,
    RepositoryQueueTask,
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

    @action(
        detail=True,
        methods=["POST"],
        url_name="repository-auto-translation",
        permission_classes=[],
        authentication_classes=[TranslatorAuthentication],
    )
    def auto_translation(self, request, **kwargs):
        repository_version = request.auth.repository_version_language.repository_version
        user_authorization = repository_version.repository.get_user_authorization(
            request.user
        )

        if not user_authorization.can_translate:
            raise PermissionDenied()

        # Validates if the language is available
        languages.validate_language(
            value=request.auth.repository_version_language.language
        )

        if (
            request.auth.repository_version_language.language
            not in languages.GOOGLE_API_TRANSLATION_LANGUAGES_SUPPORTED
        ):
            raise APIException(  # pragma: no cover
                detail=_("This language is not available in machine translation")
            )

        if (
            repository_version.repository.language
            == request.auth.repository_version_language.language
        ):
            raise APIException(  # pragma: no cover
                detail=_(
                    "It is not possible to translate the base language into your own language"
                )
            )

        queue_running = (
            repository_version.get_version_language(
                language=request.auth.repository_version_language.language
            )
            .queues.filter(
                Q(status=RepositoryQueueTask.STATUS_PENDING)
                | Q(status=RepositoryQueueTask.STATUS_PROCESSING)
            )
            .filter(
                Q(type_processing=RepositoryQueueTask.TYPE_PROCESSING_AUTO_TRANSLATE)
            )
        )

        if queue_running:
            raise APIException(  # pragma: no cover
                detail=_(
                    "It is only possible to perform an automatic translation per language, a translation is already running"
                )
            )

        task = celery_app.send_task(
            "auto_translation",
            args=[
                repository_version.pk,
                repository_version.repository.language,
                request.auth.repository_version_language.language,
            ],
        )

        return Response({"id_queue": task.task_id})
