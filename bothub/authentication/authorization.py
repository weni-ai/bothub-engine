from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from bothub.common.models import RepositoryTranslator


class TranslatorAuthentication(TokenAuthentication):
    keyword = "Translator"
    model = RepositoryTranslator

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.get(pk=key)
        except RepositoryTranslator.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        return (token.created_by, token)
