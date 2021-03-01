from django.utils.decorators import method_decorator
from drf_yasg2 import openapi
from drf_yasg2.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.filters import OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend

from bothub.common.models import RepositoryEvaluate
from bothub.common.models import RepositoryEvaluateResult

from ..metadata import Metadata
from .serializers import RepositoryEvaluateSerializer
from .serializers import RepositoryEvaluateResultVersionsSerializer
from .serializers import RepositoryEvaluateResultSerializer

from .filters import EvaluatesFilter
from .filters import EvaluateResultsFilter
from .filters import EvaluateResultFilter

from .permissions import RepositoryEvaluatePermission
from .permissions import RepositoryEvaluateResultPermission


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "repository_uuid",
                openapi.IN_QUERY,
                description="Repository UUID, calling " "the parameter through url",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ]
    ),
)
@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "repository_uuid",
                openapi.IN_QUERY,
                description="Repository UUID, calling " "the parameter through url",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ]
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "repository_uuid",
                openapi.IN_QUERY,
                description="Repository UUID, calling " "the parameter through url",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ]
    ),
)
@method_decorator(
    name="update",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "repository_uuid",
                openapi.IN_QUERY,
                description="Repository UUID, calling " "the parameter through url",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ]
    ),
)
@method_decorator(
    name="partial_update",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "repository_uuid",
                openapi.IN_QUERY,
                description="Repository UUID, calling " "the parameter through url",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ]
    ),
)
@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "repository_uuid",
                openapi.IN_QUERY,
                description="Repository UUID, calling " "the parameter through url",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ]
    ),
)
class EvaluateViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    """
    Manager evaluate (tests).
    """

    queryset = RepositoryEvaluate.objects
    serializer_class = RepositoryEvaluateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, RepositoryEvaluatePermission]
    metadata_class = Metadata

    def list(self, request, *args, **kwargs):
        self.filter_class = EvaluatesFilter
        self.filter_backends = [OrderingFilter, SearchFilter, DjangoFilterBackend]
        self.search_fields = ["$text", "^text", "=text"]
        self.ordering_fields = ["created_at"]
        return super().list(request, *args, **kwargs)


@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "intent",
                openapi.IN_QUERY,
                description="Filter a desired intent",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "min",
                openapi.IN_QUERY,
                description="Filter Confidence Percentage",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "max",
                openapi.IN_QUERY,
                description="Filter Confidence Percentage",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "repository_uuid",
                openapi.IN_QUERY,
                description="Repository UUID, calling " "the parameter through url",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ]
    ),
)
class ResultsListViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet
):

    queryset = RepositoryEvaluateResult.objects
    serializer_class = RepositoryEvaluateResultVersionsSerializer
    permission_classes = [IsAuthenticated, RepositoryEvaluateResultPermission]
    filter_class = EvaluateResultsFilter
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filter_fields = ["cross_validation"]
    ordering_fields = ["created_at"]

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = RepositoryEvaluateResultSerializer
        self.filter_class = EvaluateResultFilter
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=["GET"], url_name="compare_results")
    def compare_results(self, request, **kwargs):
        try:
            results_ids_to_compare = request.query_params.get("ids", "").split(",")
            results = self.get_queryset().filter(pk__in=results_ids_to_compare)
            serializer = RepositoryEvaluateResultSerializer(results, many=True, context={"request": request})
        except ValueError:
            return Response(
                {"detail": "Send only integers in the 'ids' parameter. If there is a ',' left, remove it."},
                400
            )

        return Response(serializer.data, 200)
