from rest_framework import serializers
from rest_framework.fields import empty

from django.utils.translation import gettext as _

from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity
from bothub.common.models import RepositoryEntity

from ..fields import EntityText
from ..fields import EntityValueField
from ..fields import LabelValueField
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
            'label',
            'created_at',
            'value',
        ]

    repository_example = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryExample.objects,
        validators=[
            CanContributeInRepositoryExampleValidator(),
        ],
        help_text=_('Example\'s ID'))
    entity = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()

    def get_entity(self, obj):
        return obj.entity.value

    def get_label(self, obj):
        if not obj.entity.label:
            return None
        return obj.entity.label.value


class NewRepositoryExampleEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryExampleEntity
        fields = [
            'repository_example',
            'start',
            'end',
            'entity',
            'entity_label',
        ]

    repository_example = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryExample.objects,
        required=False)

    entity = EntityValueField()
    entity_label = LabelValueField(
        allow_blank=True,
        required=False)

    def create(self, validated_data):
        repository_example = validated_data.pop('repository_example', None)
        assert repository_example
        entity_label = validated_data.pop('entity_label', empty)
        example_entity = self.Meta.model.objects.create(
            repository_example=repository_example,
            **validated_data)
        if entity_label is not empty:
            example_entity.entity.set_label(entity_label)
        return example_entity


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
            entity_data.update({'repository_example': example.pk})
            entity_serializer = NewRepositoryExampleEntitySerializer(
                data=entity_data)
            entity_serializer.is_valid(raise_exception=True)
            entity_serializer.save()
        return example


class RepositoryEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryEntity
        fields = [
            'repository',
            'value',
            'label',
        ]

    label = serializers.SerializerMethodField()

    def get_label(self, obj):
        if not obj.label:
            return None
        return obj.label.value
