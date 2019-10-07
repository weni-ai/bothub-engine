from rest_framework import permissions

from bothub.api.v2 import READ_METHODS
from bothub.api.v2 import WRITE_METHODS
from bothub.api.v2 import EDIT_METHODS
from bothub.api.v2 import DELETE_METHODS
from bothub.common.models import UserPermissionRepository, Repository
from bothub.common.models import PermissionsCode


class RepositoryExamplePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.repository_update.repository.get_user_authorization(
            request.user
        )
        usergrouprepository = authorization.usergrouprepository
        permission = UserPermissionRepository.objects.filter(
            usergrouprepository=usergrouprepository
        )

        if request.user.is_authenticated:
            if request.method in READ_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="view.repositoryexample"
                    ).first()
                ).exists()
            if request.method in WRITE_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="write.repositoryexample"
                    ).first()
                ).exists()
            if request.method in EDIT_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="edit.repositoryexample"
                    ).first()
                ).exists()
            if request.method in DELETE_METHODS:
                return permission.filter(
                    codename=PermissionsCode.objects.filter(
                        codename="delete.repositoryexample"
                    ).first()
                ).exists()
        return False

    def has_permission(self, request, view):
        if request.method != 'GET':
            return super().has_permission(request, view)

        try:
            repository = Repository.objects.get(uuid=request.GET.get("repository_uuid"))
            authorization = repository.get_user_authorization(request.user)

            usergrouprepository = authorization.usergrouprepository
            permission = UserPermissionRepository.objects.filter(
                usergrouprepository=usergrouprepository
            )

            if request.user.is_authenticated:
                if request.method in READ_METHODS:
                    return permission.filter(
                        codename=PermissionsCode.objects.filter(
                            codename="view.repositoryexample"
                        ).first()
                    ).exists()
            return False

        except Repository.DoesNotExist:
            return False
