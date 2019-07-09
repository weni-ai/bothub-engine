from django.utils.translation import gettext as _
from rest_framework import serializers

from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryExampleEntity


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
        ref_name = None

    repository_example = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryExample.objects,
        help_text=_('Example\'s ID'))
    entity = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()

    def get_entity(self, obj):
        return obj.entity.value

    def get_label(self, obj):
        if not obj.entity.label:
            return None
        return obj.entity.label.value


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
            'translations',
        ]
        ref_name = None

    entities = RepositoryExampleEntitySerializer(
        many=True,
        read_only=True)
