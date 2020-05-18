from rest_framework import permissions

from bothub.api.v2 import READ_METHODS


class RepositoryTranslatedExamplePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        repository = (
            obj.original_example.repository_version_language.repository_version.repository
        )
        authorization = repository.get_user_authorization(request.user)
        if request.method in READ_METHODS:
            return authorization.can_read
        return authorization.can_translate


class RepositoryTranslatedExampleExporterPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.repository.get_user_authorization(request.user)
        return authorization.can_translate
