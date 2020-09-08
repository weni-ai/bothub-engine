import random

from django.db.models import Q
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bothub.common.models import RepositoryExample, RepositoryVersion
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
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            required=["uuid", "language"],
                            properties={
                                "uuid": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="UUID of the repository",
                                ),
                                "language": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="Language abbreviation",
                                ),
                            },
                        ),
                    ),
                    "text": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
            responses={200: RepositoriesSearchExamplesResponseSerializer(many=True)},
        ),
    )
    @action(detail=True, methods=["POST"], url_name="repositories-examples")
    def search_repositories_examples(self, request, **kwargs):
        serializer = RepositoriesSearchExamplesSerializer(
            data=request.data
        )  # pragma: no cover
        serializer.is_valid(raise_exception=True)  # pragma: no cover

        repositories = self.request.data.get("repositories")
        text = self.request.data.get("text")

        result_examples = []

        for repository in repositories:
            examples = (
                get_object_or_404(
                    RepositoryVersion,
                    repository=repository.get("uuid"),
                    repository__allow_search_examples=True,
                    is_default=True,
                )
                .get_version_language(language=repository.get("language"))
                .examples.filter(
                    Q(text__icontains=text) | Q(translations__text__icontains=text)
                )[:5]
            )

            for example in examples:
                result_examples.append(example.get_text(repository.get("language")))

        return Response(
            {"result": random.sample(result_examples, len(result_examples))[:5]}
        )
