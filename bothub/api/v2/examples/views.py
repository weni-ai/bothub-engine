from django.conf import settings
from django.db.models import Q
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bothub.common.models import RepositoryExample, RepositoryAuthorization, Repository, RepositoryVersion

from ..example.serializers import (
    RepositoriesSearchExamplesResponseSerializer,
    RepositoriesSearchExamplesSerializer,
    RepositoryExampleSerializer,
)
from ..repository.permissions import RepositoryExamplePermission
from .filters import ExamplesFilter


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
                    "exclude_intents": openapi.Schema(
                        description="Specify the intentions you want to remove from the search",
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING),
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
        exclude_intents = self.request.data.get("exclude_intents", [])

        examples = (
            RepositoryExample.objects.exclude(intent__text__in=exclude_intents)
            .filter(
                Q(repository_version_language__language=language)
                | Q(translations__repository_version_language__language=language),
                repository_version_language__repository_version__is_default=True,
                repository_version_language__repository_version__repository__in=repositories,
            )
            .filter(
                Q(text__unaccent__trigram_similar=text)
                | Q(translations__text__unaccent__trigram_similar=text)
            )
            .distinct()
        )

        return Response(
            {
                "result": [
                    example.get_text(language=language) for example in examples[:5]
                ]
            }
        )

    @action(
        detail=True,
        methods=["GET"],
        url_name="untrained-examples"
    )
    def get_untrained_examples(self, request, **kwargs):
        repository_uuid = request.data.get("repository_uuid")
        user = request.user

        if len(RepositoryAuthorization.objects.filter(user=user, repository__uuid=repository_uuid)) == 0:
            raise PermissionDenied("You don't have permission on that repository.")

        repository = None
        try:
            repository = Repository.objects.get(uuid=repository_uuid)
        except Exception as err:
            raise NotFound(f"Repository does not exists: {err}")

        repository_version = RepositoryVersion.objects.get(repository=repository)
        response = []
        for repository_language in repository_version.version_languages.all():
            response.append({
                "language": repository_language.language,
                "is_trained": len(repository_language.training_log) > 0,
                "texts": [example.text for example in repository_language.examples]
            })
        return Response({"data": response}, status=status.HTTP_200_OK)
