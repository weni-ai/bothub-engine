from rest_framework import permissions


class ModuleHasPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):  # pragma: no cover
        return request.user.has_perm("can_communicate_internally")
