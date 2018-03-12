from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework import permissions
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count
from django_filters import rest_framework as filters

from .serializers import RepositorySerializer
from .serializers import RepositoryExampleSerializer
from .serializers import RepositoryExampleEntitySerializer
from .serializers import RepositoryAuthorizationSerializer
from .serializers import RepositoryTranslatedExampleSerializer
from .serializers import RepositoryTranslatedExampleEntitySeralizer
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity
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

READ_METHODS = permissions.SAFE_METHODS
WRITE_METHODS = ['POST', 'PUT', 'PATCH']
ADMIN_METHODS = ['DELETE']


class RepositoryPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.get_user_authorization(request.user)
        if request.method in READ_METHODS:
            return authorization.can_read
        if request.method in WRITE_METHODS:
            return authorization.can_write
        return authorization.is_admin


class RepositoryExamplePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.repository_update.repository \
            .get_user_authorization(request.user)
        if request.method in READ_METHODS:
            return authorization.can_read
        return authorization.is_admin


class RepositoryExampleEntityPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.repository_example.repository_update.repository \
            .get_user_authorization(request.user)
        if request.method in READ_METHODS:
            return authorization.can_read
        return authorization.is_admin


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
        RepositoryPermission,
    ]

    @detail_route(
        methods=['GET'],
        url_name='repository-languages-status')
    def languagesstatus(self, request, **kwargs):
        repository = self.get_object()
        return Response({
            'languages_status': repository.languages_status,
        })

    @detail_route(
        methods=['GET'],
        url_name='repository-authorization')
    def authorization(self, request, **kwargs):
        repository = self.get_object()
        user_authorization = repository.get_user_authorization(request.user)
        serializer = RepositoryAuthorizationSerializer(user_authorization)
        return Response(serializer.data)


class NewRepositoryExampleViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    permission_classes = [permissions.IsAuthenticated]


class RepositoryExampleViewSet(
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
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


class NewRepositoryExampleEntityViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    queryset = RepositoryExampleEntity.objects
    serializer_class = RepositoryExampleEntitySerializer
    permission_classes = [permissions.IsAuthenticated]


class RepositoryExampleEntityViewSet(
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    queryset = RepositoryExampleEntity.objects
    serializer_class = RepositoryExampleEntitySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        RepositoryExampleEntityPermission,
    ]


class NewRepositoryTranslatedExampleViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    queryset = RepositoryTranslatedExample.objects
    serializer_class = RepositoryTranslatedExampleSerializer
    permission_classes = [permissions.IsAuthenticated]


class RepositoryTranslatedExampleViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    queryset = RepositoryTranslatedExample.objects
    serializer_class = RepositoryTranslatedExampleSerializer
    permission_classes = [permissions.IsAuthenticated]


class NewRepositoryTranslatedExampleEntityViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):
    queryset = RepositoryTranslatedExampleEntity.objects
    serializer_class = RepositoryTranslatedExampleEntitySeralizer
    permission_classes = [permissions.IsAuthenticated]


class RepositoryTranslatedExampleEntityViewSet(
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    queryset = RepositoryTranslatedExampleEntity.objects
    serializer_class = RepositoryTranslatedExampleEntitySeralizer
    permission_classes = [permissions.IsAuthenticated]


class RepositoryExamplesViewSet(
        mixins.ListModelMixin,
        GenericViewSet):
    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    filter_class = ExamplesFilter
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_queryset(self):
        repository_uuid = self.request.query_params.get('repository_uuid')
        repository = get_repository_from_uuid(repository_uuid)
        return self.queryset.filter(repository_update__repository=repository)
