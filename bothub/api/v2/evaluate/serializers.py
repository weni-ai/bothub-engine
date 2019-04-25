from rest_framework import serializers

from bothub.common.models import Repository
from bothub.common.models import RepositoryEntity
from bothub.common.models import RepositoryEvaluate
from bothub.common.models import RepositoryEvaluateEntity

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

    def create(self, validated_data):
        repository_evaluate = validated_data.get('repository_evaluate')

        entity = self.Meta.model.objects.create(
            start=validated_data.get('start'),
            end=validated_data.get('end'),
            repository_evaluate=repository_evaluate,
            entity=RepositoryEntity.objects.get(
                repository=repository_evaluate.repository_update.repository,
                value=validated_data.get('entity'),
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
            'language',
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
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(ThereIsEntityValidator())
        self.validators.append(ThereIsIntentValidator())

    def create(self, validated_data):
        entities = validated_data.pop('entities')
        repository = validated_data.pop('repository')

        try:
            language = validated_data.pop('language')
        except KeyError:
            language = None

        repository_update = repository.current_update(language)
        validated_data.update({'repository_update': repository_update})
        evaluate = super().create(validated_data)

        for entity in entities:
            entity.update({'repository_evaluate': evaluate.pk})
            entity_serializer = RepositoryEvaluateEntitySerializer(data=entity)
            entity_serializer.is_valid(raise_exception=True)
            entity_serializer.save()

        return evaluate
