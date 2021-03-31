from django_grpc_framework import mixins
from django_grpc_framework import generics

from .serializers import RepositoryProtoSerializer
from bothub.common.models import Repository


class RepositoryService(mixins.ListModelMixin, generics.GenericService):
    queryset = Repository.objects.all()
    serializer_class = RepositoryProtoSerializer

    def filter_queryset(self, queryset):
        owner_id = self.request.owner_id
        if owner_id:
            queryset = queryset.filter(owner__pk=owner_id)

        return queryset
