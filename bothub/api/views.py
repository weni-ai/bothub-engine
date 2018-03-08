from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework import permissions
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count
from django_filters import rest_framework as filters

from .serializers import RepositorySerializer
from .serializers import CurrentRepositoryUpdateSerializer
from .serializers import RepositoryExampleSerializer
from .serializers import RepositoryExampleEntitySerializer
from .serializers import RepositoryAuthorizationSerializer
from .serializers import RepositoryTranslatedExampleSerializer
from .serializers import RepositoryTranslatedExampleEntitySeralizer
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryTranslatedExampleEntity


# Utils

def get_repository_from_uuid(repository_uuid):
    if not repository_uuid:
        raise ValidationError(_('repository_uuid is required'), code=400)

    try:
        return Repository.objects.get(uuid=repository_uuid)
    except Repository.DoesNotExist:
        raise NotFound(
            _('Repository {} does not exist').format(repository_uuid))
    except DjangoValidationError:
        raise ValidationError(_('Invalid repository_uuid'))


# Permisions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsRepositoryUpdateOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.repository_update.repository.owner == request.user


class IsRepositoryExampleOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        repository = obj.repository_example.repository_update.repository
        return repository.owner == request.user


class IsOriginalRepositoryExampleOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        repository = obj.original_example.repository_update.repository
        return repository.owner == request.user


class IsTranslatedExampleOriginalRepositoryExampleOwner(
        permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        repository = obj.repository_translated_example.original_example \
            .repository_update.repository
        return repository.owner == request.user


# Filters

class ExamplesFilter(filters.FilterSet):
    class Meta:
        model = RepositoryExample
        fields = [
            'text',
            'language',
        ]

    language = filters.CharFilter(
        name='language',
        method='filter_language')
    has_translation = filters.BooleanFilter(
        name='has_translation',
        method='filter_has_translation')

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


# ViewSets

class NewRepositoryViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    queryset = Repository.objects
    serializer_class = RepositorySerializer
    permission_classes = [permissions.IsAuthenticated]


class MyRepositoriesViewSet(
        mixins.ListModelMixin,
        GenericViewSet):
    queryset = Repository.objects
    serializer_class = RepositorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(owner=self.request.user)


class RepositoryViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    queryset = Repository.objects
    serializer_class = RepositorySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwner,
    ]

    @detail_route(
        methods=['POST'],
        url_name='repository-current-update')
    def currentupdate(self, request, **kwargs):
        instance = self.get_object()
        language = request.POST.get('language')

        if not language:
            raise APIException(_('language is required'))

        serializer = CurrentRepositoryUpdateSerializer(
            instance.current_update(language))

        return Response(dict(serializer.data))

    @detail_route(
        methods=['POST'],
        url_name='repository-current-rasa-nlu-data')
    def currentrasanludata(self, request, **kwargs):
        repository = self.get_object()

        language = request.POST.get('language')
        if not language:
            raise APIException(_('language is required'))

        return Response(repository.current_rasa_nlu_data(language))

    @detail_route(
        methods=['GET'],
        url_name='languages-status')
    def languagesstatus(self, request, **kwargs):
        repository = self.get_object()
        return Response({
            'languages_status': repository.languages_status,
        })


class RepositoryAuthorizationView(GenericViewSet):
    serializer_class = RepositoryAuthorizationSerializer
    queryset = RepositoryAuthorization.objects
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, **kwargs):
        repository_uuid = request.POST.get('repository_uuid')
        repository = get_repository_from_uuid(repository_uuid)
        user_authorization = repository.get_user_authorization(request.user)

        if not user_authorization:
            raise PermissionDenied(
                _('User don\'t have authorization for this repository'))

        serializer = self.get_serializer(user_authorization)
        return Response(serializer.data)


class NewRepositoryExampleViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsRepositoryUpdateOwner,
    ]


class RepositoryExampleViewSet(
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsRepositoryUpdateOwner,
    ]

    def perform_destroy(self, obj):
        if obj.deleted_in:
            raise APIException(_('Example already deleted'))
        obj.delete()


class NewRepositoryExampleEntityViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    queryset = RepositoryExampleEntity.objects
    serializer_class = RepositoryExampleEntitySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsRepositoryExampleOwner,
    ]


class RepositoryExampleEntityViewSet(
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    queryset = RepositoryExampleEntity.objects
    serializer_class = RepositoryExampleEntitySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsRepositoryExampleOwner,
    ]


class NewRepositoryTranslatedExampleViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    queryset = RepositoryTranslatedExample.objects
    serializer_class = RepositoryTranslatedExampleSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOriginalRepositoryExampleOwner,
    ]


class RepositoryTranslatedExampleViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    queryset = RepositoryTranslatedExample.objects
    serializer_class = RepositoryTranslatedExampleSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOriginalRepositoryExampleOwner,
    ]


class NewRepositoryTranslatedExampleEntityViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    queryset = RepositoryTranslatedExampleEntity.objects
    serializer_class = RepositoryTranslatedExampleEntitySeralizer
    permission_classes = [
        permissions.IsAuthenticated,
        IsTranslatedExampleOriginalRepositoryExampleOwner,
    ]


class RepositoryTranslatedExampleEntityViewSet(
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    queryset = RepositoryTranslatedExampleEntity.objects
    serializer_class = RepositoryTranslatedExampleEntitySeralizer
    permission_classes = [
        permissions.IsAuthenticated,
        IsTranslatedExampleOriginalRepositoryExampleOwner,
    ]


class RepositoryExamplesViewSet(
        mixins.ListModelMixin,
        GenericViewSet):
    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    filter_class = ExamplesFilter
    permission_classes = [
        permissions.IsAuthenticated,
        IsRepositoryUpdateOwner,
    ]

    def get_queryset(self):
        repository_uuid = self.request.query_params.get('repository_uuid')
        repository = get_repository_from_uuid(repository_uuid)
        return self.queryset.filter(repository_update__repository=repository)
