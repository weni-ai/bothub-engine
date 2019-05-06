from rest_framework import permissions

from .. import READ_METHODS
from .. import WRITE_METHODS


class RepositoryEvaluatePermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        authorization = obj.repository_update. \
            repository.get_user_authorization(request.user)
        if request.method in READ_METHODS:
            return authorization.can_read
        if request.user.is_authenticated:
            if request.method in WRITE_METHODS:
                return authorization.can_write
            return authorization.is_admin
        return False


class RepositoryEvaluateResultPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        authorization = obj.repository_update. \
            repository.get_user_authorization(request.user)

        if request.method in READ_METHODS:
            return authorization.can_read
        return authorization.can_contribute
