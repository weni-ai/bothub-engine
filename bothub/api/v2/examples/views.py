from django.conf import settings
from django.db.models import Q
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bothub.common.models import RepositoryExample
from .filters import ExamplesFilter
from ..example.serializers import (
    RepositoryExampleSerializer,
    RepositoriesSearchExamplesSerializer,
    RepositoriesSearchExamplesResponseSerializer,
)
from ..repository.permissions import RepositoryExamplePermission


class ExamplesViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    filter_class = ExamplesFilter
    filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
    search_fields = ["$text", "^text", "=text"]
    ordering_fields = ["created_at"]
    permission_classes = [RepositoryExamplePermission]

    @method_decorator(
        name="create",
        decorator=swagger_auto_schema(
            request_body=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "repositories": openapi.Schema(
                        description="UUID of the repository",
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
                    ),
                    "text": openapi.Schema(type=openapi.TYPE_STRING),
                    "language": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Language abbreviation"
                    ),
                },
            ),
            responses={200: RepositoriesSearchExamplesResponseSerializer(many=True)},
        ),
    )
    @action(
        detail=True,
        methods=["POST"],
        url_name="repositories-examples",
        permission_classes=[],
    )
    def search_repositories_examples(self, request, **kwargs):
        authorization = request.stream.headers.get("Authorization")
        if not authorization == settings.TOKEN_SEARCH_REPOSITORIES:
            raise PermissionDenied()
        serializer = RepositoriesSearchExamplesSerializer(
            data=request.data
        )  # pragma: no cover
        serializer.is_valid(raise_exception=True)  # pragma: no cover

        repositories = self.request.data.get("repositories")
        language = self.request.data.get("language")
        text = self.request.data.get("text")

        examples = RepositoryExample.objects.filter(
            repository_version_language__language=language,
            repository_version_language__repository_version__is_default=True,
            repository_version_language__repository_version__repository__in=repositories,
        ).filter(Q(text__icontains=text) | Q(translations__text__icontains=text))[:5]

        return Response(
            {"result": [example.get_text(language=language) for example in examples]}
        )
