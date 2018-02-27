from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework import permissions
from rest_framework.decorators import detail_route
from rest_framework.decorators import list_route
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.exceptions import NotFound
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError as DjangoValidationError

from .serializers import RepositorySerializer
from .serializers import CurrentRepositoryUpdateSerializer
from .serializers import RepositoryExampleSerializer
from .serializers import RepositoryExampleEntitySerializer
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity


# Permisions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsRepositoryUUIDOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        repository_uuid = request.POST.get('repository_uuid')

        if not repository_uuid:
            raise APIException(_('repository_uuid is required'))
        
        try:
            repository = Repository.objects.get(uuid=repository_uuid)
        except Repository.DoesNotExist:
            raise NotFound(_('Repository {} does not exist').format(repository_uuid))
        except DjangoValidationError:
            raise APIException(_('Invalid repository_uuid'))
        
        return repository.owner == request.user

class IsRepositoryUpdateOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.repository_update.repository.owner == request.user

class IsRepositoryExampleOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.repository_example.repository_update.repository.owner == request.user


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
        methods=['GET'],
        url_name='repository-current-update')
    def currentupdate(self, request, **kwargs):
        instance = self.get_object()
        serializer = CurrentRepositoryUpdateSerializer(instance.current_update)
        return Response(dict(serializer.data))
    
    @detail_route(
        methods=['GET'],
        url_name='repository-examples')
    def examples(self, request, **kwargs):
        repository = self.get_object()
        examples = RepositoryExample.objects.filter(
            repository_update__repository=repository,
            deleted_in__isnull=True)
        
        page = self.paginate_queryset(examples)
        if page is not None:
            serializer = RepositoryExampleSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = RepositoryExampleSerializer(examples, many=True)
        return Response(serializer.data)

class NewRepositoryExampleViewSet(
    mixins.CreateModelMixin,
    GenericViewSet):
    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsRepositoryUUIDOwner,
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
        obj.deleted_in = obj.repository_update.repository.current_update
        obj.save(update_fields=['deleted_in'])

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
