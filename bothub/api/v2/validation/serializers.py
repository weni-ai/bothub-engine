from rest_framework import serializers
from rest_framework.fields import empty
from django.utils.translation import gettext as _

from bothub.common.models import Repository
from bothub.common.models import RepositoryValidation
from bothub.common.models import RepositoryValidationEntity
from bothub.common import languages

from bothub.api.v1.fields import EntityText
from bothub.api.v1.fields import EntityValueField
from bothub.api.v1.fields import LabelValueField

from bothub.api.v1.validators import CanContributeInRepositoryValidator
from bothub.api.v1.validators import EntityNotEqualLabelValidator

from .validators import DoesIntentExistValidator
from .validators import DoesEntityAndLabelExistValidator
from .validators import RepositoryValidationWithIntentOrEntityValidator


class RepositoryValidationEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryValidationEntity
        fields = [
            'id',
            'repository_validation',
            'start',
            'end',
            'entity',
            'label',
            'created_at',
            'value',
        ]

    repository_validation = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryValidation.objects,
        help_text=_('Example\'s ID'))

    entity = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()

    def get_entity(self, obj):
        return obj.entity.value

    def get_label(self, obj):
        if not obj.entity.label:
            return None
        return obj.entity.label.value

class NewRepositoryValidationEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryValidationEntity
        fields = [
            'repository_validation',
            'start',
            'end',
            'entity',
            'label',
        ]

    repository_validation = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryValidation.objects,
        required=False)

    entity = EntityValueField()

    label = LabelValueField(
        allow_blank=True,
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(EntityNotEqualLabelValidator())
        self.validators.append(DoesEntityAndLabelExistValidator())

    def create(self, validated_data):
        repository_validation = validated_data.pop('repository_validation', None)
        assert repository_validation
        label = validated_data.pop('label', empty)
        validation_entity = self.Meta.model.objects.create(
            repository_validation=repository_validation,
            **validated_data)
        if label is not empty:
            validation_entity.entity.set_label(label)
            validation_entity.entity.save(update_fields=['label'])
        return validation_entity


class RepositoryValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryValidation
        fields = [
            'id',
            'repository_update',
            'deleted_in',
            'text',
            'intent',
            'language',
            'created_at',
            'entities',
        ]
        read_only_fields = [
            'repository_update',
            'deleted_in',
        ]

    entities = RepositoryValidationEntitySerializer(
        many=True,
        read_only=True)

    language = serializers.SerializerMethodField()

    def get_language(self, obj):
        return obj.language


class NewRepositoryValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryValidation
        fields = [
            'id',
            'repository',
            'repository_update',
            'text',
            'language',
            'intent',
            'entities',
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
        write_only=True,
        style={'show': False})
    repository_update = serializers.PrimaryKeyRelatedField(
        read_only=True,
        style={'show': False})
    language = serializers.ChoiceField(
        languages.LANGUAGE_CHOICES,
        allow_blank=True,
        required=False)
    entities = NewRepositoryValidationEntitySerializer(
        many=True,
        style={'text_field': 'text'})
    intent = serializers.CharField(
        validators=[
            DoesIntentExistValidator(),
        ]
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(RepositoryValidationWithIntentOrEntityValidator())

    def create(self, validated_data):
        entities_data = validated_data.pop('entities')
        repository = validated_data.pop('repository')
        try:
            language = validated_data.pop('language')
        except KeyError:
            language = None
        repository_update = repository.current_update(language or None)
        validated_data.update({'repository_update': repository_update})
        validation = self.Meta.model.objects.create(**validated_data)
        for entity_data in entities_data:
            entity_data.update({'repository_validation': validation.pk})
            entity_serializer = NewRepositoryValidationEntitySerializer(
                data=entity_data)
            entity_serializer.is_valid(raise_exception=True)
            entity_serializer.save()
        return validation
