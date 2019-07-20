from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
        required=True,
        validators=[
            validate_password,
        ]
    )

    class Meta:
        model = User
        fields = [
            'current_password',
            'password'
        ]
        ref_name = None

    def validate_current_password(self, value):
        request = self.context.get('request')
        if not request.user.check_password(value):
            raise ValidationError(_('Wrong password'))
        return value


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

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            raise ValidationError(_('No user registered with this email'))
