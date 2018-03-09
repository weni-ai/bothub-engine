from rest_framework.authtoken.models import Token

from bothub.authentication.models import User


def create_user_and_token(nick='fake'):
    user = User.objects.create_user(
            '{}@user.com'.format(nick),
            nick)
    token, create = Token.objects.get_or_create(user=user)
    return (user, token,)
