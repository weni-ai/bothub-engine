from rest_framework import serializers

from bothub.common.models import Repository
from bothub.common.models import RepositoryCategory
from bothub.common.models import RepositoryEntityLabel
from bothub.common.languages import LANGUAGE_CHOICES


class RepositoryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryCategory
        fields = [
            'id',
            'name',
        ]


class RepositoryEntityLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryEntityLabel
        fields = [
            'repository',
            'value',
            'entities',
        ]

    entities = serializers.SlugRelatedField(
        many=True,
        slug_field='value',
        read_only=True)


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = [
            'uuid',
            'name',
            'slug',
            'language',
            'description',
            'is_private',
            'absolute_url',
            'available_languages',
            'intents',
            'entities_list',
            'labels_list',
            'ready_for_train',
            'created_at',
            'owner',
            'owner__nickname',
            'categories',
            'categories_list',
            'labels',
            'examples__count',
        ]

    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault())
    owner__nickname = serializers.SlugRelatedField(
        source='owner',
        slug_field='nickname',
        read_only=True)
    categories = RepositoryCategorySerializer(
        many=True,
        read_only=True)
    categories_list = serializers.SlugRelatedField(
        source='categories',
        slug_field='name',
        many=True,
        read_only=True)
    language = serializers.ChoiceField(
        LANGUAGE_CHOICES,
        label=Repository._meta.get_field('language').verbose_name)
    owner__nickname = serializers.SlugRelatedField(
        source='owner',
        slug_field='nickname',
        read_only=True)
    absolute_url = serializers.SerializerMethodField()
    labels = RepositoryEntityLabelSerializer(many=True)
    examples__count = serializers.SerializerMethodField()

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()

    def get_examples__count(self, obj):
        return obj.examples().count()
