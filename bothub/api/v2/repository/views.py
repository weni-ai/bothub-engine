from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from bothub.common.models import Repository
from bothub.common.models import RepositoryCategory
from bothub.common.models import RepositoryVote
from bothub.common.models import RepositoryAuthorization

from ..metadata import Metadata
from .serializers import RepositorySerializer
from .serializers import RepositoryContributionsSerializer
from .serializers import RepositoryVotesSerializer
from .serializers import RepositoryCategorySerializer
from .serializers import ShortRepositorySerializer
from .serializers import NewRepositorySerializer
from .permissions import RepositoryPermission
from .filters import RepositoriesFilter


class RepositoryViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    """
    Manager repository (bot).
    """
    queryset = Repository.objects
    lookup_field = 'uuid'
    serializer_class = RepositorySerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        RepositoryPermission,
    ]
    metadata_class = Metadata


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'user',
                openapi.IN_QUERY,
                description='Nickname User to find repositories votes',
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'repository',
                openapi.IN_QUERY,
                description='Repository UUID, returns a list of '
                            'users who voted for this repository',
                type=openapi.TYPE_STRING
            ),
        ]
    )
)
class RepositoryVotesViewSet(
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        mixins.ListModelMixin,
        GenericViewSet):
    """
    Manager repository votes (bot).
    """
    queryset = RepositoryVote.objects.all()
    lookup_field = 'repository'
    lookup_fields = ['repository']
    serializer_class = RepositoryVotesSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly
    ]
    metadata_class = Metadata

    def get_queryset(self, *args, **kwargs):
        if self.request.query_params.get('repository', None):
            return self.queryset.filter(
                repository=self.request.query_params.get(
                    'repository',
                    None
                )
            )
        elif self.request.query_params.get('user', None):
            return self.queryset.filter(
                user__nickname=self.request.query_params.get(
                    'user',
                    None
                )
            )
        else:
            return self.queryset.all()

    def destroy(self, request, *args, **kwargs):
        self.queryset.filter(
            repository=self.request.query_params.get(
                'repository',
                None
            ),
            user=self.request.user
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RepositoriesViewSet(
        mixins.ListModelMixin,
        GenericViewSet):
    """
    List all public repositories.
    """
    serializer_class = ShortRepositorySerializer
    queryset = Repository.objects.all().publics().order_by_relevance()
    filter_class = RepositoriesFilter
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
    ]
    search_fields = [
        '$name',
        '^name',
        '=name',
    ]


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'nickname',
                openapi.IN_QUERY,
                description='Nickname User',
                type=openapi.TYPE_STRING,
                required=True
            ),
        ]
    )
)
class RepositoriesContributionsViewSet(
        mixins.ListModelMixin,
        GenericViewSet):
    """
    List Repositories Contributions by user.
    """
    serializer_class = RepositoryContributionsSerializer
    queryset = RepositoryAuthorization.objects.all()
    permission_classes = [
        IsAuthenticatedOrReadOnly
    ]
    lookup_field = 'nickname'

    def get_queryset(self):
        if self.request.query_params.get('nickname', None):
            return self.queryset.filter(
                user__nickname=self.request.query_params.get(
                    'nickname',
                    None
                )
            )
        else:
            return self.queryset.none()


class RepositoryCategoriesViewSet(mixins.ListModelMixin, GenericViewSet):
    """
    List all categories.
    """
    serializer_class = RepositoryCategorySerializer
    queryset = RepositoryCategory.objects.all()
    pagination_class = None


class NewRepositoryViewSet(mixins.CreateModelMixin, GenericViewSet):
    """
    Create a new Repository, add examples and train a bot.
    """
    queryset = Repository.objects
    serializer_class = NewRepositorySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            RepositorySerializer(instance).data,
            status=status.HTTP_201_CREATED,
            headers=headers)
