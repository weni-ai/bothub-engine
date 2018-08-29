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


class IntentSerializer(serializers.Serializer):
    value = serializers.CharField()
    examples__count = serializers.IntegerField()


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = [
            'uuid',
            'name',
            'slug',
            'description',
            'is_private',
            'available_languages',
            'entities_list',
            'labels_list',
            'ready_for_train',
            'created_at',
            'language',
            'owner',
            'owner__nickname',
            'categories',
            'categories_list',
            'intents',
            'intents_list',
            'labels',
            'examples__count',
            'absolute_url',
        ]
        read_only = [
            'uuid',
            'available_languages',
            'entities_list',
            'labels_list',
            'ready_for_train',
            'created_at',
        ]

    language = serializers.ChoiceField(
        LANGUAGE_CHOICES,
        label=Repository._meta.get_field('language').verbose_name)
    owner = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True)
    owner__nickname = serializers.SlugRelatedField(
        source='owner',
        slug_field='nickname',
        read_only=True)
    intents = serializers.SerializerMethodField()
    intents_list = serializers.SerializerMethodField()
    categories = RepositoryCategorySerializer(
        many=True,
        read_only=True)
    categories_list = serializers.SlugRelatedField(
        source='categories',
        slug_field='name',
        many=True,
        read_only=True)
    labels = RepositoryEntityLabelSerializer(
        many=True,
        read_only=True)
    examples__count = serializers.SerializerMethodField()
    absolute_url = serializers.SerializerMethodField()

    def get_intents(self, obj):
        return IntentSerializer(
            map(
                lambda intent: {
                    'value': intent,
                    'examples__count': obj.examples(
                        exclude_deleted=False).filter(
                            intent=intent).count(),
                },
                obj.intents),
            many=True).data

    def get_intents_list(self, obj):
        return obj.intents

    def get_examples__count(self, obj):
        return obj.examples().count()

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()
