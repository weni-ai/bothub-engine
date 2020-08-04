from rest_framework import permissions


class OrganizationAdminManagerAuthorization(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.organization.get_organization_authorization(request.user)
        return authorization.is_admin
