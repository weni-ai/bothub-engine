from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bothub.common.models import Repository

from bothub.api.v2.internal.repository.serializers import InternalRepositorySerializer
from bothub.api.v2.internal.permissions import ModuleHasPermission


class InternalRepositoriesViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = InternalRepositorySerializer
    queryset = Repository.objects
    permission_classes = [ModuleHasPermission]
    filter_backends = [SearchFilter]
    search_fields = ["$name", "^name", "=name"]

    def get_queryset(self, *args, **kwargs):
        queryset = self.queryset.all()
        name = self.request.query_params.get("name", None)
        if name:
            queryset = self.queryset.filter(name__icontains=name)
        org_id = self.request.query_params.get("org_id", None)
        if org_id:
            queryset = queryset.filter(authorizations__user__pk=org_id)

        return queryset[:20]

    @action(detail=True, methods=["GET"], url_name="retrieve-authorization")
    def retrieve_authorization(self, request, **kwargs):
        auth = self.request.query_params.get("repository_authorization", None)
        repository = Repository.objects.none()
        if auth:
            repository = Repository.objects.get(authorizations__uuid=auth)
        serialized_data = InternalRepositorySerializer(repository)

        return Response(serialized_data.data)
