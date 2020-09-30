from rest_framework import permissions

from bothub.common.models import Repository
from .. import READ_METHODS


class RepositoryExampleTranslatorPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            repository = Repository.objects.get(
                pk=request.auth.repository_version_language.repository_version.repository.pk
            )
            authorization = repository.get_user_authorization(request.user)

            if request.method in READ_METHODS:
                return authorization.can_read
            return authorization.can_contribute
        except Repository.DoesNotExist:
            return False
        except AttributeError:
            return False
