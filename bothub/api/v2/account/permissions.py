from rest_framework import permissions


class ChangePasswordPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.check_password(request.data.get('password')):
            return False
        return True
