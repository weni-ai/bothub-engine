from rest_framework import permissions

from bothub.api.v2 import READ_METHODS, WRITE_METHODS


class OrganizationAdminManagerAuthorization(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.organization.get_organization_authorization(request.user)
        return authorization.is_admin


class OrganizationHasPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.get_organization_authorization(request.user)
        if request.method in READ_METHODS and not request.user.is_authenticated:
            return authorization.can_read

        if request.user.is_authenticated:
            if request.method in READ_METHODS:
                return authorization.can_read
            if request.method in WRITE_METHODS:
                return authorization.can_write
            return authorization.is_admin
        return False
