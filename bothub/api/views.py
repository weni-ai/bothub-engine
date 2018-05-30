from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework import permissions
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.filters import OrderingFilter
from django.utils.translation import gettext as _
from django.db.models import Count
from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q

from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryTranslatedExampleEntity
from bothub.common.models import RepositoryCategory
from bothub.authentication.models import User

from .serializers import RepositorySerializer
from .serializers import NewRepositorySerializer
from .serializers import RepositoryExampleSerializer
from .serializers import RepositoryAuthorizationSerializer
from .serializers import RepositoryTranslatedExampleSerializer
from .serializers import RepositoryTranslatedExampleEntitySeralizer
from .serializers import RegisterUserSerializer
from .serializers import UserSerializer
from .serializers import ChangePasswordSerializer
from .serializers import RequestResetPasswordSerializer
from .serializers import ResetPasswordSerializer
from .serializers import LoginSerializer
from .serializers import RepositoryCategorySerializer
from .serializers import NewRepositoryExampleSerializer
from .serializers import AnalyzeTextSerializer
from .serializers import EditRepositorySerializer
from .serializers import NewRepositoryTranslatedExampleSerializer


# Permisions

READ_METHODS = permissions.SAFE_METHODS
WRITE_METHODS = ['POST', 'PUT', 'PATCH']
ADMIN_METHODS = ['DELETE']


class RepositoryPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.get_user_authorization(request.user)
        if request.method in READ_METHODS:
            return authorization.can_read
        if request.user.is_authenticated:
            if request.method in WRITE_METHODS:
                return authorization.can_write
            return authorization.is_admin
        return False  # pragma: no cover


class RepositoryExamplePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.repository_update.repository \
            .get_user_authorization(request.user)
        if request.method in READ_METHODS:
            return authorization.can_read
        return authorization.can_contribute


class RepositoryTranslatedExamplePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        repository = obj.original_example.repository_update.repository
        authorization = repository.get_user_authorization(request.user)
        if request.method in READ_METHODS:
            return authorization.can_read
        return authorization.can_contribute


class RepositoryTranslatedExampleEntityPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        repository = obj.repository_translated_example.original_example \
            .repository_update.repository
        authorization = repository.get_user_authorization(request.user)
        if request.method in READ_METHODS:
            return authorization.can_read
        return authorization.can_contribute


# Filters

class ExamplesFilter(filters.FilterSet):
    class Meta:
        model = RepositoryExample
        fields = [
            'text',
            'language',
        ]

    repository_uuid = filters.CharFilter(
        name='repository_uuid',
        method='filter_repository_uuid',
        required=True,
        help_text=_('Repository\'s UUID'))
    language = filters.CharFilter(
        name='language',
        method='filter_language',
        help_text='Filter by language, default is repository base language')
    has_translation = filters.BooleanFilter(
        name='has_translation',
        method='filter_has_translation',
        help_text=_('Filter for examples with or without translation'))
    has_not_translation_to = filters.CharFilter(
        name='has_not_translation_to',
        method='filter_has_not_translation_to')
    order_by_translation = filters.CharFilter(
        name='order_by_translation',
        method='filter_order_by_translation',
        help_text=_('Order examples with translation by language'))

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)
            if not authorization.can_read:
                raise PermissionDenied()
            return repository.examples(queryset=queryset)
        except Repository.DoesNotExist:
            raise NotFound(
                _('Repository {} does not exist').format(value))
        except DjangoValidationError:
            raise NotFound(_('Invalid repository_uuid'))

    def filter_language(self, queryset, name, value):
        return queryset.filter(repository_update__language=value)

    def filter_has_translation(self, queryset, name, value):
        annotated_queryset = queryset.annotate(
            translation_count=Count('translations'))
        if value:
            return annotated_queryset.filter(
                translation_count__gt=0)
        else:
            return annotated_queryset.filter(
                translation_count=0)

    def filter_has_not_translation_to(self, queryset, name, value):
        annotated_queryset = queryset.annotate(
            translation_count=Count(
                'translations',
                filter=Q(translations__language=value)))
        return annotated_queryset.filter(translation_count=0)

    def filter_order_by_translation(self, queryset, name, value):
        inverted = value[0] == '-'
        language = value[1:] if inverted else value
        result_queryset = queryset.annotate(
            translation_count=Count(
                'translations',
                filter=Q(translations__language=language)))
        result_queryset = result_queryset.order_by(
            '-translation_count' if inverted else 'translation_count')
        return result_queryset


