from django_grpc_framework import generics
from django_grpc_framework import mixins

from bothub.common.models import Repository
from .serializers import RepositoryProtoSerializer


class RepositoryService(mixins.ListModelMixin, generics.GenericService):
    queryset = Repository.objects.all()
    serializer_class = RepositoryProtoSerializer

    def filter_queryset(self, queryset):
        org_id = self.request.org_id

        queryset = queryset.filter(name__icontains=self.request.name)

        if org_id:
            queryset = queryset.filter(authorizations__user__pk=org_id)

        return queryset[:20]

    def RetrieveAuthorization(self, request, context):
        repository = Repository.objects.get(
            authorizations__uuid=self.request.repository_authorization
        )

        return RepositoryProtoSerializer(repository).message
