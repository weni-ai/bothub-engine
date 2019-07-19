from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import serializers

from bothub.authentication.models import User
from ..fields import PasswordField


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


class RegisterUserSerializer(serializers.ModelSerializer):
    password = PasswordField(
        write_only=True,
        validators=[
            validate_password,
        ])

    class Meta:
        model = User
        fields = [
            'email',
            'name',
            'nickname',
            'password',
        ]
        ref_name = None

    @staticmethod
    def validate_password(value):
        return make_password(value)


class ChangePasswordSerializer(serializers.ModelSerializer):
    current_password = PasswordField(
        required=True
    )
    password = PasswordField(
        required=True
    )

    class Meta:
        model = User
        fields = [
            'current_password',
            'password'
        ]
        ref_name = None


class RequestResetPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        label=_('Email'),
        required=True
    )

    class Meta:
        model = User
        fields = [
            'email'
        ]
        ref_name = None
