from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import serializers

from bothub.authentication.models import User
from ..fields import PasswordField
from django.utils.translation import gettext as _


class LoginSerializer(AuthTokenSerializer, serializers.ModelSerializer):
    username = serializers.EmailField(
        label=_('Email'),
    )
    password = PasswordField(
        label=_('Password'),
    )

    class Meta:
        model = User
        fields = [
            'username',
            'password',
        ]
        ref_name = None
