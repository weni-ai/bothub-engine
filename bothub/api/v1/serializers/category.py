from rest_framework import serializers

from bothub.common.models import RepositoryCategory


class RepositoryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryCategory
        fields = [
            'id',
            'name',
            'icon',
        ]
        ref_name = None
