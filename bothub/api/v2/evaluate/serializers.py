from django.utils.translation import gettext as _
from rest_framework import serializers

from bothub.common.models import Repository
from bothub.common.models import RepositoryEvaluate
from bothub.common.models import RepositoryEvaluateEntity
from bothub.common.languages import LANGUAGE_CHOICES

from ..fields import EntityValueField
from .validators import ThereIsEntityValidator
from .validators import ThereIsIntentValidator


class RepositoryEvaluateEntitySerializer(serializers.ModelSerializer):

    class Meta:
        model = RepositoryEvaluateEntity
        fields = [
            'repository_evaluate',
            'entity',
            'start',
            'end',
        ]

    repository_evaluate = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryEvaluate.objects,
        required=False
    )

    entity = EntityValueField()


class RepositoryEvaluateSerializer(serializers.ModelSerializer):

    class Meta:
        model = RepositoryEvaluate
        fields = [
            'id',
            'repository',
            'text',
            'language',
            'intent',
            'entities',
            'created_at',
        ]
        read_only_fields = [
            'deleted_in',
            'created_at',
        ]

    entities = RepositoryEvaluateEntitySerializer(
        many=True,
        required=False,
    )

    repository = serializers.PrimaryKeyRelatedField(
        queryset=Repository.objects,
        write_only=True,
        required=True,
    )

    language = serializers.ChoiceField(
        LANGUAGE_CHOICES,
        label=_('Language')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(ThereIsEntityValidator())
        self.validators.append(ThereIsIntentValidator())

    def create(self, validated_data):
        entities = validated_data.pop('entities')
        repository = validated_data.pop('repository')
        language = validated_data.pop('language')

        repository_update = repository.current_update(language)
        validated_data.update({'repository_update': repository_update})
        evaluate = RepositoryEvaluate.objects.create(**validated_data)

        for entity in entities:
            RepositoryEvaluateEntity.objects.create(
                repository_evaluate=evaluate, **entity)

        return evaluate

    def update(self, instance, validated_data):
        repository = validated_data.pop('repository')
        language = validated_data.get('language', instance.language)

        instance.text = validated_data.get('text', instance.text)
        instance.intent = validated_data.get('intent', instance.intent)
        instance.repository_update = repository.current_update(language)
        instance.save()
        instance.delete_entities()

        for entity in validated_data.pop('entities'):
            RepositoryEvaluateEntity.objects.create(
                repository_evaluate=instance, **entity)

        return instance
