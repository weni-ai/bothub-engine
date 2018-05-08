from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

from bothub.authentication.models import User

from ..fields import PasswordField


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'name',
            'nickname',
            'password',
        ]

    password = PasswordField(
        write_only=True,
        validators=[
            validate_password,
        ])

    def validate_password(self, value):
        return make_password(value)


class EditUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'name',
            'locale',
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'nickname',
            'email',
            'name',
            'locale',
        ]


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(
        required=True)
    password = serializers.CharField(
        required=True,
        validators=[
            validate_password,
        ])

    def validate_current_password(self, value):
        request = self.context.get('request')
        if not request.user.check_password(value):
            raise ValidationError(_('Wrong password'))
        return value


class RequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label=_('Email'),
        required=True)

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            raise ValidationError(_('No user registered with this email'))


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(
        label=_('Token'))
    password = PasswordField(
        label=_('Password'),
        required=True,
        validators=[
            validate_password,
        ])

    def validate_token(self, value):
        user = self.context.get('view').get_object()
        if not user.check_password_reset_token(value):
            raise ValidationError(_('Invalid token for this user'))
        return value


class LoginSerializer(AuthTokenSerializer):
    username = serializers.EmailField(label=_("Email"))
    password = PasswordField(
        label=_("Password")
    )
