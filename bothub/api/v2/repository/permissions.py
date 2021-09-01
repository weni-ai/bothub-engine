from rest_framework import permissions

from bothub.common.models import QAtext, RepositoryVersionLanguage
from .. import READ_METHODS
from .. import WRITE_METHODS


class RepositoryLogPermission(permissions.BasePermission):
    def has_object_permission(self, request, view):
        value = self.request.query_params.get("repository_version_language", None)
        obj = RepositoryVersionLanguage.objects.get(
            pk=value
        ).repository_version.repository
        authorization = obj.get_user_authorization(request.user)
        if request.method in READ_METHODS and not request.user.is_authenticated:
            return authorization.can_read

        if request.user.is_authenticated:
            if request.method in READ_METHODS:
                return authorization.can_read
            if request.method in WRITE_METHODS:
                return authorization.can_write
            return authorization.is_admin
        return False


class RepositoryQALogPermission(permissions.BasePermission):
    def has_object_permission(self, request, view):
        value = self.request.query_params.get("context", None)
        obj = QAtext.objects.get(
            pk=value
        ).repository
        authorization = obj.get_user_authorization(request.user)
        if request.method in READ_METHODS and not request.user.is_authenticated:
            return authorization.can_read

        if request.user.is_authenticated:
            if request.method in READ_METHODS:
                return authorization.can_read
            if request.method in WRITE_METHODS:
                return authorization.can_write
            return authorization.is_admin
        return False


class RepositoryPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.get_user_authorization(request.user)
        if request.method in READ_METHODS and not request.user.is_authenticated:
            return authorization.can_read

        if request.user.is_authenticated:
            if request.method in READ_METHODS:
                return authorization.can_read
            if request.method in WRITE_METHODS:
                return authorization.can_write
            return authorization.is_admin
        return False


class RepositoryInfoPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.repository.get_user_authorization(request.user)
        if request.method in READ_METHODS and not request.user.is_authenticated:
            return authorization.can_read

        if request.user.is_authenticated:
            if request.method in READ_METHODS:
                return authorization.can_read
            if request.method in WRITE_METHODS:
                return authorization.can_write
            return authorization.is_admin
        return False


class RepositoryTrainInfoPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.repository_version.repository.get_user_authorization(
            request.user
        )
        if request.method in READ_METHODS and not request.user.is_authenticated:
            return authorization.can_read

        if request.user.is_authenticated:
            if request.method in READ_METHODS:
                return authorization.can_read
            if request.method in WRITE_METHODS:
                return authorization.can_write
            return authorization.is_admin
        return False


class RepositoryMigratePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.repository_version.repository.get_user_authorization(
            request.user
        )
        if request.method in READ_METHODS and not request.user.is_authenticated:
            return authorization.can_read

        if request.user.is_authenticated:
            if request.method in READ_METHODS:
                return authorization.can_read
            if request.method in WRITE_METHODS:
                return authorization.can_write
            return authorization.is_admin
        return False


class RepositoryAdminManagerAuthorization(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.repository.get_user_authorization(request.user)
        return authorization.is_admin


class RepositoryExamplePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.repository_version_language.repository_version.repository.get_user_authorization(
            request.user
        )
        if request.method in READ_METHODS:
            return authorization.can_read
        return authorization.can_contribute


class RepositoryEntityHasPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
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


class RepositoryIntentPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.repository_version.repository.get_user_authorization(
            request.user
        )
        if request.method in READ_METHODS:
            return authorization.can_read
        return authorization.can_contribute
