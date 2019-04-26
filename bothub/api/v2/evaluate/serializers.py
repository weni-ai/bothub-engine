from django.utils.translation import gettext as _
from rest_framework import serializers

from bothub.common.models import Repository
from bothub.common.models import RepositoryEntity
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

    def save(self):
        repository_evaluate = self.validated_data.get('repository_evaluate')
        entity = RepositoryEvaluateEntity.objects.create(
            start=self.validated_data.get('start'),
            end=self.validated_data.get('end'),
            repository_evaluate=repository_evaluate,
            entity=RepositoryEntity.objects.get(
                repository=repository_evaluate.repository_update.repository,
                value=self.validated_data.get('entity'),
                create_entity=False,
            )
        )

        return entity


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

        self._update_entities(entities, evaluate)
        return evaluate

    def update(self, instance, validated_data):
        repository = validated_data.pop('repository')
        language = validated_data.get('language', instance.language)

        instance.text = validated_data.get('text', instance.text)
        instance.intent = validated_data.get('intent', instance.intent)
        instance.repository_update = repository.current_update(language)
        instance.save()
        instance.delete_entities()

        self._update_entities(validated_data.pop('entities'), instance)
        return instance

    def _update_entities(self, entities, evaluate):
        for entity in entities:
            entity.update({'repository_evaluate': evaluate.pk})
            entity_serializer = RepositoryEvaluateEntitySerializer(data=entity)
            entity_serializer.is_valid(raise_exception=True)
            entity_serializer.save()
