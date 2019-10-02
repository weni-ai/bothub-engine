from rest_framework import permissions

from bothub.common.models import Repository, UserPermissionRepository, PermissionsCode
from .. import READ_METHODS, EDIT_METHODS, DELETE_METHODS
from .. import WRITE_METHODS


class RepositoryEvaluatePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        try:
            repository = Repository.objects.get(
                uuid=request.GET.get('repository_uuid')
            )
            authorization = repository.get_user_authorization(request.user)

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
                        codename='view.repositoryevaluate'
                    ).exists()
                if request.method in WRITE_METHODS:
                    return permission.filter(
                        codename='write.repositoryevaluate'
                    ).exists()
                if request.method in EDIT_METHODS:
                    return permission.filter(
                        codename='edit.repositoryevaluate'
                    ).exists()
                if request.method in DELETE_METHODS:
                    return permission.filter(
                        codename=PermissionsCode.objects.filter(
                            codename='delete.repositoryevaluate'
                        ).first()
                    ).exists()
            return False

        except Repository.DoesNotExist:
            return False


class RepositoryEvaluateResultPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        try:
            repository = Repository.objects.get(
                uuid=request.GET.get('repository_uuid')
            )
            authorization = repository.get_user_authorization(request.user)
            usergrouprepository = authorization.usergrouprepository
            permission = UserPermissionRepository.objects.filter(
                usergrouprepository=usergrouprepository
            )

            if request.user.is_authenticated:
                if request.method in READ_METHODS:
                    return permission.filter(
                        codename='view.repositoryevaluateresult'
                    ).exists()
                if request.method in WRITE_METHODS:
                    return permission.filter(
                        codename='write.repositoryevaluateresult'
                    ).exists()
                if request.method in EDIT_METHODS:
                    return permission.filter(
                        codename='edit.repositoryevaluateresult'
                    ).exists()
                if request.method in DELETE_METHODS:
                    return permission.filter(
                        codename='delete.repositoryevaluateresult'
                    ).exists()
            return False

        except Repository.DoesNotExist:
            return False
