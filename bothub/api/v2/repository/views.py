from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, \
    IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from bothub.common.models import Repository, RepositoryVote

from ..metadata import Metadata
from .serializers import RepositorySerializer, RepositoryVotesSerializer
from .serializers import ShortRepositorySerializer
from .permissions import RepositoryPermission
from .filters import RepositoriesFilter


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
    lookup_fields = ['user', 'repository']
    serializer_class = RepositoryVotesSerializer
    permission_classes = [
        IsAuthenticated
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
