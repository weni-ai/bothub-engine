import logging

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

LOGGER = logging.getLogger("connect_django_oidc")


class ConnectOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    """
    Custom authentication class for django-admin.
    """

    def verify_claims(self, claims):
        #validação de permissão
        verified = super(ConnectOIDCAuthenticationBackend, self).verify_claims(claims)
        is_admin = "admin" in claims.get("roles", [])
        return verified #and is_admin # not checking for user roles from keycloak at this time

    def create_user(self, claims):
        # Override existing create_user method in OIDCAuthenticationBackend
        email = claims.get('email')
        username = self.get_username(claims)
        user = self.UserModel.objects.create_user(email, username)

        old_username = user.nickname
        user.nickname = claims.get("preferred_username", old_username)
        user.name = claims.get("name", "")
        user.email = claims.get("email", "")
        user.save()

        return user

    def update_user(self, user, claims):
        user.name = claims.get("name", "")
        user.email = claims.get("email", "")
        user.save()

        return user
