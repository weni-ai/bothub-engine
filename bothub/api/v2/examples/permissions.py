from rest_framework import permissions

from bothub.api.v2 import READ_METHODS
from bothub.api.v2 import WRITE_METHODS
from bothub.api.v2 import EDIT_METHODS
from bothub.api.v2 import DELETE_METHODS
from bothub.common.models import UserPermissionRepository


class RepositoryExamplePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.repository_update.repository.\
            get_user_authorization(request.user)
        usergrouprepository = authorization.usergrouprepository
        permission = UserPermissionRepository.objects.filter(
            usergrouprepository=usergrouprepository
        )

        if request.user.is_authenticated:
            if request.method in READ_METHODS:
                return permission.filter(
                    codename='view.repositoryexample'
                ).exists()
            if request.method in WRITE_METHODS:
                return permission.filter(
                    codename='write.repositoryexample'
                ).exists()
            if request.method in EDIT_METHODS:
                return permission.filter(
                    codename='edit.repositoryexample'
                ).exists()
            if request.method in DELETE_METHODS:
                return permission.filter(
                    codename='delete.repositoryexample'
                ).exists()
        return False
