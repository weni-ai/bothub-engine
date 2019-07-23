from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import PermissionDenied

from bothub.api.v2.mixins import MultipleFieldLookupMixin
from bothub.common.models import Repository
from bothub.common.models import RepositoryCategory
from bothub.common.models import RepositoryVote
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryUpdate

from ..metadata import Metadata
from .serializers import RepositorySerializer
from .serializers import RepositoryContributionsSerializer
from .serializers import RepositoryVotesSerializer
from .serializers import RepositoryCategorySerializer
from .serializers import ShortRepositorySerializer
from .serializers import NewRepositorySerializer
from .serializers import RepositoryTranslatedExampleSerializer
from .serializers import RepositoryExampleSerializer
from .serializers import NewRepositoryTranslatedExampleSerializer
from .serializers import RepositoryUpdateSerializer
from .serializers import EditRepositorySerializer
from .serializers import RepositoryAuthorizationSerializer
from .serializers import AnalyzeTextSerializer
from .serializers import EvaluateSerializer
from .permissions import RepositoryPermission
from .permissions import CUSTOM_WRITE_METHODS
from .permissions import RepositoryTranslatedExamplePermission
from .permissions import RepositoryExamplePermission
from .permissions import RepositoryUpdateHasPermission
from .filters import RepositoriesFilter
from .filters import RepositoryTranslationsFilter
from .filters import RepositoryUpdatesFilter


class RepositoryViewSet(
        MultipleFieldLookupMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    """
    Manager repository.

    retrieve:
    Get repository data.

    update:
    Update your repository.

    partial_update:
    Update, partially, your repository.

    delete:
    Delete your repository.
    """
    queryset = Repository.objects
    lookup_field = 'slug'
    lookup_fields = ['owner__nickname', 'slug']
    serializer_class = RepositorySerializer
    edit_serializer_class = EditRepositorySerializer
    permission_classes = [
        RepositoryPermission,
    ]

    @action(
        detail=True,
        methods=['GET'],
        url_name='repository-languages-status')
    def languagesstatus(self, request, **kwargs):
        """
        Get current language status.
        """
        repository = self.get_object()
        return Response({
            'languages_status': repository.languages_status,
        })

    @action(
        detail=True,
        methods=['POST'],
        url_name='repository-analyze',
        permission_classes=[])
    def analyze(self, request, **kwargs):
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        serializer = AnalyzeTextSerializer(
            data=request.data)  # pragma: no cover
        serializer.is_valid(raise_exception=True)  # pragma: no cover
        request = Repository.request_nlp_analyze(
            user_authorization,
            serializer.data)  # pragma: no cover

        if request.status_code == status.HTTP_200_OK:  # pragma: no cover
            return Response(request.json())  # pragma: no cover

        response = None  # pragma: no cover
        try:  # pragma: no cover
            response = request.json()  # pragma: no cover
        except Exception:
            pass

        if not response:  # pragma: no cover
            raise APIException(  # pragma: no cover
                detail=_('Something unexpected happened! ' + \
                         'We couldn\'t analyze your text.'))
        error = response.get('error')  # pragma: no cover
        message = error.get('message')  # pragma: no cover
        raise APIException(detail=message)  # pragma: no cover

    def get_serializer_class(self):
        if self.request and self.request.method in \
           ['OPTIONS'] + CUSTOM_WRITE_METHODS or not self.request:
            return self.edit_serializer_class
        return self.serializer_class

    def get_action_permissions_classes(self):
        if not self.action:
            return None
        fn = getattr(self, self.action, None)
        if not fn:
            return None
        fn_kwargs = getattr(fn, 'kwargs', None)
        if not fn_kwargs:
            return None
        permission_classes = fn_kwargs.get('permission_classes')
        if not permission_classes:
            return None
        return permission_classes

    def get_permissions(self):
        action_permissions_classes = self.get_action_permissions_classes()
        if action_permissions_classes:
            return [permission()
                    for permission
                    in action_permissions_classes]
        return super().get_permissions()


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


class RepositoryTranslatedExampleViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    """
    Manager example translation.

    retrieve:
    Get example translation data.

    update:
    Update example translation.

    partial_update:
    Update, partially, example translation.

    delete:
    Delete example translation.
    """
    queryset = RepositoryTranslatedExample.objects
    serializer_class = RepositoryTranslatedExampleSerializer
    permission_classes = [
        IsAuthenticated,
        RepositoryTranslatedExamplePermission,
    ]


class RepositoryExampleViewSet(
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

    def perform_destroy(self, obj):
        if obj.deleted_in:
            raise APIException(_('Example already deleted'))
        obj.delete()


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


class NewRepositoryTranslatedExampleViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    """
    Translate example
    """
    queryset = RepositoryTranslatedExample.objects
    serializer_class = NewRepositoryTranslatedExampleSerializer
    permission_classes = [IsAuthenticated]


class RepositoryTranslationsViewSet(
        mixins.ListModelMixin,
        GenericViewSet):
    """
    List repository translations.
    """
    serializer_class = RepositoryTranslatedExampleSerializer
    queryset = RepositoryTranslatedExample.objects.all()
    filter_class = RepositoryTranslationsFilter


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
