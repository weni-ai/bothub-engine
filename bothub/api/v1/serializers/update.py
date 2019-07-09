from rest_framework import serializers

from bothub.common.models import RepositoryUpdate


class RepositoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryUpdate
        fields = [
            'id',
            'repository',
            'language',
            'created_at',
            'by',
            'by__nickname',
            'training_started_at',
            'trained_at',
            'failed_at',
        ]
        ref_name = None

    by__nickname = serializers.SlugRelatedField(
        source='by',
        slug_field='nickname',
        read_only=True)
