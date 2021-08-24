from rest_framework import permissions

from bothub.api.v2 import READ_METHODS


class QABasePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        authorization = obj.get_user_authorization(request.user)
        if request.method in READ_METHODS:
            return authorization.can_read
        return authorization.can_contribute

class QAKnowledgeBasePermission(QABasePermission):
    pass


class QAContextPermission(QABasePermission):
    pass
