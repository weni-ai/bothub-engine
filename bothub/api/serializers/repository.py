from rest_framework import serializers

from bothub.common.models import Repository
from bothub.common.models import RepositoryCategory
from bothub.common.models import RepositoryAuthorization
from bothub.common.languages import LANGUAGE_CHOICES

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


class EditRepositorySerializer(NewRepositorySerializer):
    pass


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
            'examples__count',
            'authorization',
            'ready_for_train',
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
    authorization = serializers.SerializerMethodField()
    examples__count = serializers.SerializerMethodField()

    def get_categories_list(self, obj):
        return RepositoryCategorySerializer(obj.categories, many=True).data

    def get_authorization(self, obj):
        request = self.context.get('request')
        if not request:
            return None  # pragma: no cover
        return RepositoryAuthorizationSerializer(
            obj.get_user_authorization(request.user)).data

    def get_examples__count(self, obj):
        return obj.examples().count()


class RepositoryAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryAuthorization
        fields = [
            'uuid',
            'user',
            'repository',
            'level',
            'can_read',
            'can_contribute',
            'can_write',
            'is_admin',
            'created_at',
        ]


class AnalyzeTextSerializer(serializers.Serializer):
    language = serializers.ChoiceField(LANGUAGE_CHOICES, required=True)
    text = serializers.CharField(allow_blank=False)
