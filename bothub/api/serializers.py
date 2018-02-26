from rest_framework import serializers

from bothub.common.models import Repository
from bothub.common.models import RepositoryUpdate


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = [
            'uuid',
            'owner',
            'slug',
            'is_private',
            'created_at',
        ]
    
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault())

class CurrentRepositoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryUpdate
        fields = [
            'id',
            'repository',
            'created_at',
        ]
