from rest_framework import permissions

from bothub.common.models import Repository
from .. import READ_METHODS
from .. import WRITE_METHODS


class RepositoryEvaluatePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            repository = Repository.objects.get(uuid=request.GET.get("repository_uuid"))
            authorization = repository.get_user_authorization(request.user)

            if request.method in READ_METHODS and not request.user.is_authenticated:
                return authorization.can_read

            if request.user.is_authenticated:
                if request.method in READ_METHODS:
                    return authorization.can_read
                if request.method in WRITE_METHODS:
                    return authorization.can_write
                return authorization.is_admin
            return False
        except Repository.DoesNotExist:
            return False


class RepositoryEvaluateResultPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            repository = Repository.objects.get(uuid=request.GET.get("repository_uuid"))
            authorization = repository.get_user_authorization(request.user)

            if request.method in READ_METHODS:
                return authorization.can_read
            return authorization.can_contribute
        except Repository.DoesNotExist:
            return False
