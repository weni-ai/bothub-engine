from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
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


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = [
            'uuid',
            'owner',
            'name',
            'slug',
            'language',
            'categories',
            'categories_list',
            'description',
            'is_private',
            'created_at',
        ]

    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault())
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
        ])
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
        ])
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
        ])
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
            'nick',
            'password',
        ]

    password = serializers.CharField(
        write_only=True,
        validators=[
            validate_password,
        ])

    def validate_password(self, value):
        return make_password(value)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'name',
            'locale',
        ]
