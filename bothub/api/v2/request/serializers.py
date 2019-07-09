from rest_framework import serializers

from bothub.common.models import RequestRepositoryAuthorization


class RequestRepositoryAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestRepositoryAuthorization
        fields = [
            'id',
            'user',
            'user__nickname',
            'repository',
            'text',
            'approved_by',
            'approved_by__nickname',
            'created_at',
        ]
        ref_name = None

    user__nickname = serializers.SlugRelatedField(
        source='user',
        slug_field='nickname',
        read_only=True)
    approved_by__nickname = serializers.SlugRelatedField(
        source='approved_by',
        slug_field='nickname',
        read_only=True)
