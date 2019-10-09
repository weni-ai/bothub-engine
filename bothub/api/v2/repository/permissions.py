from rest_framework import permissions
from rest_framework import serializers

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

        if (
            request.user.is_authenticated
            and obj.is_private
            and usergrouprepository.name == "Public"
        ):
            return False

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


class RepositoryAuthorizationPermission(permissions.BasePermission):
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
                        codename="view.repository_authorization"
                    ).first()
                ).exists()
            if request.method in EDIT_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="edit.repository_authorization"
                    ).first()
                ).exists()
        return False


class RepositoryeUploadExamplePermission(permissions.BasePermission):
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
                        codename="write.repositoryuploadexamples"
                    ).first()
                ).exists()
        return False


class RepositoryAuthorizationRequestsPermission(permissions.BasePermission):
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
                        codename="write.repositoryauthorizationrequests"
                    ).first()
                ).exists()
            if request.method in READ_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="view.repositoryauthorizationrequests"
                    ).first()
                ).exists()
            if request.method in EDIT_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="edit.repositoryauthorizationrequests"
                    ).first()
                ).exists()
            if request.method in DELETE_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="delete.repositoryauthorizationrequests"
                    ).first()
                ).exists()
        return False


class RepositoryGroupPermissionsPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.user.is_authenticated:
            if request.method in EDIT_METHODS:
                if obj.standard:
                    raise serializers.ValidationError(
                        "Cannot edit the name of a default permission."
                    )
            return True
        return False
