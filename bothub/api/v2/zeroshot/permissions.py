from rest_framework import permissions
from bothub.common.models import RepositoryAuthorization
from .. import READ_METHODS

class ZeroshotOptionsPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            authorization = obj.option.repository_zeroshot.repository.get_user_authorization(
                request.user
            )
        else:
            if "token" in request.data:
                authorization = RepositoryAuthorization.objects.get(uuid=request.data.get("token"), repository=request.get("repository_uuid"))
        
        print(request.data, request.user, request.method, authorization.role, authorization.can_read, authorization.can_contribute) 
        if request.method in READ_METHODS:
            return authorization.can_read
        return authorization.can_contribute

class ZeroshotOptionsTextPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print(request.data, request.user)
        if request.user.is_authenticated:
            authorization = obj.option.repository_zeroshot.repository.get_user_authorization(
                request.user
            )
        else:
            if "token" in request.data:
                authorization = RepositoryAuthorization.objects.get(uuid=request.data.get("token"), repository=request.get("repository_uuid"))
            
        if request.method in READ_METHODS:
            return authorization.can_read
        return authorization.can_contribute
