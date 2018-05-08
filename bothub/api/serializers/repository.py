from rest_framework import serializers

from bothub.common.models import Repository
from bothub.common.models import RepositoryCategory
from bothub.common.models import RepositoryAuthorization

from ..fields import ModelMultipleChoiceField
from ..fields import TextField

from .category import RepositoryCategorySerializer


class NewRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = [
            'uuid',
            'owner',
            'name',
            'slug',
            'language',
            'categories',
            'description',
            'is_private',
        ]

    uuid = serializers.ReadOnlyField(
        style={'show': False})
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        style={'show': False})
    categories = ModelMultipleChoiceField(
        child_relation=serializers.PrimaryKeyRelatedField(
            queryset=RepositoryCategory.objects.all()),
        allow_empty=False,
        help_text=Repository.CATEGORIES_HELP_TEXT)
    description = TextField(
        allow_blank=True,
        help_text=Repository.DESCRIPTION_HELP_TEXT)


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = [
            'uuid',
            'owner',
            'owner__nickname',
            'name',
            'slug',
            'language',
            'available_languages',
            'categories',
            'categories_list',
            'description',
            'is_private',
            'created_at',
        ]

    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault())
    owner__nickname = serializers.SlugRelatedField(
        source='owner',
        slug_field='nickname',
        read_only=True)
    categories_list = serializers.SerializerMethodField()

    def get_categories_list(self, obj):
        return RepositoryCategorySerializer(obj.categories, many=True).data


class RepositoryAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryAuthorization
        fields = [
            'uuid',
            'user',
            'repository',
            'created_at',
        ]
