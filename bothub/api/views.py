from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions

from .serializers import RepositorySerializer
from bothub.common.models import Repository


# Permisions

class IsRepositoryOwner(permissions.BasePermission):
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
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet):
    queryset = Repository.objects
    serializer_class = RepositorySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsRepositoryOwner,
    ]
