from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework import status
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import APIException

from bothub.api.v2.mixins import MultipleFieldLookupMixin
from bothub.authentication.models import User
from bothub.common.models import Repository
from bothub.common.models import RepositoryVote
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RepositoryCategory
from bothub.common.models import RequestRepositoryAuthorization
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryUpdate

from ..metadata import Metadata
from .serializers import RepositorySerializer
from .serializers import RepositoryAuthorizationRoleSerializer
from .serializers import RepositoryContributionsSerializer
from .serializers import RepositoryVotesSerializer
from .serializers import ShortRepositorySerializer
from .serializers import RepositoryCategorySerializer
from .serializers import RepositoryAuthorizationSerializer
from .serializers import RequestRepositoryAuthorizationSerializer
from .serializers import RepositoryExampleSerializer
from .serializers import RepositoryUpdateSerializer
from .permissions import RepositoryPermission
from .permissions import RepositoryAdminManagerAuthorization
from .permissions import RepositoryExamplePermission
from .permissions import RepositoryUpdateHasPermission
from .filters import RepositoriesFilter
from .filters import RepositoryAuthorizationFilter
from .filters import RepositoryAuthorizationRequestsFilter
from .filters import RepositoryUpdatesFilter


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


class RepositoryCategoriesView(
        mixins.ListModelMixin,
        GenericViewSet):
    """
    List all categories.
    """
    serializer_class = RepositoryCategorySerializer
    queryset = RepositoryCategory.objects.all()
    pagination_class = None


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'nickname',
                openapi.IN_QUERY,
                description='Nickname User to find repositories',
                type=openapi.TYPE_STRING
            ),
        ]
    )
)
class SearchRepositoriesViewSet(
        mixins.ListModelMixin,
        GenericViewSet):
    """
    List all user's repositories
    """
    queryset = Repository.objects
    serializer_class = RepositorySerializer
    lookup_field = 'nickname'

    def get_queryset(self, *args, **kwargs):
        try:
            if self.request.query_params.get('nickname', None):
                return self.queryset.filter(
                    owner__nickname=self.request.query_params.get(
                        'nickname',
                        self.request.user
                    )
                )
            else:
                return self.queryset.filter(owner=self.request.user)
        except TypeError:
            return self.queryset.none()


class RepositoryAuthorizationViewSet(
        MultipleFieldLookupMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        GenericViewSet):
    queryset = RepositoryAuthorization.objects.exclude(
        role=RepositoryAuthorization.ROLE_NOT_SETTED)
    serializer_class = RepositoryAuthorizationSerializer
    filter_class = RepositoryAuthorizationFilter
    lookup_fields = ['repository__uuid', 'user__nickname']
    permission_classes = [
        IsAuthenticated,
    ]

    def get_object(self):
        repository_uuid = self.kwargs.get('repository__uuid')
        user_nickname = self.kwargs.get('user__nickname')

        repository = get_object_or_404(Repository, uuid=repository_uuid)
        user = get_object_or_404(User, nickname=user_nickname)

        obj = repository.get_user_authorization(user)

        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, *args, **kwargs):
        self.lookup_field = 'user__nickname'

        self.filter_class = None
        self.serializer_class = RepositoryAuthorizationRoleSerializer
        self.permission_classes = [
            IsAuthenticated,
            RepositoryAdminManagerAuthorization,
        ]
        response = super().update(*args, **kwargs)
        instance = self.get_object()
        if instance.role is not RepositoryAuthorization.ROLE_NOT_SETTED:
            instance.send_new_role_email(self.request.user)
        return response

    def list(self, request, *args, **kwargs):
        self.lookup_fields = []
        return super().list(request, *args, **kwargs)


class RepositoryAuthorizationRequestsViewSet(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    """
    List of all authorization requests for a repository
    """
    queryset = RequestRepositoryAuthorization.objects.exclude(
        approved_by__isnull=False)
    serializer_class = RequestRepositoryAuthorizationSerializer
    filter_class = RepositoryAuthorizationRequestsFilter
    permission_classes = [
        IsAuthenticated,
    ]

    def create(self, request, *args, **kwargs):
        self.queryset = RequestRepositoryAuthorization.objects
        self.filter_class = None
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.queryset = RequestRepositoryAuthorization.objects
        self.filter_class = None
        self.permission_classes = [
            IsAuthenticated,
            RepositoryAdminManagerAuthorization,
        ]
        try:
            return super().update(request, *args, **kwargs)
        except DjangoValidationError as e:
            raise ValidationError(e.message)

    def destroy(self, request, *args, **kwargs):
        self.queryset = RequestRepositoryAuthorization.objects
        self.filter_class = None
        self.permission_classes = [
            IsAuthenticated,
            RepositoryAdminManagerAuthorization,
        ]
        return super().destroy(request, *args, **kwargs)


class RepositoryExampleViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        GenericViewSet):
    """
    Manager repository example.

    retrieve:
    Get repository example data.

    delete:
    Delete repository example.

    update:
    Update repository example.

    """
    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    permission_classes = [
        RepositoryExamplePermission,
    ]

    def create(self, request, *args, **kwargs):
        self.permission_classes = [permissions.IsAuthenticated]
        return super().create(request, *args, **kwargs)

    def perform_destroy(self, obj):
        if obj.deleted_in:
            raise APIException(_('Example already deleted'))
        obj.delete()


class RepositoryUpdatesViewSet(
      mixins.ListModelMixin,
      GenericViewSet):
    queryset = RepositoryUpdate.objects.filter(
        training_started_at__isnull=False).order_by('-trained_at')
    serializer_class = RepositoryUpdateSerializer
    filter_class = RepositoryUpdatesFilter
    permission_classes = [
        IsAuthenticated,
        RepositoryUpdateHasPermission,
    ]
