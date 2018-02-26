from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from .serializers import RepositorySerializer
from .serializers import CurrentRepositoryUpdateSerializer
from bothub.common.models import Repository


# Permisions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


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
