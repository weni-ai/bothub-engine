from rest_framework import permissions
from bothub.common.models import RepositoryAuthorization, Repository
from .. import READ_METHODS


class ZeroshotOptionsPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        can = True
        repository = Repository.objects.get(uuid=request.data.get("repository_uuid"))
        if request.user.is_authenticated:
            authorization = repository.get_user_authorization(
                request.user
            )
        else:
            if "token" in request.data:
                authorization = RepositoryAuthorization.objects.get(uuid=request.data.get("token"), repository=repository)
            else:
                can = False
        if request.method in READ_METHODS:
            can = can and authorization.can_read
        return can and authorization.can_contribute


class ZeroshotOptionsTextPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        can = True
        repository = Repository.objects.get(uuid=request.data.get("repository_uuid"))
        if request.user.is_authenticated:
            authorization = repository.get_user_authorization(
                request.user
            )
        else:
            if "token" in request.data:
                authorization = RepositoryAuthorization.objects.get(uuid=request.data.get("token"), repository=repository)
            else:
                can = False
        if request.method in READ_METHODS:
            can = can and authorization.can_read
        return can and authorization.can_contribute


class ZeroshotPredictPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        can = True
        repository = Repository.objects.get(uuid=request.data.get("repository_uuid"))
        if request.user.is_authenticated:
            authorization = repository.get_user_authorization(
                request.user
            )
        else:
            if "token" in request.data:
                authorization = RepositoryAuthorization.objects.get(uuid=request.data.get("token"), repository=repository)
            else:
                can = False
        if request.method in READ_METHODS:
            can = can and authorization.can_read
        return can and authorization.can_contribute 
