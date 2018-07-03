from rest_framework import serializers

from bothub.common.models import RequestRepositoryAuthorization


class NewRequestRepositoryAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestRepositoryAuthorization
        fields = [
            'user',
            'repository',
            'text',
        ]

    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        style={'show': False})
