from rest_framework import serializers

from django.utils.translation import gettext as _

from bothub.common.models import RepositoryTranslatedExampleEntity
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryExample

from ..validators import CanContributeInRepositoryTranslatedExampleValidator
from ..validators import CanContributeInRepositoryExampleValidator


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
