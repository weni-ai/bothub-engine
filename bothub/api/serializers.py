from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.serializers import AuthTokenSerializer
from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

from bothub.common.models import RepositoryCategory
from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryTranslatedExampleEntity
from bothub.common.models import RepositoryAuthorization
from bothub.authentication.models import User

from .fields import ModelMultipleChoiceField
from .fields import TextField
from .fields import PasswordField


# Validators

class CanContributeInRepositoryExampleValidator(object):
    def __call__(self, value):
        repository = value.repository_update.repository
        user_authorization = repository.get_user_authorization(
            self.request.user)
        if not user_authorization.can_contribute:
            raise PermissionDenied(
                _('You can\'t contribute in this repository'))

    def set_context(self, serializer):
        self.request = serializer.context.get('request')


class CanContributeInRepositoryTranslatedExampleValidator(object):
    def __call__(self, value):
        repository = value.original_example.repository_update.repository
        user_authorization = repository.get_user_authorization(
            self.request.user)
        if not user_authorization.can_contribute:
            raise PermissionDenied(
                _('You can\'t contribute in this repository'))

    def set_context(self, serializer):
        self.request = serializer.context.get('request')


# Serializers

class RepositoryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryCategory
        fields = [
            'id',
            'name',
        ]


class NewRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = [
            'uuid',
            'owner',
            'name',
            'slug',
            'language',
            'categories',
            'description',
            'is_private',
        ]

    uuid = serializers.ReadOnlyField(
        style={'show': False})
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        style={'show': False})
    categories = ModelMultipleChoiceField(
        child_relation=serializers.PrimaryKeyRelatedField(
            queryset=RepositoryCategory.objects.all()),
        allow_empty=False,
        help_text=Repository.CATEGORIES_HELP_TEXT)
    description = TextField(
        allow_blank=True,
        help_text=Repository.DESCRIPTION_HELP_TEXT)


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = [
            'uuid',
            'owner',
            'owner__nickname',
            'name',
            'slug',
            'language',
            'available_languages',
            'categories',
            'categories_list',
            'description',
            'is_private',
            'created_at',
        ]

    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault())
    owner__nickname = serializers.SlugRelatedField(
        source='owner',
        slug_field='nickname',
        read_only=True)
    categories_list = serializers.SerializerMethodField()

    def get_categories_list(self, obj):
        return RepositoryCategorySerializer(obj.categories, many=True).data


class RepositoryExampleEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryExampleEntity
        fields = [
            'id',
            'repository_example',
            'start',
            'end',
            'entity',
            'created_at',
            'value',
        ]

    repository_example = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryExample.objects,
        validators=[
            CanContributeInRepositoryExampleValidator(),
        ],
        help_text=_('Example\'s ID'))
    value = serializers.SerializerMethodField()

    def get_value(self, obj):
        return obj.value


class RepositoryTranslatedExampleEntitySeralizer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryTranslatedExampleEntity
        fields = [
            'id',
            'repository_translated_example',
            'start',
            'end',
            'entity',
            'created_at',
            'value',
        ]

    repository_translated_example = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryTranslatedExample.objects,
        validators=[
            CanContributeInRepositoryTranslatedExampleValidator(),
        ],
        help_text='Example translation ID')
    value = serializers.SerializerMethodField()

    def get_value(self, obj):
        return obj.value


class RepositoryTranslatedExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryTranslatedExample
        fields = [
            'id',
            'original_example',
            'language',
            'text',
            'has_valid_entities',
            'entities',
        ]

    original_example = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryExample.objects,
        validators=[
            CanContributeInRepositoryExampleValidator(),
        ],
        help_text=_('Example\'s ID'))
    has_valid_entities = serializers.SerializerMethodField()
    entities = RepositoryTranslatedExampleEntitySeralizer(
        many=True,
        read_only=True)

    def get_has_valid_entities(self, obj):
        return obj.has_valid_entities


class RepositoryExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryExample
        fields = [
            'id',
            'repository',
            'repository_update',
            'deleted_in',
            'text',
            'intent',
            'language',
            'created_at',
            'entities',
            'translations',
        ]
        read_only_fields = [
            'repository_update',
            'deleted_in',
        ]

    repository = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Repository.objects,
        source='repository_update')
    entities = RepositoryExampleEntitySerializer(
        many=True,
        read_only=True)
    translations = RepositoryTranslatedExampleSerializer(
        many=True,
        read_only=True)
    language = serializers.SerializerMethodField()

    def get_language(self, obj):
        return obj.language

    def validate_repository(self, repository):
        request = self.context.get('request')
        authorization = repository.get_user_authorization(request.user)
        if not authorization.can_contribute:
            raise PermissionDenied()
        return repository.current_update()


class RepositoryAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryAuthorization
        fields = [
            'uuid',
            'user',
            'repository',
            'created_at',
        ]


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
