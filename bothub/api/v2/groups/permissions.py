from rest_framework import permissions

from .. import READ_METHODS, WRITE_METHODS


class RepositoryEntityGroupHasPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):  # pragma: no cover
        authorization = obj.repository_version.repository.get_user_authorization(
            request.user
        )
        if request.method in READ_METHODS:
            return authorization.can_read
        if request.user.is_authenticated:
            if request.method in WRITE_METHODS:
                return authorization.can_write
            return authorization.is_admin
        return False
