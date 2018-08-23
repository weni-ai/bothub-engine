from rest_framework import serializers

from bothub.common.models import Repository
from bothub.common.models import RepositoryCategory
from bothub.common.languages import LANGUAGE_CHOICES


class RepositoryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryCategory
        fields = [
            'id',
            'name',
        ]


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = [
            'uuid',
            'owner',
            'name',
            'slug',
            'language',
            'categories',
            'categories_list',
            'description',
            'is_private',
            'owner__nickname',
            'absolute_url',
            'available_languages',
        ]

    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault())
    categories_list = RepositoryCategorySerializer(
        many=True,
        source='categories',
        read_only=True)
    language = serializers.ChoiceField(
        LANGUAGE_CHOICES,
        label=Repository._meta.get_field('language').verbose_name)
    owner__nickname = serializers.SlugRelatedField(
        source='owner',
        slug_field='nickname',
        read_only=True)
    absolute_url = serializers.SerializerMethodField()

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()
