import logging

from rest_framework import permissions

from django.conf import settings

logger = logging.getLogger("bothub.health.checks")


class ZeroshotTokenPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        logger.info(request.META)
        token = request.META.get('HTTP_AUTHORIZATION')

        if token:
            return token == f'Bearer {settings.FLOWS_TOKEN_ZEROSHOT}'
        else:
            return False

    def has_object_permission(self, request, view, obj):
        return self.has_object_permission(request, view, obj)
