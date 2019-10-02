from rest_framework import permissions

from bothub.api.v2 import READ_METHODS
from bothub.api.v2 import WRITE_METHODS
from bothub.api.v2 import EDIT_METHODS
from bothub.api.v2 import DELETE_METHODS
from bothub.common.models import UserPermissionRepository


class RepositoryTranslatedExamplePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        repository = obj.original_example.repository_update.repository
        authorization = repository.get_user_authorization(request.user)
        usergrouprepository = authorization.usergrouprepository
        permission = UserPermissionRepository.objects.filter(
            usergrouprepository=usergrouprepository
        )

        if request.user.is_authenticated:
            if request.method in READ_METHODS:
                return permission.filter(
                    codename='view.repositorytranslatedexample'
                ).exists()
            if request.method in WRITE_METHODS:
                return permission.filter(
                    codename='write.repositorytranslatedexample'
                ).exists()
            if request.method in EDIT_METHODS:
                return permission.filter(
                    codename='edit.repositorytranslatedexample'
                ).exists()
            if request.method in DELETE_METHODS:
                return permission.filter(
                    codename='delete.repositorytranslatedexample'
                ).exists()
        return False
