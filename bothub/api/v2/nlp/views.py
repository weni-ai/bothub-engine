from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny

from bothub.common.models import RepositoryAuthorization


class RepositoryAuthorizationNLPViewSet(
        mixins.RetrieveModelMixin,
        GenericViewSet):
    queryset = RepositoryAuthorization.objects
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        repository_authorization = self.get_object()
        current_update = repository_authorization.repository.current_update(
            str(request.query_params.get('language'))
        )

        data = {
            'ready_for_train':
                current_update.ready_for_train,
            'current_update_id':
                current_update.id,
            'repository_authorization_user_id':
                repository_authorization.user.id,
            'language':
                current_update.language
        }
        return Response(data)
