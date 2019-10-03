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

        if request.method in READ_METHODS and not request.user.is_authenticated:
            return True

        if request.user.is_authenticated:
            if request.method in READ_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="view.repository"
                    ).first()
                ).exists()
            if request.method in WRITE_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="write.repository"
                    ).first()
                ).exists()
            if request.method in EDIT_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="write.repository"
                    ).first()
                ).exists()
            if request.method in DELETE_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="delete.repository"
                    ).first()
                ).exists()
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
                    codename=PermissionsCode.objects.filter(
                        codename="view.repositoryadminmanager"
                    ).first()
                ).exists()
            if request.method in WRITE_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="write.repositoryadminmanager"
                    ).first()
                ).exists()
            if request.method in EDIT_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="edit.repositoryadminmanager"
                    ).first()
                ).exists()
            if request.method in DELETE_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="delete.repositoryadminmanager"
                    ).first()
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
                    codename=PermissionsCode.objects.filter(
                        codename="view.repositoryupdate"
                    ).first()
                ).exists()
            if request.method in WRITE_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="write.repositoryupdate"
                    ).first()
                ).exists()
            if request.method in EDIT_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="edit.repositoryupdate"
                    ).first()
                ).exists()
            if request.method in DELETE_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="delete.repositoryupdate"
                    ).first()
                ).exists()
        return False


class RepositoryAnalyzePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.get_user_authorization(request.user)
        usergrouprepository = authorization.usergrouprepository
        permission = UserPermissionRepository.objects.filter(
            usergrouprepository=usergrouprepository
        )

        if request.user.is_authenticated:
            if request.method in WRITE_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="write.repository_analyze"
                    ).first()
                ).exists()
        return False


class RepositoryTrainPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.get_user_authorization(request.user)
        usergrouprepository = authorization.usergrouprepository
        permission = UserPermissionRepository.objects.filter(
            usergrouprepository=usergrouprepository
        )

        if request.user.is_authenticated:
            if request.method in READ_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="view.repository_train"
                    ).first()
                ).exists()
        return False


class RepositoryEvaluatePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.get_user_authorization(request.user)
        usergrouprepository = authorization.usergrouprepository
        permission = UserPermissionRepository.objects.filter(
            usergrouprepository=usergrouprepository
        )

        if request.user.is_authenticated:
            if request.method in WRITE_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="write.repository_evaluate"
                    ).first()
                ).exists()
        return False
