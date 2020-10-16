import json

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from bothub import utils
from bothub.api.v2.example.serializers import RepositoryExampleEntitySerializer
from bothub.api.v2.fields import EntityText, RepositoryVersionRelatedField
from bothub.api.v2.fields import ModelMultipleChoiceField
from bothub.api.v2.fields import TextField
from bothub.authentication.models import RepositoryOwner
from bothub.celery import app as celery_app
from bothub.common import languages
from bothub.common.languages import LANGUAGE_CHOICES
from bothub.common.models import (
    Repository,
    RepositoryVersion,
    RepositoryNLPLog,
    RepositoryEntity,
    RepositoryEvaluate,
    RepositoryExampleEntity,
    RepositoryQueueTask,
    OrganizationAuthorization,
    Organization,
    RepositoryNLPTrain,
    RepositoryIntent,
    RepositoryTranslator,
    RepositoryScore,
)
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RepositoryCategory
from bothub.common.models import RepositoryEntityGroup
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryMigrate
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryTranslatedExampleEntity
from bothub.common.models import RepositoryVote
from bothub.common.models import RequestRepositoryAuthorization
from bothub.utils import classifier_choice
from .validators import (
    APIExceptionCustom,
    CanCreateRepositoryInOrganizationValidator,
    IntentValidator,
)
from .validators import CanContributeInRepositoryValidator
from .validators import CanContributeInRepositoryVersionValidator
from .validators import ExampleWithIntentOrEntityValidator
from ..translation.validators import (
    CanContributeInRepositoryExampleValidator,
    CanContributeInRepositoryTranslatedExampleValidator,
)


class RequestRepositoryAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestRepositoryAuthorization
        fields = [
            "id",
            "user",
            "user__nickname",
            "repository",
            "text",
            "approved_by",
            "approved_by__nickname",
            "created_at",
        ]
        ref_name = None

    id = serializers.IntegerField(
        read_only=True, required=False, label="ID", style={"show": False}
    )

    repository = serializers.PrimaryKeyRelatedField(
        queryset=Repository.objects, style={"show": False}, required=False
    )
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(), style={"show": False}
    )
    text = TextField(
        label=_("Leave a message for repository administrators"),
        min_length=5,
        max_length=RequestRepositoryAuthorization._meta.get_field("text").max_length,
        required=False,
    )
    user__nickname = serializers.SlugRelatedField(
        source="user", slug_field="nickname", read_only=True, style={"show": False}
    )
    approved_by__nickname = serializers.SlugRelatedField(
        source="approved_by",
        slug_field="nickname",
        read_only=True,
        style={"show": False},
    )
    approved_by = serializers.PrimaryKeyRelatedField(
        read_only=True, style={"show": False}, required=False
    )
    created_at = serializers.DateTimeField(
        required=False, read_only=True, style={"show": False}
    )

    def update(self, instance, validated_data):
        if "user" in validated_data:
            validated_data.pop("user")
        validated_data.update({"approved_by": self.context["request"].user})
        return super().update(instance, validated_data)


class RepositoryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryCategory
        fields = ["id", "name", "icon"]
        ref_name = None


class RepositoryEntityGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryEntityGroup
        fields = [
            "id",
            "repository_version",
            "repository",
            "value",
            "entities",
            "examples__count",
        ]
        ref_name = None

    id = serializers.PrimaryKeyRelatedField(read_only=True)
    repository = serializers.UUIDField(
        source="repository_version.repository.uuid", read_only=True
    )
    entities = serializers.SerializerMethodField()
    examples__count = serializers.SerializerMethodField()

    def get_entities(self, obj):
        entities = (
            obj.repository_version.other_entities()
            if obj.value == "other"
            else obj.entities.all()
        )
        return map(lambda e: e.value, entities)

    def get_examples__count(self, obj):
        if obj.value == "other":
            return (
                obj.repository.examples()
                .filter(entities__entity__in=obj.repository_version.other_entities())
                .count()
            )
        return obj.examples().count()


class IntentSerializer(serializers.Serializer):
    value = serializers.CharField()
    id = serializers.IntegerField()
    examples__count = serializers.IntegerField()


class RepositoryAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryAuthorization
        fields = [
            "uuid",
            "user",
            "user__nickname",
            "repository",
            "role",
            "level",
            "can_read",
            "can_contribute",
            "can_write",
            "can_translate",
            "is_admin",
            "created_at",
            "id_request_authorizations",
            "user__is_organization",
        ]
        read_only = ["user", "user__nickname", "repository", "role", "created_at"]
        ref_name = None

    user__nickname = serializers.SlugRelatedField(
        source="user", slug_field="nickname", read_only=True
    )
    user__is_organization = serializers.SlugRelatedField(
        source="user", slug_field="is_organization", read_only=True
    )

    id_request_authorizations = serializers.SerializerMethodField()

    def get_id_request_authorizations(self, obj):
        id_auth = RequestRepositoryAuthorization.objects.filter(
            repository=obj.repository, user=obj.user
        )
        if id_auth.count() == 1:
            return id_auth.first().pk
        return None


class RepositoryTranslatorInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryTranslator
        fields = [
            "repository_version_id",
            "uuid",
            "name",
            "slug",
            "description",
            "is_private",
            "entities",
            "groups_list",
            "created_at",
            "language",
            "owner",
            "categories",
            "categories_list",
            "intents",
            "intents_list",
            "groups",
            "other_group",
            "examples__count",
            "absolute_url",
            "target_language",
        ]
        read_only = fields
        ref_name = None

    repository_version_id = serializers.PrimaryKeyRelatedField(
        read_only=True,
        style={"show": False},
        source="repository_version_language.repository_version.pk",
    )
    uuid = serializers.UUIDField(
        style={"show": False},
        read_only=True,
        source="repository_version_language.repository_version.repository.uuid",
    )
    name = serializers.CharField(
        style={"show": False},
        read_only=True,
        source="repository_version_language.repository_version.repository.name",
    )
    slug = serializers.SlugField(
        style={"show": False},
        read_only=True,
        source="repository_version_language.repository_version.repository.slug",
    )
    description = serializers.CharField(
        style={"show": False},
        read_only=True,
        source="repository_version_language.repository_version.repository.description",
    )
    is_private = serializers.BooleanField(
        style={"show": False},
        read_only=True,
        source="repository_version_language.repository_version.repository.is_private",
    )
    entities = serializers.SerializerMethodField(style={"show": False})
    groups_list = serializers.SerializerMethodField(style={"show": False})
    language = serializers.ChoiceField(
        LANGUAGE_CHOICES,
        label=_("Language"),
        source="repository_version_language.repository_version.repository.language",
    )
    owner = serializers.SerializerMethodField(style={"show": False})
    intents = serializers.SerializerMethodField(style={"show": False})
    intents_list = serializers.SerializerMethodField(style={"show": False})
    categories = ModelMultipleChoiceField(
        child_relation=serializers.PrimaryKeyRelatedField(
            queryset=RepositoryCategory.objects.all()
        ),
        allow_empty=False,
        help_text=Repository.CATEGORIES_HELP_TEXT,
        label=_("Categories"),
        source="repository_version_language.repository_version.repository.categories",
    )
    categories_list = serializers.SerializerMethodField(style={"show": False})
    groups = serializers.SerializerMethodField(style={"show": False})
    other_group = serializers.SerializerMethodField(style={"show": False})
    examples__count = serializers.SerializerMethodField(style={"show": False})
    absolute_url = serializers.SerializerMethodField(style={"show": False})
    target_language = serializers.ChoiceField(
        LANGUAGE_CHOICES, label=_("Language"), source="language"
    )

    def get_entities(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj.repository_version_language.repository_version
        )
        return (
            obj.repository_version_language.repository_version.current_entities(
                queryset=queryset,
                version_default=obj.repository_version_language.repository_version.is_default,
            )
            .values("value", "id")
            .distinct()
        )

    def get_groups_list(self, obj):
        return (
            obj.repository_version_language.repository_version.groups.distinct()
            .values_list("value", flat=True)
            .distinct()
        )

    def get_owner(self, obj):
        return {
            "id": obj.repository_version_language.repository_version.repository.owner.pk,
            "nickname": obj.repository_version_language.repository_version.repository.owner.nickname,
        }

    def get_intents(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj.repository_version_language.repository_version
        )

        return IntentSerializer(
            map(
                lambda intent: {
                    "value": intent.text,
                    "id": intent.pk,
                    "examples__count": obj.repository_version_language.repository_version.repository.examples(
                        queryset=queryset,
                        version_default=obj.repository_version_language.repository_version.is_default,
                    )
                    .filter(intent=intent)
                    .count(),
                },
                obj.repository_version_language.repository_version.version_intents.all(),
            ),
            many=True,
        ).data

    def get_intents_list(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj.repository_version_language.repository_version
        )
        return obj.repository_version_language.repository_version.repository.intents(
            queryset=queryset,
            version_default=obj.repository_version_language.repository_version.is_default,
        )

    def get_categories_list(self, obj):
        return RepositoryCategorySerializer(
            obj.repository_version_language.repository_version.repository.categories,
            many=True,
        ).data

    def get_groups(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj.repository_version_language.repository_version
        )

        current_groups = (
            obj.repository_version_language.repository_version.groups.distinct()
        )

        return list(
            map(
                lambda group: {
                    "repository": group.repository_version.repository.pk,
                    "value": group.value,
                    "group_id": group.pk,
                    "entities": list(
                        map(
                            lambda e: {"entity_id": e.pk, "value": e.value},
                            group.other_entities(
                                queryset=queryset,
                                version_default=obj.repository_version_language.repository_version.is_default,
                            )
                            if group.value == "other"
                            else group.entities.all(),
                        )
                    ),
                    "examples__count": (
                        group.repository.examples(
                            queryset=queryset,
                            version_default=obj.repository_version_language.repository_version.is_default,
                        )
                        .filter(entities__entity__in=group.other_entities())
                        .count()
                    )
                    if group.value == "other"
                    else group.examples(
                        queryset=queryset,
                        version_default=obj.repository_version_language.repository_version.is_default,
                    ).count(),
                },
                current_groups,
            )
        )

    def get_other_group(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj.repository_version_language.repository_version
        )

        group = obj.repository_version_language.repository_version.other_entities(
            queryset=queryset,
            version_default=obj.repository_version_language.repository_version.is_default,
        )

        return {
            "repository": obj.repository_version_language.repository_version.repository.pk,
            "value": "other",
            "entities": list(
                map(lambda e: {"entity_id": e.pk, "value": e.value}, group)
            ),
            "examples__count": (
                obj.repository_version_language.repository_version.repository.examples(
                    queryset=queryset,
                    version_default=obj.repository_version_language.repository_version.is_default,
                )
                .filter(entities__entity__in=group)
                .count()
            ),
        }

    def get_examples__count(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj.repository_version_language.repository_version
        )
        return obj.repository_version_language.repository_version.repository.examples(
            queryset=queryset,
            version_default=obj.repository_version_language.repository_version.is_default,
        ).count()

    def get_absolute_url(self, obj):
        return (
            obj.repository_version_language.repository_version.repository.get_absolute_url()
        )


class NewRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryVersion
        fields = [
            "repository_version_id",
            "uuid",
            "name",
            "slug",
            "description",
            "is_private",
            "available_languages",
            "entities",
            "groups_list",
            "ready_for_train",
            "requirements_to_train",
            "created_at",
            "language",
            "owner",
            "categories",
            "categories_list",
            "intents",
            "intents_list",
            "groups",
            "other_group",
            "examples__count",
            "evaluate_languages_count",
            "absolute_url",
            "authorization",
            "request_authorization",
            "available_request_authorization",
            "languages_warnings",
            "algorithm",
            "use_language_model_featurizer",
            "use_competing_intents",
            "use_name_entities",
            "use_analyze_char",
            "nlp_server",
            "version_default",
            "is_organization",
            "authorizations",
            "ready_for_parse",
            "count_authorizations",
            "repository_score",
        ]
        read_only = [
            "uuid",
            "available_languages",
            "available_languages_count",
            "languages_warnings_count",
            "entities",
            "entities_list",
            "evaluate_languages_count",
            "groups_list",
            "ready_for_train",
            "created_at",
            "authorization",
            "nlp_server",
            "is_organization",
            "ready_for_parse",
            "count_authorizations",
        ]
        ref_name = None

    repository_version_id = serializers.PrimaryKeyRelatedField(
        read_only=True, style={"show": False}, source="pk"
    )

    uuid = serializers.UUIDField(
        style={"show": False}, read_only=True, source="repository.uuid"
    )
    name = serializers.CharField(
        style={"show": False}, read_only=True, source="repository.name"
    )
    slug = serializers.SlugField(
        style={"show": False}, read_only=True, source="repository.slug"
    )
    description = serializers.CharField(
        style={"show": False}, read_only=True, source="repository.description"
    )
    is_private = serializers.BooleanField(
        style={"show": False}, read_only=True, source="repository.is_private"
    )
    available_languages = serializers.SerializerMethodField(style={"show": False})
    entities = serializers.SerializerMethodField(style={"show": False})
    groups_list = serializers.SerializerMethodField(style={"show": False})
    ready_for_train = serializers.SerializerMethodField(style={"show": False})
    requirements_to_train = serializers.SerializerMethodField(style={"show": False})
    created_at = serializers.DateTimeField(
        style={"show": False}, read_only=True, source="repository.created_at"
    )
    language = serializers.ChoiceField(
        LANGUAGE_CHOICES, label=_("Language"), source="repository.language"
    )
    owner = serializers.SerializerMethodField(style={"show": False})
    intents = serializers.SerializerMethodField(style={"show": False})
    intents_list = serializers.SerializerMethodField(style={"show": False})
    categories = ModelMultipleChoiceField(
        child_relation=serializers.PrimaryKeyRelatedField(
            queryset=RepositoryCategory.objects.all()
        ),
        allow_empty=False,
        help_text=Repository.CATEGORIES_HELP_TEXT,
        label=_("Categories"),
        source="repository.categories",
    )
    categories_list = serializers.SerializerMethodField(style={"show": False})
    groups = serializers.SerializerMethodField(style={"show": False})
    other_group = serializers.SerializerMethodField(style={"show": False})
    examples__count = serializers.SerializerMethodField(style={"show": False})
    evaluate_languages_count = serializers.SerializerMethodField(style={"show": False})
    absolute_url = serializers.SerializerMethodField(style={"show": False})
    authorization = serializers.SerializerMethodField(style={"show": False})
    request_authorization = serializers.SerializerMethodField(style={"show": False})
    available_request_authorization = serializers.SerializerMethodField(
        style={"show": False}
    )
    languages_warnings = serializers.SerializerMethodField(style={"show": False})
    algorithm = serializers.ChoiceField(
        style={"show": False, "only_settings": True},
        choices=Repository.ALGORITHM_CHOICES,
        default=Repository.ALGORITHM_TRANSFORMER_NETWORK_DIET,
        label=_("Algorithm"),
        source="repository.algorithm",
    )
    use_language_model_featurizer = serializers.ReadOnlyField(
        style={"show": False}, source="repository.use_language_model_featurizer"
    )
    use_competing_intents = serializers.BooleanField(
        style={"show": False, "only_settings": True},
        help_text=_(
            "When using competing intents the confidence of the "
            + "prediction is distributed in all the intents."
        ),
        default=False,
        label=_("Use competing intents"),
        source="repository.use_competing_intents",
    )
    use_name_entities = serializers.BooleanField(
        style={"show": False, "only_settings": True},
        help_text=_(
            "When enabling name entities you will receive name of "
            + "people, companies and places as results of your "
            + "predictions."
        ),
        default=False,
        label=_("Use name entities"),
        source="repository.use_name_entities",
    )
    use_analyze_char = serializers.BooleanField(
        style={"show": False, "only_settings": True},
        help_text=_(
            "When selected, the algorithm will learn the patterns of "
            + "individual characters instead of whole words. "
            + "This approach works better for some languages."
        ),
        default=False,
        label=_("Use analyze char"),
        source="repository.use_analyze_char",
    )
    nlp_server = serializers.SerializerMethodField(style={"show": False})
    version_default = serializers.SerializerMethodField(style={"show": False})
    is_organization = serializers.BooleanField(
        source="repository.owner.is_organization"
    )
    authorizations = serializers.SerializerMethodField(style={"show": False})
    ready_for_parse = serializers.SerializerMethodField(style={"show": False})
    count_authorizations = serializers.IntegerField(
        style={"show": False}, read_only=True, source="repository.count_authorizations"
    )
    repository_score = serializers.SerializerMethodField(style={"show": False})

    def get_authorizations(self, obj):
        auths = RepositoryAuthorization.objects.filter(
            repository=obj.repository
        ).exclude(role=RepositoryAuthorization.ROLE_NOT_SETTED)
        return {
            "count": auths.count(),
            "users": [
                {"nickname": i.user.nickname, "name": i.user.name} for i in auths
            ],
        }

    def get_ready_for_parse(self, obj):
        q = (
            RepositoryNLPTrain.objects.filter(
                repositoryversionlanguage__repository_version=obj
            )
            .exclude(bot_data__isnull=True)
            .exclude(bot_data__exact="")
        )
        return True if q.count() > 0 else False

    def get_available_languages(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )
        return obj.repository.available_languages(
            queryset=queryset, version_default=obj.is_default
        )

    def get_entities(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )
        return (
            obj.current_entities(queryset=queryset, version_default=obj.is_default)
            .values("value", "id")
            .distinct()
        )

    def get_groups_list(self, obj):
        return obj.groups.distinct().values_list("value", flat=True).distinct()

    def get_ready_for_train(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )
        return obj.repository.ready_for_train(
            queryset=queryset, repository_version=obj.pk
        )

    def get_requirements_to_train(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )
        return dict(
            filter(
                lambda l: l[1],
                map(
                    lambda u: (u.language, u.requirements_to_train),
                    obj.repository.current_versions(
                        queryset=queryset,
                        repository_version=obj.pk,
                        version_default=obj.is_default,
                    ),
                ),
            )
        )

    def get_owner(self, obj):
        return {
            "id": obj.repository.owner.pk,
            "nickname": obj.repository.owner.nickname,
        }

    def get_intents(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )

        return IntentSerializer(
            map(
                lambda intent: {
                    "value": intent.text,
                    "id": intent.pk,
                    "examples__count": obj.repository.examples(
                        queryset=queryset, version_default=obj.is_default
                    )
                    .filter(intent=intent)
                    .count(),
                },
                obj.version_intents.all(),
            ),
            many=True,
        ).data

    def get_intents_list(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )
        return obj.repository.intents(queryset=queryset, version_default=obj.is_default)

    def get_categories_list(self, obj):
        return RepositoryCategorySerializer(obj.repository.categories, many=True).data

    def get_groups(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )

        current_groups = obj.groups.distinct()

        return list(
            map(
                lambda group: {
                    "repository": group.repository_version.repository.pk,
                    "value": group.value,
                    "group_id": group.pk,
                    "entities": list(
                        map(
                            lambda e: {"entity_id": e.pk, "value": e.value},
                            group.other_entities(
                                queryset=queryset, version_default=obj.is_default
                            )
                            if group.value == "other"
                            else group.entities.all(),
                        )
                    ),
                    "examples__count": (
                        group.repository.examples(
                            queryset=queryset, version_default=obj.is_default
                        )
                        .filter(entities__entity__in=group.other_entities())
                        .count()
                    )
                    if group.value == "other"
                    else group.examples(
                        queryset=queryset, version_default=obj.is_default
                    ).count(),
                },
                current_groups,
            )
        )

    def get_other_group(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )

        group = obj.other_entities(queryset=queryset, version_default=obj.is_default)

        return {
            "repository": obj.repository.pk,
            "value": "other",
            "entities": list(
                map(lambda e: {"entity_id": e.pk, "value": e.value}, group)
            ),
            "examples__count": (
                obj.repository.examples(
                    queryset=queryset, version_default=obj.is_default
                )
                .filter(entities__entity__in=group)
                .count()
            ),
        }

    def get_examples__count(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )
        return obj.repository.examples(
            queryset=queryset, version_default=obj.is_default
        ).count()

    def get_evaluate_languages_count(self, obj):
        queryset = RepositoryEvaluate.objects.filter(
            repository_version_language__repository_version=obj
        )
        return dict(
            map(
                lambda x: (
                    x,
                    obj.repository.evaluations(
                        language=x, queryset=queryset, version_default=obj.is_default
                    ).count(),
                ),
                obj.repository.available_languages(
                    queryset=RepositoryExample.objects.filter(
                        repository_version_language__repository_version=obj
                    ),
                    version_default=obj.is_default,
                ),
            )
        )

    def get_absolute_url(self, obj):
        return obj.repository.get_absolute_url()

    def get_authorization(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        data = RepositoryAuthorizationSerializer(
            obj.repository.get_user_authorization(request.user)
        ).data

        data.update(
            {
                "organizations": list(
                    map(
                        lambda auth: RepositoryAuthorizationSerializer(
                            obj.repository.get_user_authorization(auth.organization)
                        ).data,
                        OrganizationAuthorization.objects.exclude(
                            role=OrganizationAuthorization.ROLE_NOT_SETTED
                        ).filter(user=request.user),
                    )
                )
            }
        )
        return data

    def get_request_authorization(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        try:
            request_authorization = RequestRepositoryAuthorization.objects.get(
                user=request.user, repository=obj.repository
            )
            return RequestRepositoryAuthorizationSerializer(request_authorization).data
        except RequestRepositoryAuthorization.DoesNotExist:
            return None

    def get_available_request_authorization(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        authorization = obj.repository.get_user_authorization(request.user)
        if authorization.role is not RepositoryAuthorization.ROLE_NOT_SETTED:
            return False
        if authorization.is_owner:
            return False

        organization = Organization.objects.filter(
            repository_owner=obj.repository.owner
        )
        if organization:
            organization = organization.first()
            org_authorization = organization.get_organization_authorization(
                request.user
            )
            if not org_authorization.role == OrganizationAuthorization.ROLE_NOT_SETTED:
                return False

        try:
            RequestRepositoryAuthorization.objects.get(
                user=request.user.user, repository=obj.repository
            )
            return False
        except RequestRepositoryAuthorization.DoesNotExist:
            return True

    def get_languages_warnings(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )

        return dict(
            filter(
                lambda w: len(w[1]) > 0,
                map(
                    lambda u: (u.language, u.warnings),
                    obj.repository.current_versions(
                        queryset=queryset,
                        version_default=obj.is_default,
                        repository_version=obj.pk,
                    ),
                ),
            )
        )

    def get_nlp_server(self, obj):
        if obj.repository.nlp_server:
            return obj.repository.nlp_server
        return settings.BOTHUB_NLP_BASE_URL

    def get_version_default(self, obj):
        return {
            "id": obj.repository.current_version().repository_version.pk,
            "name": obj.repository.current_version().repository_version.name,
        }

    def get_repository_score(self, obj):
        score, created = obj.repository.repository_score.get_or_create()
        return RepositoryScoreSerializer(score).data


class RepositoryTrainInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryVersion
        fields = [
            "repository_version_id",
            "uuid",
            "ready_for_train",
            "requirements_to_train",
            "languages_warnings",
        ]
        read_only = fields
        ref_name = None

    repository_version_id = serializers.PrimaryKeyRelatedField(
        read_only=True, style={"show": False}, source="pk"
    )

    uuid = serializers.UUIDField(
        style={"show": False}, read_only=True, source="repository.uuid"
    )
    ready_for_train = serializers.SerializerMethodField(style={"show": False})
    requirements_to_train = serializers.SerializerMethodField(style={"show": False})
    languages_warnings = serializers.SerializerMethodField(style={"show": False})

    def get_ready_for_train(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )
        return obj.repository.ready_for_train(
            queryset=queryset, repository_version=obj.pk
        )

    def get_requirements_to_train(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )
        return dict(
            filter(
                lambda l: l[1],
                map(
                    lambda u: (u.language, u.requirements_to_train),
                    obj.repository.current_versions(
                        queryset=queryset,
                        repository_version=obj.pk,
                        version_default=obj.is_default,
                    ),
                ),
            )
        )

    def get_languages_warnings(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )

        return dict(
            filter(
                lambda w: len(w[1]) > 0,
                map(
                    lambda u: (u.language, u.warnings),
                    obj.repository.current_versions(
                        queryset=queryset,
                        version_default=obj.is_default,
                        repository_version=obj.pk,
                    ),
                ),
            )
        )


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = [
            "uuid",
            "name",
            "slug",
            "description",
            "is_private",
            "created_at",
            "language",
            "owner",
            "owner__nickname",
            "categories",
            "categories_list",
            "algorithm",
            "use_competing_intents",
            "use_name_entities",
            "use_analyze_char",
            "organization",
        ]
        read_only = ["uuid", "created_at"]
        ref_name = None

    uuid = serializers.UUIDField(style={"show": False}, read_only=True)
    slug = serializers.SlugField(style={"show": False}, read_only=True)
    algorithm = serializers.ChoiceField(
        style={"show": False, "only_settings": True},
        choices=Repository.ALGORITHM_CHOICES,
        default=Repository.ALGORITHM_TRANSFORMER_NETWORK_DIET_BERT,
        label=_("Algorithm"),
    )
    use_competing_intents = serializers.BooleanField(
        style={"show": False, "only_settings": True},
        help_text=_(
            "When using competing intents the confidence of the "
            + "prediction is distributed in all the intents."
        ),
        default=False,
        label=_("Use competing intents"),
    )
    use_name_entities = serializers.BooleanField(
        style={"show": False, "only_settings": True},
        help_text=_(
            "When enabling name entities you will receive name of "
            + "people, companies and places as results of your "
            + "predictions."
        ),
        default=False,
        label=_("Use name entities"),
    )
    use_analyze_char = serializers.BooleanField(
        style={"show": False, "only_settings": True},
        help_text=_(
            "When selected, the algorithm will learn the patterns of "
            + "individual characters instead of whole words. "
            + "This approach works better for some languages."
        ),
        default=False,
        label=_("Use analyze char"),
    )
    created_at = serializers.DateTimeField(style={"show": False}, read_only=True)

    language = serializers.ChoiceField(LANGUAGE_CHOICES, label=_("Language"))
    owner = serializers.PrimaryKeyRelatedField(style={"show": False}, read_only=True)
    owner__nickname = serializers.SlugRelatedField(
        source="owner", slug_field="nickname", read_only=True, style={"show": False}
    )
    categories = ModelMultipleChoiceField(
        child_relation=serializers.PrimaryKeyRelatedField(
            queryset=RepositoryCategory.objects.all()
        ),
        allow_empty=False,
        help_text=Repository.CATEGORIES_HELP_TEXT,
        label=_("Categories"),
    )
    organization = serializers.IntegerField(
        required=False,
        help_text="Specify the organization id",
        validators=[CanCreateRepositoryInOrganizationValidator()],
        style={"show": False},
    )
    categories_list = serializers.SerializerMethodField(style={"show": False})

    def create(self, validated_data):
        organization = validated_data.pop("organization", None)

        if organization:
            owner = get_object_or_404(RepositoryOwner, pk=organization)
            validated_data.update({"owner": owner})
        else:
            validated_data.update({"owner": self.context["request"].user})
            owner = self.context["request"].user

        validated_data.update(
            {"slug": utils.unique_slug_generator(validated_data, Repository)}
        )

        repository = super().create(validated_data)

        if owner.is_organization:
            repository.authorizations.create(
                user=owner, role=RepositoryAuthorization.ROLE_ADMIN
            )

        repository.versions.create(
            is_default=True, created_by=self.context["request"].user
        )

        return repository

    def get_categories_list(self, obj):
        return RepositoryCategorySerializer(obj.categories, many=True).data


class RepositoryPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryAuthorization
        fields = [
            "uuid",
            "name",
            "slug",
            "role",
            "created_at",
            "language",
            "owner",
            "owner__nickname",
            "categories",
            "categories_list",
        ]
        ref_name = None

    uuid = serializers.UUIDField(
        style={"show": False}, read_only=True, source="repository.uuid"
    )
    name = serializers.CharField(source="repository.name")
    slug = serializers.SlugField(
        style={"show": False}, read_only=True, source="repository.slug"
    )
    created_at = serializers.DateTimeField(
        style={"show": False}, read_only=True, source="repository.created_at"
    )
    language = serializers.ChoiceField(
        LANGUAGE_CHOICES, label=_("Language"), source="repository.language"
    )
    owner = serializers.PrimaryKeyRelatedField(
        style={"show": False}, read_only=True, source="repository.owner"
    )
    owner__nickname = serializers.SlugRelatedField(
        source="repository.owner",
        slug_field="nickname",
        read_only=True,
        style={"show": False},
    )
    categories = ModelMultipleChoiceField(
        child_relation=serializers.PrimaryKeyRelatedField(
            queryset=RepositoryCategory.objects.all()
        ),
        allow_empty=False,
        help_text=Repository.CATEGORIES_HELP_TEXT,
        label=_("Categories"),
        source="repository.categories",
    )
    categories_list = serializers.SerializerMethodField(style={"show": False})

    def get_categories_list(self, obj):
        return RepositoryCategorySerializer(obj.repository.categories, many=True).data


class RepositoryVotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryVote
        fields = ["user", "repository", "created"]

        read_only_fields = ["user", "created_at"]
        ref_name = None

    def create(self, validated_data):
        user = self.context.get("request").user
        repository = validated_data.pop("repository")
        vote, created = RepositoryVote.objects.get_or_create(
            repository=repository, user=user
        )
        return vote


class ShortRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = [
            "uuid",
            "name",
            "slug",
            "description",
            "is_private",
            "categories",
            "categories_list",
            "language",
            "available_languages",
            "created_at",
            "owner",
            "owner__nickname",
            "absolute_url",
            "votes",
        ]
        read_only = fields
        ref_name = None

    categories = RepositoryCategorySerializer(many=True, read_only=True)
    categories_list = serializers.SlugRelatedField(
        source="categories", slug_field="name", many=True, read_only=True
    )
    owner__nickname = serializers.SlugRelatedField(
        source="owner", slug_field="nickname", read_only=True
    )
    absolute_url = serializers.SerializerMethodField()

    votes = RepositoryVotesSerializer(many=True, read_only=True)

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()


class RepositoryContributionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryAuthorization
        fields = ["user", "repository", "role", "created_at"]

        read_only_fields = ["user", "role", "created_at"]
        ref_name = None


class RepositoryAuthorizationRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryAuthorization
        fields = ["role"]
        ref_name = None

    def validate(self, data):
        if self.instance.user == self.instance.repository.owner:
            raise PermissionDenied(_("The owner role can't be changed."))
        if data.get("role") == RepositoryAuthorization.LEVEL_NOTHING:
            raise PermissionDenied(_("You cannot set user role 0"))
        return data


class RepositoryTranslatedExampleEntitySeralizer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryTranslatedExampleEntity
        fields = [
            "id",
            "repository_translated_example",
            "start",
            "end",
            "entity",
            "created_at",
            "value",
        ]
        ref_name = None

    repository_translated_example = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryTranslatedExample.objects,
        validators=[CanContributeInRepositoryTranslatedExampleValidator()],
        help_text="Example translation ID",
    )
    entity = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()

    def get_entity(self, obj):
        return obj.entity.value

    def get_value(self, obj):
        return obj.value


class RepositoryTranslatedExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryTranslatedExample
        fields = [
            "id",
            "original_example",
            "from_language",
            "language",
            "text",
            "has_valid_entities",
            "entities",
            "created_at",
        ]
        ref_name = None

    original_example = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryExample.objects,
        validators=[CanContributeInRepositoryExampleValidator()],
        help_text=_("Example's ID"),
    )
    from_language = serializers.SerializerMethodField()
    has_valid_entities = serializers.SerializerMethodField()
    entities = RepositoryTranslatedExampleEntitySeralizer(many=True, read_only=True)

    def get_from_language(self, obj):
        return obj.original_example.repository_version_language.language

    def get_has_valid_entities(self, obj):
        return obj.has_valid_entities


class RepositoryExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryExample
        fields = [
            "id",
            "repository",
            "text",
            "intent",
            "is_corrected",
            "language",
            "created_at",
            "entities",
            "translations",
            "repository_version",
        ]
        read_only_fields = []
        ref_name = None

    id = serializers.PrimaryKeyRelatedField(read_only=True, style={"show": False})
    text = EntityText(style={"entities_field": "entities"}, required=False)
    repository = serializers.PrimaryKeyRelatedField(
        queryset=Repository.objects,
        validators=[CanContributeInRepositoryValidator()],
        write_only=True,
        style={"show": False},
    )
    language = serializers.ChoiceField(
        languages.LANGUAGE_CHOICES, allow_blank=True, required=False
    )

    entities = RepositoryExampleEntitySerializer(
        many=True, style={"text_field": "text"}, required=True
    )
    translations = RepositoryTranslatedExampleSerializer(many=True, read_only=True)
    repository_version = RepositoryVersionRelatedField(
        source="repository_version_language",
        queryset=RepositoryVersion.objects,
        style={"show": False},
        required=True,
        validators=[CanContributeInRepositoryVersionValidator()],
    )
    intent = serializers.CharField(required=True, validators=[IntentValidator()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs["context"].get("request").stream is None:
            self.fields["entities"] = RepositoryExampleEntitySerializer(
                many=True, style={"text_field": "text"}, data="GET"
            )
        self.validators.append(ExampleWithIntentOrEntityValidator())

    def create(self, validated_data):
        entities_data = validated_data.pop("entities")
        repository = validated_data.pop("repository")
        version_id = validated_data.get("repository_version_language")
        intent_text = validated_data.get("intent")

        try:
            language = validated_data.pop("language")
        except KeyError:
            language = None

        if version_id:
            repository_version_language = repository.get_specific_version_id(
                repository_version=version_id.pk, language=language or None
            )
            validated_data.pop("repository_version_language")

            if RepositoryExample.objects.filter(
                text=validated_data.get("text"),
                intent__text=validated_data.get("intent"),
                repository_version_language__repository_version__repository=repository,
                repository_version_language__repository_version=version_id,
                repository_version_language__language=language,
            ):
                raise APIExceptionCustom(
                    detail=_("Intention and Sentence already exists")
                )
        else:
            repository_version_language = repository.current_version(language or None)

            if RepositoryExample.objects.filter(
                text=validated_data.get("text"),
                intent__text=validated_data.get("intent"),
                repository_version_language=repository_version_language,
                repository_version_language__repository_version__is_default=True,
                repository_version_language__language=language,
            ):
                raise APIExceptionCustom(
                    detail=_("Intention and Sentence already exists")
                )

        validated_data.update(
            {"repository_version_language": repository_version_language}
        )
        intent, created = RepositoryIntent.objects.get_or_create(
            repository_version=version_id, text=intent_text
        )
        validated_data.update({"intent": intent})
        example = self.Meta.model.objects.create(**validated_data)
        for entity_data in entities_data:
            entity_data.update({"repository_example": example.pk})
            entity_serializer = RepositoryExampleEntitySerializer(data=entity_data)
            entity_serializer.is_valid(raise_exception=True)
            entity_serializer.save()
        return example

    def update(self, instance, validated_data):
        entities_data = validated_data.pop("entities")
        validated_data.pop("repository")
        validated_data.pop("repository_version_language")
        validated_data.pop("language", None)
        intent_text = validated_data.get("intent", None)

        if intent_text:
            intent, created = RepositoryIntent.objects.get_or_create(
                repository_version=instance.repository_version_language.repository_version,
                text=intent_text,
            )
            validated_data.update({"intent": intent})

        instance_update = super().update(instance, validated_data)

        RepositoryExampleEntity.objects.filter(repository_example=instance.pk).delete()

        for entity_data in entities_data:
            entity_data.update({"repository_example": instance.pk})
            entity_serializer = RepositoryExampleEntitySerializer(data=entity_data)
            entity_serializer.is_valid(raise_exception=True)
            entity_serializer.save()
        return instance_update


class RepositoryMigrateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryMigrate
        fields = [
            "user",
            "repository_version",
            "auth_token",
            "language",
            "classifier",
            "created",
        ]

        read_only_fields = ["user", "created_at"]

    repository_version = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryVersion.objects,
        style={"show": False},
        required=True,
        validators=[CanContributeInRepositoryVersionValidator()],
    )
    language = serializers.ChoiceField(LANGUAGE_CHOICES, label=_("Language"))
    classifier = serializers.ChoiceField(classifier_choice(), label=_("Classifier"))

    def create(self, validated_data):
        validated_data.update({"user": self.context.get("request").user})
        repository_version = validated_data.get("repository_version")
        auth_token = validated_data.get("auth_token")
        language = validated_data.get("language")
        classifier = validated_data.get("classifier")

        instance = super().create(validated_data)

        celery_app.send_task(
            "migrate_repository",
            args=[repository_version.pk, auth_token, language, classifier],
        )
        return instance


class AnalyzeTextSerializer(serializers.Serializer):
    language = serializers.ChoiceField(LANGUAGE_CHOICES, required=True)
    text = serializers.CharField(allow_blank=False)
    repository_version = serializers.IntegerField(required=False)


class DebugParseSerializer(serializers.Serializer):
    language = serializers.ChoiceField(LANGUAGE_CHOICES, required=True)
    text = serializers.CharField(allow_blank=False)
    repository_version = serializers.IntegerField(required=False)


class WordDistributionSerializer(serializers.Serializer):
    language = serializers.ChoiceField(LANGUAGE_CHOICES, required=True)
    repository_version = serializers.IntegerField(required=False)


class TrainSerializer(serializers.Serializer):
    repository_version = serializers.IntegerField(required=False)


class EvaluateSerializer(serializers.Serializer):
    language = serializers.ChoiceField(LANGUAGE_CHOICES, required=True)
    repository_version = serializers.IntegerField(required=False)


class RepositoryAutoTranslationSerializer(serializers.Serializer):
    target_language = serializers.ChoiceField(LANGUAGE_CHOICES, required=True)


class RepositoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryVersion
        fields = [
            "id",
            "repository",
            "created_at",
            "created_by",
            "created_by__nickname",
        ]
        ref_name = None

    created_by__nickname = serializers.SlugRelatedField(
        source="by", slug_field="nickname", read_only=True
    )


class RepositoryUpload(serializers.Serializer):
    pass


class RepositoryNLPLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryNLPLog
        fields = [
            "id",
            "version_name",
            "text",
            "from_backend",
            "user_agent",
            "nlp_log",
            "user",
            "log_intent",
            "created_at",
        ]
        ref_name = None

    log_intent = serializers.SerializerMethodField()
    nlp_log = serializers.SerializerMethodField()
    version_name = serializers.SerializerMethodField()

    def get_log_intent(self, obj):
        intents = {}
        for intent in obj.intents(obj):
            intents[intent.pk] = {
                "intent": intent.intent,
                "confidence": intent.confidence,
                "is_default": intent.is_default,
            }

        return intents

    def get_nlp_log(self, obj):
        return json.loads(obj.nlp_log)

    def get_version_name(self, obj):
        return obj.repository_version_language.repository_version.name


class RepositoryEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryEntity
        fields = ["id", "repository_version", "value", "group_id", "group"]
        ref_name = None

    id = serializers.PrimaryKeyRelatedField(read_only=True)
    group_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text=_("Allows you to define a group for a specific entity"),
    )
    group = RepositoryEntityGroupSerializer(many=False, read_only=True)

    def update(self, instance, validated_data):
        group_id = validated_data.get("group_id", False)
        repository_version = validated_data.get("repository_version")
        if group_id or group_id is None:
            if group_id is None:
                instance.group = None
            else:
                instance.group = get_object_or_404(
                    RepositoryEntityGroup,
                    pk=group_id,
                    repository_version=repository_version,
                )
            instance.save(update_fields=["group"])
            validated_data.pop("group_id")

        return super().update(instance, validated_data)


class RasaUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    language = serializers.ChoiceField(LANGUAGE_CHOICES, label=_("Language"))


class ObjectRasaSerializer(serializers.Serializer):
    regex_features = serializers.ListField(required=True)
    entity_synonyms = serializers.ListField(required=True)
    common_examples = serializers.ListField(required=True)


class RasaSerializer(serializers.Serializer):
    rasa_nlu_data = ObjectRasaSerializer()


class RepositoryQueueTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryQueueTask
        fields = [
            "id",
            "id_queue",
            "from_queue",
            "status",
            "ml_units",
            "created_at",
            "end_training",
            "status_codes",
            "from_queue_codes",
            "from_queue_codes",
            "type_processing",
            "processing_codes",
        ]
        ref_name = None

    id = serializers.PrimaryKeyRelatedField(read_only=True)
    status_codes = serializers.SerializerMethodField()
    from_queue_codes = serializers.SerializerMethodField()
    processing_codes = serializers.SerializerMethodField()

    def get_status_codes(self, obj):
        return {key: value for key, value in RepositoryQueueTask.STATUS_CHOICES}

    def get_from_queue_codes(self, obj):
        return {key: value for key, value in RepositoryQueueTask.QUEUE_CHOICES}

    def get_processing_codes(self, obj):
        return {
            key: value for key, value in RepositoryQueueTask.TYPE_PROCESSING_CHOICES
        }


class RepositoryNLPLogReportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = [
            "uuid",
            "name",
            "slug",
            "description",
            "is_private",
            "owner",
            "total_count",
        ]
        ref_name = None

    uuid = serializers.UUIDField(style={"show": False}, read_only=True)
    name = serializers.CharField(style={"show": False}, read_only=True)
    slug = serializers.SlugField(style={"show": False}, read_only=True)
    description = serializers.CharField(style={"show": False}, read_only=True)
    is_private = serializers.BooleanField(style={"show": False}, read_only=True)
    total_count = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    def get_total_count(self, obj):
        return obj.total_count

    def get_owner(self, obj):
        return {"id": obj.owner.pk, "nickname": obj.owner.nickname}


class RepositoryIntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryIntent
        fields = ["id", "repository_version", "text", "created_at"]
        read_only_fields = ["repository_version", "created_at"]
        ref_name = None

    text = serializers.CharField(required=True, validators=[IntentValidator()])


class RepositoryScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryScore
        fields = [
            "intents_balance_score",
            "intents_balance_recommended",
            "intents_size_score",
            "intents_size_recommended",
            "evaluate_size_score",
            "evaluate_size_recommended",
        ]


class ExampleSuggestionSerializer(serializers.Serializer):
    suggestions = serializers.JSONField()

    def get(self, validated_data):
        result = celery_app.send_task(
            "word_suggestions"
        )
        return result
