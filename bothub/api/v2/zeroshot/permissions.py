from rest_framework import permissions
from .. import READ_METHODS

class ZeroshotOptionsPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.repository_zeroshot.repository.get_user_authorization(
            request.user
        )
        if request.method in READ_METHODS:
            return authorization.can_read
        return authorization.can_contribute

class ZeroshotOptionsTextPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.option.repository_zeroshot.repository.get_user_authorization(
            request.user
        )
        if request.method in READ_METHODS:
            return authorization.can_read
        return authorization.can_contribute
