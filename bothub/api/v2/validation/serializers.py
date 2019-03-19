from rest_framework import serializers

from bothub.common.models import RepositoryValidation


class RepositoryValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryTestingQuery
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
