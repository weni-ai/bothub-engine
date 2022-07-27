from rest_framework import permissions

from bothub.utils import get_user


class InternalOrganizationAdminHasPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.organization.get_organization_authorization(
            get_user(request.query_params.get("user_email", None))
        )
        return authorization.is_admin
