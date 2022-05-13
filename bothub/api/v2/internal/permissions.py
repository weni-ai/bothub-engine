from rest_framework import permissions

from bothub.utils import check_module_keycloak


class ModuleHasPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):  # pragma: no cover
        return check_module_keycloak(request.query_params.get("token", None))
