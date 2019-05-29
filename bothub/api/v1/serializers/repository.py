from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext as _

from bothub.common.models import Repository
from bothub.common.models import RepositoryCategory
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RepositoryVote
from bothub.common.models import RequestRepositoryAuthorization
from bothub.common.languages import LANGUAGE_CHOICES

from ..fields import ModelMultipleChoiceField
from ..fields import TextField

from .category import RepositoryCategorySerializer
from .request import RequestRepositoryAuthorizationSerializer
from .example import RepositoryEntityLabelSerializer


class NewRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = [
            'uuid',
            'owner',
            'name',
            'slug',
            'language',
            'algorithm',
            'use_competing_intents',
            'use_name_entities',
            'categories',
            'description',
            'is_private',
        ]

    uuid = serializers.ReadOnlyField(
        style={'show': False})
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    language = serializers.ChoiceField(
        LANGUAGE_CHOICES,
        label=_('Language'))
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
            'algorithm',
            'use_language_model_featurizer',
            'use_competing_intents',
            'use_name_entities',
            'categories',
            'categories_list',
            'description',
            'is_private',
            'intents',
            'entities',
            'labels',
            'labels_list',
            'examples__count',
            'authorization',
            'available_request_authorization',
            'request_authorization',
            'ready_for_train',
            'requirements_to_train',
            'languages_ready_for_train',
            'languages_warnings',
            'votes_sum',
            'created_at',
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
    categories_list = serializers.SerializerMethodField()
    entities = serializers.SerializerMethodField()
    labels = RepositoryEntityLabelSerializer(many=True)
    labels_list = serializers.SerializerMethodField()
    authorization = serializers.SerializerMethodField()
    examples__count = serializers.SerializerMethodField()
    request_authorization = serializers.SerializerMethodField()
    available_request_authorization = serializers.SerializerMethodField()

    def get_categories_list(self, obj):
        return RepositoryCategorySerializer(obj.categories, many=True).data

    def get_entities(self, obj):
        return list(obj.entities_list)

    def get_labels_list(self, obj):
        return list(obj.labels_list)

    def get_authorization(self, obj):
        request = self.context.get('request')
        if not request:
            return None  # pragma: no cover
        return RepositoryAuthorizationSerializer(
            obj.get_user_authorization(request.user)).data

    def get_examples__count(self, obj):
        return obj.examples().count()

    def get_available_request_authorization(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        authorization = obj.get_user_authorization(request.user)
        if authorization.role is not RepositoryAuthorization.ROLE_NOT_SETTED:
            return False
        if authorization.is_owner:
            return False
        try:
            RequestRepositoryAuthorization.objects.get(
                user=request.user,
                repository=obj)
            return False
        except RequestRepositoryAuthorization.DoesNotExist:
            return True

    def get_request_authorization(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        try:
            request_authorization = RequestRepositoryAuthorization.objects.get(
                user=request.user,
                repository=obj)
            return RequestRepositoryAuthorizationSerializer(
                request_authorization).data
        except RequestRepositoryAuthorization.DoesNotExist:
            return None


class RepositoryAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryAuthorization
        fields = [
            'uuid',
            'user',
            'user__nickname',
            'repository',
            'role',
            'level',
            'can_read',
            'can_contribute',
            'can_write',
            'is_admin',
            'created_at',
        ]

    user__nickname = serializers.SlugRelatedField(
        source='user',
        slug_field='nickname',
        read_only=True)


class AnalyzeTextSerializer(serializers.Serializer):
    language = serializers.ChoiceField(LANGUAGE_CHOICES, required=True)
    text = serializers.CharField(allow_blank=False)


class EvaluateSerializer(serializers.Serializer):
    language = serializers.ChoiceField(LANGUAGE_CHOICES, required=True)


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryVote
        fields = [
            'vote',
        ]


class RepositoryAuthorizationRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryAuthorization
        fields = [
            'role',
        ]

    def validate(self, data):
        if self.instance.user == self.instance.repository.owner:
            raise PermissionDenied(_('The owner role can\'t be changed.'))
        return data
