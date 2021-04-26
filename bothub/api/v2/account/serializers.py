from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from bothub.authentication.models import User, RepositoryOwner
from ..fields import PasswordField, TextField


class LoginSerializer(AuthTokenSerializer, serializers.ModelSerializer):
    username = serializers.EmailField(label=_("Email"))
    password = PasswordField(label=_("Password"))

    class Meta:
        model = User
        fields = ["username", "password"]
        ref_name = None


class RegisterUserSerializer(serializers.ModelSerializer):
    password = PasswordField(
        write_only=True, validators=[validate_password], label=_("Password")
    )

    class Meta:
        model = User
        fields = ["email", "name", "nickname", "password", "language"]
        ref_name = None

    @staticmethod
    def validate_password(value):
        return make_password(value)


class ChangePasswordSerializer(serializers.ModelSerializer):
    current_password = PasswordField(required=True, label=_("Current Password"))
    password = PasswordField(
        required=True, validators=[validate_password], label=_("New Password")
    )

    class Meta:
        model = User
        fields = ["current_password", "password"]
        ref_name = None

    def validate_current_password(self, value):
        request = self.context.get("request")
        if not request.user.check_password(value):
            raise ValidationError(_("Wrong password"))
        return value


class RequestResetPasswordSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(label=_("Email"), required=True)

    class Meta:
        model = User
        fields = ["email"]
        ref_name = None

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            raise ValidationError(_("No user registered with this email"))


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryOwner
        fields = [
            "nickname",
            "name",
            "locale",
            "is_organization",
            "biography",
            "language",
        ]
        ref_name = None

    is_organization = serializers.BooleanField(style={"show": False}, read_only=True)
    biography = TextField(min_length=0, max_length=350, required=False)
    language = serializers.CharField(read_only=True)


class ResetPasswordSerializer(serializers.ModelSerializer):
    token = serializers.CharField(label=_("Token"), style={"show": False})
    password = PasswordField(
        label=_("New Password"), required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ["token", "password"]
        ref_name = None

    def validate_token(self, value):
        user = self.context.get("view").get_object()
        if not user.check_password_reset_token(value):
            raise ValidationError(_("Invalid token for this user"))
        return value
