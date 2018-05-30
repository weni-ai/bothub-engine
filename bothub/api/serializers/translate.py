from rest_framework import serializers

from django.utils.translation import gettext as _

from bothub.common.models import RepositoryTranslatedExampleEntity
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryExample

from ..validators import CanContributeInRepositoryTranslatedExampleValidator
from ..validators import CanContributeInRepositoryExampleValidator
from ..validators import TranslatedExampleEntitiesValidator


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
            'from_language',
            'language',
            'text',
            'has_valid_entities',
            'entities',
            'created_at',
        ]

    original_example = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryExample.objects,
        validators=[
            CanContributeInRepositoryExampleValidator(),
        ],
        help_text=_('Example\'s ID'))
    from_language = serializers.SerializerMethodField()
    has_valid_entities = serializers.SerializerMethodField()
    entities = RepositoryTranslatedExampleEntitySeralizer(
        many=True,
        read_only=True)

    def get_from_language(self, obj):
        return obj.original_example.repository_update.language

    def get_has_valid_entities(self, obj):
        return obj.has_valid_entities


class NewRepositoryTranslatedExampleEntitySeralizer(
        serializers.ModelSerializer):
    class Meta:
        model = RepositoryTranslatedExampleEntity
        fields = [
            'start',
            'end',
            'entity',
        ]


class NewRepositoryTranslatedExampleSerializer(serializers.ModelSerializer):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(TranslatedExampleEntitiesValidator())

    original_example = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryExample.objects,
        validators=[
            CanContributeInRepositoryExampleValidator(),
        ],
        help_text=_('Example\'s ID'))
    has_valid_entities = serializers.SerializerMethodField()
    entities = NewRepositoryTranslatedExampleEntitySeralizer(
        many=True,
        style={'text_field': 'text'})

    def get_has_valid_entities(self, obj):
        return obj.has_valid_entities

    def create(self, validated_data):
        entities_data = validated_data.pop('entities')

        translated = self.Meta.model.objects.create(**validated_data)
        for entity_data in entities_data:
            RepositoryTranslatedExampleEntity.objects.create(
                repository_translated_example=translated,
                **entity_data)
        return translated
