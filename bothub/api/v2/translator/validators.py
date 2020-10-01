from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import PermissionDenied


class CanContributeInRepositoryExampleTranslatorValidator(object):
    def __call__(self, value):
        repository = value.repository_version_language.repository_version.repository
        user_authorization = repository.get_user_authorization(self.request.user)

        if not user_authorization.can_translate:
            raise PermissionDenied(_("You can't contribute in this repository"))

        if (
            not value.repository_version_language.repository_version
            == self.request.auth.repository_version_language.repository_version
        ):
            raise PermissionDenied(_("You can't contribute in this repository"))

    def set_context(self, serializer):
        self.request = serializer.context.get("request")
