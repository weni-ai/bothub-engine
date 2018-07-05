from rest_framework import serializers
from django.utils.translation import gettext as _

from bothub.common.models import RequestRepositoryAuthorization
from bothub.common.models import Repository
from ..fields import TextField


class NewRequestRepositoryAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestRepositoryAuthorization
        fields = [
            'user',
            'repository',
            'text',
        ]

    repository = serializers.PrimaryKeyRelatedField(
        queryset=Repository.objects,
        style={'show': False})
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        style={'show': False})
    text = TextField(
        label=_('Leave a message for repository administrators'),
        min_length=5,
        max_length=RequestRepositoryAuthorization._meta.get_field(
            'text').max_length)


class RequestRepositoryAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestRepositoryAuthorization
        fields = [
            'id',
            'user',
            'user__nickname',
            'repository',
            'text',
            'created_at',
        ]

    user__nickname = serializers.SlugRelatedField(
        source='user',
        slug_field='nickname',
        read_only=True)
