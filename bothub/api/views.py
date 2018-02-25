from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from .serializers import RepositorySerializer
from bothub.common.models import Repository

class NewRepositoryViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Repository.objects
    serializer_class = RepositorySerializer
    permission_classes = [IsAuthenticated]
