from rest_framework import permissions

from bothub.common.models import UserPermissionRepository, PermissionsCode
from .. import READ_METHODS
from .. import WRITE_METHODS
from .. import EDIT_METHODS
from .. import DELETE_METHODS


class RepositoryPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.get_user_authorization(request.user)
        usergrouprepository = authorization.usergrouprepository
        permission = UserPermissionRepository.objects.filter(
            usergrouprepository=usergrouprepository
        )

        if request.method in READ_METHODS and \
                not request.user.is_authenticated:
            return True

        if request.user.is_authenticated:
            if request.method in READ_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                            codename='view.repository'
                        ).first()).exists()
            if request.method in WRITE_METHODS:
                return permission.filter(codename='write.repository').exists()
            if request.method in EDIT_METHODS:
                return permission.filter(codename='edit.repository').exists()
            if request.method in DELETE_METHODS:
                return permission.filter(codename='delete.repository').exists()
        return False


class RepositoryAdminManagerAuthorization(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.repository.get_user_authorization(request.user)
        usergrouprepository = authorization.usergrouprepository
        permission = UserPermissionRepository.objects.filter(
            usergrouprepository=usergrouprepository
        )

        if request.user.is_authenticated:
            if request.method in READ_METHODS:
                return permission.filter(
                    codename='view.repositoryadminmanager'
                ).exists()
            if request.method in WRITE_METHODS:
                return permission.filter(
                    codename='write.repositoryadminmanager'
                ).exists()
            if request.method in EDIT_METHODS:
                return permission.filter(
                    codename='edit.repositoryadminmanager'
                ).exists()
            if request.method in DELETE_METHODS:
                return permission.filter(
                    codename='delete.repositoryadminmanager'
                ).exists()
        return False


class RepositoryUpdateHasPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.repository.get_user_authorization(request.user)
        usergrouprepository = authorization.usergrouprepository
        permission = UserPermissionRepository.objects.filter(
            usergrouprepository=usergrouprepository
        )

        if request.user.is_authenticated:
            if request.method in READ_METHODS:
                return permission.filter(
                    codename='view.repositoryupdate'
                ).exists()
            if request.method in WRITE_METHODS:
                return permission.filter(
                    codename='write.repositoryupdate'
                ).exists()
            if request.method in EDIT_METHODS:
                return permission.filter(
                    codename='edit.repositoryupdate'
                ).exists()
            if request.method in DELETE_METHODS:
                return permission.filter(
                    codename='delete.repositoryupdate'
                ).exists()
        return False
