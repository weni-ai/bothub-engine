from rest_framework import permissions

from bothub.api.v2 import READ_METHODS, WRITE_METHODS
from utils import get_user


class InternalOrganizationAdminHasPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.organization.get_organization_authorization(get_user(request.query_params.get("user_email", None)))
        return authorization.is_admin


class InternalOrganizationHasPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = get_user(request.query_params.get("user_email", None))
        if user is not None:
            authorization = obj.get_organization_authorization(user)
            if request.method in READ_METHODS:
                return authorization.can_read
            if request.method in WRITE_METHODS:
                return authorization.can_write
            return authorization.is_admin
        return False
