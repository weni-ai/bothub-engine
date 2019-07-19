from rest_framework import permissions
from bothub.authentication.models import User


class ChangePasswordPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.check_password(request.data.get('password')):
            return False
        return True


class RequestResetPasswordPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if User.objects.filter(email=request.data.get('email')).count() == 0:
            return False
        return True
