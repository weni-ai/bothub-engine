import logging

from django.utils.translation import ugettext_lazy as _
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from bothub.common.models import RepositoryTranslator, Repository


LOGGER = logging.getLogger("weni_django_oidc")


class TranslatorAuthentication(TokenAuthentication):
    keyword = "Translator"
    model = RepositoryTranslator

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.get(pk=key)
        except RepositoryTranslator.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Invalid token."))

        repository = Repository.objects.get(
            pk=token.repository_version_language.repository_version.repository.pk
        )
        authorization = repository.get_user_authorization(token.created_by)

        if not authorization.can_translate:
            raise exceptions.PermissionDenied()

        return (token.created_by, token)


class WeniOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    def verify_claims(self, claims):
        # validação de permissão
        verified = super(WeniOIDCAuthenticationBackend, self).verify_claims(claims)
        # is_admin = "admin" in claims.get("roles", [])
        return (
            verified
        )  # and is_admin # not checking for user roles from keycloak at this time

    def get_username(self, claims):
        username = claims.get("preferred_username")
        if username:
            return username
        return super(WeniOIDCAuthenticationBackend, self).get_username(claims=claims)

    def create_user(self, claims):
        # Override existing create_user method in OIDCAuthenticationBackend
        email = claims.get("email")
        username = self.get_username(claims)[:16]
        user = self.UserModel.objects.create_user(email, username)

        user.name = claims.get("name", "")
        user.save()

        return user

    def update_user(self, user, claims):
        user.name = claims.get("name", "")
        user.email = claims.get("email", "")
        user.save()

        return user
