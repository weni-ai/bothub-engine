from django_grpc_framework import mixins
from django_grpc_framework import generics

from .serializers import RepositoryProtoSerializer
from bothub.common.models import Repository


class RepositoryService(mixins.ListModelMixin, generics.GenericService):
    queryset = Repository.objects.all()
    serializer_class = RepositoryProtoSerializer

    def filter_queryset(self, queryset):
        org_id = self.request.org_id

        queryset = queryset.filter(name__icontains=self.request.name)

        if org_id:
            queryset = queryset.filter(authorizations__user__pk=org_id)

        return queryset
