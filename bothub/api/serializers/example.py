from rest_framework import serializers

from django.utils.translation import gettext as _

from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity

from ..fields import EntityText
from ..validators import CanContributeInRepositoryExampleValidator
from ..validators import CanContributeInRepositoryValidator
from ..validators import ExampleWithIntentOrEntityValidator
from .translate import RepositoryTranslatedExampleSerializer


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


class NewRepositoryExampleEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryExampleEntity
        fields = [
            'repository_example',
            'start',
            'end',
            'entity',
        ]


class RepositoryExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryExample
        fields = [
            'id',
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

    entities = RepositoryExampleEntitySerializer(
        many=True,
        read_only=True)
    translations = RepositoryTranslatedExampleSerializer(
        many=True,
        read_only=True)
    language = serializers.SerializerMethodField()

    def get_language(self, obj):
        return obj.language


class NewRepositoryExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryExample
        fields = [
            'id',
            'repository',
            'repository_update',
            'text',
            'entities',
            'intent',
        ]

    id = serializers.PrimaryKeyRelatedField(
        read_only=True,
        style={'show': False})
    text = EntityText(style={'entities_field': 'entities'})
    repository = serializers.PrimaryKeyRelatedField(
        queryset=Repository.objects,
        validators=[
            CanContributeInRepositoryValidator(),
        ],
        source='repository_update',
        style={'show': False})
    repository_update = serializers.PrimaryKeyRelatedField(
        read_only=True,
        style={'show': False})
    entities = NewRepositoryExampleEntitySerializer(
        many=True,
        style={'text_field': 'text'})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(ExampleWithIntentOrEntityValidator())

    def validate_repository(self, repository):
        return repository.current_update()

    def create(self, validated_data):
        entities_data = validated_data.pop('entities')
        example = self.Meta.model.objects.create(**validated_data)
        for entity_data in entities_data:
            RepositoryExampleEntity.objects.create(
                repository_example=example,
                **entity_data)
        return example
