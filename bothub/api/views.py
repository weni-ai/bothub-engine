from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError as DjangoValidationError

from .serializers import RepositorySerializer
from .serializers import CurrentRepositoryUpdateSerializer
from .serializers import RepositoryExampleSerializer
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample


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


# ViewSets

class NewRepositoryViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet):
    queryset = Repository.objects
    serializer_class = RepositorySerializer
    permission_classes = [permissions.IsAuthenticated]

class MyRepositoriesViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet):
    queryset = Repository.objects
    serializer_class = RepositorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        return self.queryset.filter(owner=self.request.user)

class RepositoryViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet):
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

class NewRepositoryExampleViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet):
    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsRepositoryUUIDOwner,
    ]

class RepositoryExampleViewSet(
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet):
    queryset = RepositoryExample.objects
    serializer_class = RepositoryExampleSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsRepositoryUpdateOwner,
    ]
