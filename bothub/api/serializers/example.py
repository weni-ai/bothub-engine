from rest_framework import serializers

from django.utils.translation import gettext as _

from bothub.common.models import Repository
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity

from ..validators import CanContributeInRepositoryExampleValidator
from ..validators import CanContributeInRepositoryValidator
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
        validators=[
            CanContributeInRepositoryValidator(),
        ],
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
        return repository.current_update()
