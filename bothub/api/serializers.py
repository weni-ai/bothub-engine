from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError as DjangoValidationError

from bothub.common.models import Repository
from bothub.common.models import RepositoryUpdate
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryTranslatedExampleEntity
from bothub.common.models import RepositoryAuthorization


# Defaults

class CurrentUpdateDefault(object):
    def set_context(self, serializer_field):
        request = serializer_field.context['request']
        repository_uuid = request.POST.get('repository_uuid')

        if not repository_uuid:
            raise ValidationError(_('repository_uuid is required'))

        try:
            repository = Repository.objects.get(uuid=repository_uuid)
        except Repository.DoesNotExist:
            raise NotFound(
                _('Repository {} does not exist').format(repository_uuid))
        except DjangoValidationError:
            raise ValidationError(_('Invalid repository_uuid'))

        self.repository_update = repository.current_update()

    def __call__(self):
        return self.repository_update


# Serializers

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
            'description',
            'is_private',
            'created_at',
        ]

    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault())


class CurrentRepositoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryUpdate
        fields = [
            'id',
            'repository',
            'language',
            'created_at',
        ]


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
        queryset=RepositoryExample.objects)
    value = serializers.SerializerMethodField()

    def get_value(self, obj):
        return obj.value


class RepositoryExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryExample
        fields = [
            'id',
            'repository_update',
            'deleted_in',
            'text',
            'intent',
            'created_at',
            'entities',
        ]
        read_only_fields = [
            'deleted_in',
        ]

    repository_update = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=CurrentUpdateDefault())
    entities = RepositoryExampleEntitySerializer(
        many=True,
        read_only=True)


class RepositoryTranslatedExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryTranslatedExample
        fields = [
            'id',
            'original_example',
            'language',
            'text',
            'has_valid_entities',
        ]

    original_example = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryExample.objects)
    has_valid_entities = serializers.SerializerMethodField()

    def get_has_valid_entities(self, obj):
        return obj.has_valid_entities


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
        queryset=RepositoryTranslatedExample.objects)
    value = serializers.SerializerMethodField()

    def get_value(self, obj):
        return obj.value


class RepositoryAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryAuthorization
        fields = [
            'uuid',
            'user',
            'repository',
            'created_at',
        ]