class RepositoriesFilter(filters.FilterSet):
    class Meta:
        model = Repository
        fields = [
            'categories',
        ]


class TranslationsFilter(filters.FilterSet):
    class Meta:
        model = RepositoryTranslatedExample
        fields = []

    repository_uuid = filters.CharFilter(
        name='repository_uuid',
        method='filter_repository_uuid',
        required=True,
        help_text=_('Repository\'s UUID'))
    from_language = filters.CharFilter(
        name='language',
        method='filter_from_language',
        help_text='Filter by original language')
    to_language = filters.CharFilter(
        name='language',
        method='filter_to_language',
        help_text='Filter by translated language')

    def filter_repository_uuid(self, queryset, name, value):
        request = self.request
        try:
            repository = Repository.objects.get(uuid=value)
            authorization = repository.get_user_authorization(request.user)
            if not authorization.can_read:
                raise PermissionDenied()
            return RepositoryTranslatedExample.objects.filter(
                original_example__repository_update__repository=repository)
        except Repository.DoesNotExist:
            raise NotFound(
                _('Repository {} does not exist').format(value))
        except DjangoValidationError:
            raise NotFound(_('Invalid repository_uuid'))

    def filter_from_language(self, queryset, name, value):
        return queryset.filter(
            original_example__repository_update__language=value)

    def filter_to_language(self, queryset, name, value):
        return queryset.filter(language=value)


# Mixins

class MultipleFieldLookupMixin(object):
    """
    Apply this mixin to any view or viewset to get multiple field filtering
    based on a `lookup_fields` attribute, instead of the default single field
    filtering.
    """

    def get_object(self):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        filter = {}
        for field in self.lookup_fields:
            if self.kwargs.get(field):
                filter[field] = self.kwargs[field]
        obj = get_object_or_404(queryset, **filter)
        self.check_object_permissions(self.request, obj)
        return obj


# ViewSets

class NewRepositoryViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    """
    Create a new Repository, add examples and train a bot.
    """
    queryset = Repository.objects
    serializer_class = NewRepositorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            RepositorySerializer(instance).data,
            status=status.HTTP_201_CREATED,
            headers=headers)


class MyRepositoriesViewSet(
        mixins.ListModelMixin,
        GenericViewSet):
    """
    List all user's repositories
    """
    queryset = Repository.objects
    serializer_class = RepositorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(owner=self.request.user)


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

    @detail_route(
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

    @detail_route(
        methods=['GET'],
        url_name='repository-authorization')
    def authorization(self, request, **kwargs):
        """
        Get authorization to use in Bothub Natural Language Processing service.
        In Bothub NLP you can train the repository's bot and get interpreted
        messages.
        """
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        serializer = RepositoryAuthorizationSerializer(user_authorization)
        return Response(serializer.data)

    @detail_route(
        methods=['GET'],
        url_name='repository-train')
    def train(self, request, **kwargs):
        """
        Train current update using Bothub NLP service
        """
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        if not user_authorization.can_write:
            raise PermissionDenied()
        request = Repository.request_nlp_train(  # pragma: no cover
            user_authorization)
        if request.status_code != status.HTTP_200_OK:  # pragma: no cover
            raise APIException(  # pragma: no cover
                {'status_code': request.status_code},
                code=request.status_code)
        return Response(request.json())  # pragma: no cover

    @detail_route(
        methods=['POST'],
        url_name='repository-analyze')
    def analyze(self, request, **kwargs):
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        serializer = AnalyzeTextSerializer(
            data=request.data)  # pragma: no cover
        serializer.is_valid(raise_exception=True)  # pragma: no cover
        request = Repository.request_nlp_analyze(
            user_authorization,
            serializer.data)  # pragma: no cover
        if request.status_code != status.HTTP_200_OK:  # pragma: no cover
            response = None  # pragma: no cover
            try:
                response = request.json()  # pragma: no cover
            except Exception:
                pass
            raise APIException(  # pragma: no cover
                {
                    'status_code': request.status_code,
                    'response': response,
                },
                code=request.status_code)
        return Response(request.json())  # pragma: no cover

    def get_serializer_class(self):
        if self.request and self.request.method in \
           ['OPTIONS'] + WRITE_METHODS or not self.request:
                return self.edit_serializer_class
        return self.serializer_class


class NewRepositoryExampleViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    """
    Create new repository example.
    """
    queryset = RepositoryExample.objects
    serializer_class = NewRepositoryExampleSerializer
    permission_classes = [permissions.IsAuthenticated]


class RepositoryExampleViewSet(
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    """
    Manager repository example.

    retrieve:
    Get repository example data.

    delete:
    Delete repository example.
    """
    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        RepositoryExamplePermission,
    ]

    def perform_destroy(self, obj):
        if obj.deleted_in:
            raise APIException(_('Example already deleted'))
        obj.delete()


class NewRepositoryTranslatedExampleViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    """
    Translate example
    """
    queryset = RepositoryTranslatedExample.objects
    serializer_class = NewRepositoryTranslatedExampleSerializer
    permission_classes = [permissions.IsAuthenticated]


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
        permissions.IsAuthenticated,
        RepositoryTranslatedExamplePermission,
    ]


class NewRepositoryTranslatedExampleEntityViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    """
    Add entity to example translation
    """
    queryset = RepositoryTranslatedExampleEntity.objects
    serializer_class = RepositoryTranslatedExampleEntitySeralizer
    permission_classes = [permissions.IsAuthenticated]


class RepositoryTranslatedExampleEntityViewSet(
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    """
    Manage translation entity

    retrieve:
    Get translation entity data.

    delete:
    Delete translation entity.
    """
    queryset = RepositoryTranslatedExampleEntity.objects
    serializer_class = RepositoryTranslatedExampleEntitySeralizer
    permission_classes = [
        permissions.IsAuthenticated,
        RepositoryTranslatedExampleEntityPermission,
    ]


class RepositoryExamplesViewSet(
        mixins.ListModelMixin,
        GenericViewSet):
    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    filter_class = ExamplesFilter
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    ordering_fields = [
        'created_at',
    ]
    permission_classes = [
        RepositoryExamplePermission,
    ]


class RegisterUserViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    """
    Register new user
    """
    queryset = User.objects
    serializer_class = RegisterUserSerializer


class LoginViewSet(GenericViewSet):
    queryset = User.objects
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                'token': token.key,
            },
            status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class ChangePasswordViewSet(GenericViewSet):
    """
    Change current user password.
    """
    serializer_class = ChangePasswordSerializer
    queryset = User.objects
    lookup_field = None
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_object(self, *args, **kwargs):
        request = self.request
        user = request.user

        # May raise a permission denied
        self.check_object_permissions(self.request, user)

        return user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.object.set_password(serializer.data.get('password'))
            self.object.save()
            return Response({}, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class RequestResetPassword(GenericViewSet):
    """
    Request reset password
    """
    serializer_class = RequestResetPasswordSerializer
    queryset = User.objects

    def get_object(self):
        return self.queryset.get(email=self.request.data.get('email'))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.object = self.get_object()
            self.object.send_reset_password_email()
            return Response({})
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(GenericViewSet):
    """
    Reset password
    """
    serializer_class = ResetPasswordSerializer
    queryset = User.objects
    lookup_field = 'nickname'

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.object.set_password(serializer.data.get('password'))
            self.object.save()
            return Response({})
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class MyUserProfileViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        GenericViewSet):
    """
    Manager current user profile.

    retrieve:
    Get current user profile

    update:
    Update current user profile.

    partial_update:
    Update, partially, current user profile.
    """
    serializer_class = UserSerializer
    queryset = User.objects
    lookup_field = None
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_object(self, *args, **kwargs):
        request = self.request
        user = request.user

        # May raise a permission denied
        self.check_object_permissions(self.request, user)

        return user


class UserProfileViewSet(
        mixins.RetrieveModelMixin,
        GenericViewSet):
    """
    Get user profile
    """
    serializer_class = UserSerializer
    queryset = User.objects
    lookup_field = 'nickname'


class Categories(
        mixins.ListModelMixin,
        GenericViewSet):
    """
    List all categories.
    """
    serializer_class = RepositoryCategorySerializer
    queryset = RepositoryCategory.objects.all()
    pagination_class = None


class RepositoriesViewSet(
        mixins.ListModelMixin,
        GenericViewSet):
    """
    List all public repositories.
    """
    serializer_class = RepositorySerializer
    queryset = Repository.objects.filter(is_private=False)
    filter_class = RepositoriesFilter


class TranslationsViewSet(
        mixins.ListModelMixin,
        GenericViewSet):
    """
    List repository translations.
    """
    serializer_class = RepositoryTranslatedExampleSerializer
    queryset = RepositoryTranslatedExample.objects.all()
    filter_class = TranslationsFilter
