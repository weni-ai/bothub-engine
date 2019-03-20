from rest_framework import serializers
from django.utils.translation import gettext as _

from bothub.common.models import RepositoryValidation
from bothub.common.models import RepositoryValidationEntity


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
        help_text=_('Validation\'s ID'))
    entity = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()

    def get_entity(self, obj):
        return obj.entity.value

    def get_label(self, obj):
        if not obj.entity.label:
            return None
        return obj.entity.label.value


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
            'translations',
        ]
        read_only_fields = [
            'repository_update',
            'deleted_in',
            'translations',
        ]

    entities = RepositoryValidationEntitySerializer(
        many=True,
        read_only=True)
