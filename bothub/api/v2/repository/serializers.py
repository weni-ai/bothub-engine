import json

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from bothub import utils
from bothub.api.v2.example.serializers import RepositoryExampleEntitySerializer
from bothub.api.v2.fields import EntityText, RepositoryVersionRelatedField
from bothub.api.v2.fields import ModelMultipleChoiceField
from bothub.api.v2.fields import TextField
from bothub.common import languages
from bothub.common.languages import LANGUAGE_CHOICES
from bothub.common.models import (
    Repository,
    RepositoryVersion,
    RepositoryNLPLog,
    RepositoryEntity,
    RepositoryEvaluate,
    RepositoryExampleEntity,
)
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RepositoryCategory
from bothub.common.models import RepositoryEntityLabel
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryTranslatedExampleEntity
from bothub.common.models import RepositoryVote
from bothub.common.models import RequestRepositoryAuthorization
from .validators import APIExceptionCustom
from .validators import CanContributeInRepositoryExampleValidator
from .validators import CanContributeInRepositoryTranslatedExampleValidator
from .validators import CanContributeInRepositoryValidator
from .validators import CanContributeInRepositoryVersionValidator
from .validators import ExampleWithIntentOrEntityValidator


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


class RepositoryEntityLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryEntityLabel
        fields = ["repository", "value", "entities", "examples__count"]
        ref_name = None

    entities = serializers.SerializerMethodField()
    examples__count = serializers.SerializerMethodField()

    def get_entities(self, obj):
        entities = (
            obj.repository.other_entities()
            if obj.value == "other"
            else obj.entities.all()
        )
        return map(lambda e: e.value, entities)

    def get_examples__count(self, obj):
        if obj.value == "other":
            return (
                obj.repository.examples(exclude_deleted=True)
                .filter(entities__entity__in=obj.repository.other_entities())
                .count()
            )
        return obj.examples().count()


class IntentSerializer(serializers.Serializer):
    value = serializers.CharField()
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
        ]
        read_only = ["user", "user__nickname", "repository", "role", "created_at"]
        ref_name = None

    user__nickname = serializers.SlugRelatedField(
        source="user", slug_field="nickname", read_only=True
    )

    id_request_authorizations = serializers.SerializerMethodField()

    def get_id_request_authorizations(self, obj):
        id_auth = RequestRepositoryAuthorization.objects.filter(
            repository=obj.repository, user=obj.user
        )
        if id_auth.count() == 1:
            return id_auth.first().pk
        return None


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
            "labels_list",
            "ready_for_train",
            "requirements_to_train",
            "created_at",
            "language",
            "owner",
            "categories",
            "categories_list",
            "intents",
            "intents_list",
            "labels",
            "other_label",
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
        ]
        read_only = [
            "uuid",
            "available_languages",
            "available_languages_count",
            "languages_warnings_count",
            "entities",
            "entities_list",
            "evaluate_languages_count",
            "labels_list",
            "ready_for_train",
            "created_at",
            "authorization",
            "nlp_server",
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
    labels_list = serializers.SerializerMethodField(style={"show": False})
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
    labels = serializers.SerializerMethodField(style={"show": False})
    other_label = serializers.SerializerMethodField(style={"show": False})
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
        default=Repository.ALGORITHM_NEURAL_NETWORK_INTERNAL,
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
            obj.repository.current_entities(
                queryset=queryset, version_default=obj.is_default
            )
            .values("value", "id")
            .distinct()
        )

    def get_labels_list(self, obj):
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )
        return (
            obj.repository.labels.filter(
                entities__value__in=obj.repository.entities_list(
                    queryset=queryset, version_default=obj.is_default
                )
            )
            .distinct()
            .values_list("value", flat=True)
            .distinct()
        )

    def get_ready_for_train(self, obj):
        # TODO: Verificar se realmente está funcionando
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )
        return obj.repository.ready_for_train(
            queryset=queryset, repository_version=obj.pk
        )

    def get_requirements_to_train(self, obj):
        # TODO: Verificar se realmente está funcionando
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )
        return dict(
            filter(
                lambda l: l[1],
                map(
                    lambda u: (u.language, u.requirements_to_train),
                    obj.repository.current_versions(
                        queryset=queryset, repository_version=obj.pk
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
                    "value": intent,
                    "examples__count": obj.repository.examples(
                        queryset=queryset, version_default=obj.is_default
                    )
                    .filter(intent=intent)
                    .count(),
                },
                obj.repository.intents(
                    queryset=queryset, version_default=obj.is_default
                ),
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

    def get_labels(self, obj):
        # RepositoryEntityLabelSerializer # TODO: DELETAR SERIALIZER
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )

        # TODO: remover antigo repository-info e apagar a @property
        current_labels = obj.repository.labels.filter(
            entities__value__in=obj.repository.entities_list(
                queryset=queryset, version_default=obj.is_default
            )
        ).distinct()

        return list(
            map(
                lambda label: {
                    "repository": label.repository.pk,
                    "value": label.value,
                    "entities": list(
                        map(
                            lambda e: e.value,
                            label.repository.other_entities(
                                queryset=queryset, version_default=obj.is_default
                            )
                            if label.value == "other"
                            else label.entities.all(),
                        )
                    ),
                    "examples__count": (
                        label.repository.examples(
                            queryset=queryset, version_default=obj.is_default
                        )
                        .filter(entities__entity__in=label.repository.other_entities())
                        .count()
                    )
                    if label.value == "other"
                    else label.examples(
                        queryset=queryset, version_default=obj.is_default
                    ).count(),
                },
                current_labels,
            )
        )

    def get_other_label(self, obj):
        # RepositoryEntityLabelSerializer # TODO: DELETAR SERIALIZER
        queryset = RepositoryExample.objects.filter(
            repository_version_language__repository_version=obj
        )

        label = obj.repository.other_entities(
            queryset=queryset, version_default=obj.is_default
        )

        return {
            "repository": obj.repository.pk,
            "value": "other",
            "entities": list(map(lambda e: e.value, label)),
            "examples__count": (
                obj.repository.examples(
                    queryset=queryset, version_default=obj.is_default
                )
                .filter(entities__entity__in=label)
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
        return RepositoryAuthorizationSerializer(
            obj.repository.get_user_authorization(request.user)
        ).data

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
        try:
            RequestRepositoryAuthorization.objects.get(
                user=request.user, repository=obj.repository
            )
            return False
        except RequestRepositoryAuthorization.DoesNotExist:
            return True

    def get_languages_warnings(self, obj):
        # TODO: deletar languages_warnings em model
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


class RepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Repository
        fields = [
            "uuid",
            "name",
            "slug",
            "description",
            "is_private",
            "available_languages",
            "available_languages_count",
            "entities",
            "entities_list",
            "labels_list",
            "ready_for_train",
            "created_at",
            "requirements_to_train",
            "language",
            "owner",
            "owner__nickname",
            "categories",
            "categories_list",
            "intents",
            "intents_list",
            "labels",
            "other_label",
            "examples__count",
            "evaluate_languages_count",
            "absolute_url",
            "authorization",
            "ready_for_train",
            "request_authorization",
            "available_request_authorization",
            "languages_warnings",
            "languages_warnings_count",
            "algorithm",
            "use_language_model_featurizer",
            "use_competing_intents",
            "use_name_entities",
            "use_analyze_char",
            "nlp_server",
            "version_default",
        ]
        read_only = [
            "uuid",
            "available_languages",
            "available_languages_count",
            "languages_warnings_count",
            "entities",
            "entities_list",
            "evaluate_languages_count",
            "labels_list",
            "ready_for_train",
            "created_at",
            "authorization",
            "nlp_server",
        ]
        ref_name = None

    uuid = serializers.UUIDField(style={"show": False}, read_only=True)
    slug = serializers.SlugField(style={"show": False}, read_only=True)
    is_private = serializers.BooleanField(
        style={"show": False}, read_only=True, default=False
    )
    algorithm = serializers.ChoiceField(
        style={"show": False, "only_settings": True},
        choices=Repository.ALGORITHM_CHOICES,
        default=Repository.ALGORITHM_NEURAL_NETWORK_INTERNAL,
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
    available_languages = serializers.ReadOnlyField(style={"show": False})
    available_languages_count = serializers.SerializerMethodField(style={"show": False})
    entities_list = serializers.ReadOnlyField(style={"show": False})
    labels_list = serializers.ReadOnlyField(style={"show": False})
    ready_for_train = serializers.SerializerMethodField(style={"show": False})
    created_at = serializers.DateTimeField(style={"show": False}, read_only=True)
    requirements_to_train = serializers.ReadOnlyField(style={"show": False})
    languages_warnings = serializers.ReadOnlyField(style={"show": False})
    languages_warnings_count = serializers.SerializerMethodField(style={"show": False})
    use_language_model_featurizer = serializers.ReadOnlyField(style={"show": False})

    language = serializers.ChoiceField(LANGUAGE_CHOICES, label=_("Language"))
    owner = serializers.PrimaryKeyRelatedField(read_only=True, style={"show": False})
    owner__nickname = serializers.SlugRelatedField(
        source="owner", slug_field="nickname", read_only=True, style={"show": False}
    )
    intents = serializers.SerializerMethodField(style={"show": False})
    intents_list = serializers.SerializerMethodField(style={"show": False})
    categories = ModelMultipleChoiceField(
        child_relation=serializers.PrimaryKeyRelatedField(
            queryset=RepositoryCategory.objects.all()
        ),
        allow_empty=False,
        help_text=Repository.CATEGORIES_HELP_TEXT,
        label=_("Categories"),
    )
    categories_list = serializers.SerializerMethodField(style={"show": False})
    labels = RepositoryEntityLabelSerializer(
        source="current_labels", many=True, read_only=True, style={"show": False}
    )
    other_label = serializers.SerializerMethodField(style={"show": False})
    examples__count = serializers.SerializerMethodField(style={"show": False})
    evaluate_languages_count = serializers.SerializerMethodField(style={"show": False})
    absolute_url = serializers.SerializerMethodField(style={"show": False})
    authorization = serializers.SerializerMethodField(style={"show": False})
    request_authorization = serializers.SerializerMethodField(style={"show": False})
    available_request_authorization = serializers.SerializerMethodField(
        style={"show": False}
    )
    entities = serializers.SerializerMethodField(style={"show": False})
    nlp_server = serializers.SerializerMethodField(style={"show": False})
    version_default = serializers.SerializerMethodField(style={"show": False})

    def get_ready_for_train(self, obj):
        context = self.context.get("request")
        if context:
            repository_version = context.query_params.get("repository_version")
            queryset = RepositoryExample.objects.filter(
                repository_version_language__repository_version__pk=repository_version
            )
            if repository_version:
                if queryset.filter(
                    repository_version_language__repository_version__repository=obj
                ):
                    return obj.ready_for_train(queryset=queryset, version_default=False)
        return obj.ready_for_train()

    def get_version_default(self, obj):
        return {
            "id": obj.current_version().repository_version.pk,
            "name": obj.current_version().repository_version.name,
        }

    def get_categories_list(self, obj):
        return RepositoryCategorySerializer(obj.categories, many=True).data

    def get_nlp_server(self, obj):
        if obj.nlp_server:
            return obj.nlp_server
        return settings.BOTHUB_NLP_BASE_URL

    def create(self, validated_data):
        validated_data.update({"owner": self.context["request"].user})
        validated_data.update(
            {"slug": utils.unique_slug_generator(validated_data, Repository)}
        )

        repository = super().create(validated_data)

        repository.versions.create(
            is_default=True, created_by=self.context["request"].user
        )

        return repository

    def update(self, instance, validated_data):
        if validated_data.get("algorithm") in [
            Repository.ALGORITHM_TRANSFORMER_NETWORK_DIET,
            Repository.ALGORITHM_TRANSFORMER_NETWORK_DIET_WORD_EMBEDDING,
        ]:
            raise PermissionDenied(
                _(
                    f"The algorithm {validated_data.get('algorithm')} is not available at this "
                    f"time, please try again later"
                )
            )
        return super().update(instance, validated_data)

    def get_entities(self, obj):
        return obj.current_entities().values("value", "id").distinct()

    def get_intents(self, obj):
        context = self.context.get("request")
        if context:
            repository_version = context.query_params.get("repository_version")
            queryset = RepositoryExample.objects.filter(
                repository_version_language__repository_version__pk=repository_version
            )
            if repository_version:
                if queryset.filter(
                    repository_version_language__repository_version__repository=obj
                ):
                    return IntentSerializer(
                        map(
                            lambda intent: {
                                "value": intent,
                                "examples__count": obj.examples(
                                    exclude_deleted=True,
                                    queryset=queryset,
                                    version_default=False,
                                )
                                .filter(intent=intent)
                                .count(),
                            },
                            obj.intents(queryset=queryset, version_default=False),
                        ),
                        many=True,
                    ).data
                return []

        return IntentSerializer(
            map(
                lambda intent: {
                    "value": intent,
                    "examples__count": obj.examples(exclude_deleted=True)
                    .filter(intent=intent)
                    .count(),
                },
                obj.intents(),
            ),
            many=True,
        ).data

    def get_intents_list(self, obj):
        context = self.context.get("request")
        if context:
            repository_version = context.query_params.get("repository_version")
            queryset = RepositoryExample.objects.filter(
                repository_version_language__repository_version__pk=repository_version
            )
            if repository_version:
                if queryset.filter(
                    repository_version_language__repository_version__repository=obj
                ):
                    return obj.intents(queryset=queryset, version_default=False)
                return []
        return obj.intents()

    def get_other_label(self, obj):
        return RepositoryEntityLabelSerializer(
            RepositoryEntityLabel(repository=obj, value="other")
        ).data

    def get_examples__count(self, obj):
        context = self.context.get("request")
        if context:
            repository_version = context.query_params.get("repository_version")
            queryset = RepositoryExample.objects.filter(
                repository_version_language__repository_version__pk=repository_version
            )
            if repository_version:
                if queryset.filter(
                    repository_version_language__repository_version__repository=obj
                ):
                    return obj.examples(
                        exclude_deleted=True, queryset=queryset, version_default=False
                    ).count()
                return 0
        return obj.examples().count()

    def get_available_languages_count(self, obj):
        context = self.context.get("request")
        if context:
            repository_version = context.query_params.get("repository_version")
            queryset = RepositoryExample.objects.filter(
                repository_version_language__repository_version__pk=repository_version
            )
            if repository_version:
                if queryset.filter(
                    repository_version_language__repository_version__repository=obj
                ):
                    return len(
                        obj.available_languages(
                            queryset=queryset, version_default=False
                        )
                    )
                return 0
        return len(obj.available_languages())

    def get_languages_warnings_count(self, obj):
        context = self.context.get("request")
        if context:
            repository_version = context.query_params.get("repository_version")
            queryset = RepositoryExample.objects.filter(
                repository_version_language__repository_version__pk=repository_version
            )
            if repository_version:
                if queryset.filter(
                    repository_version_language__repository_version__repository=obj
                ):
                    return len(
                        obj.languages_warnings(queryset=queryset, version_default=False)
                    )
                return 0
        return len(obj.languages_warnings())

    def get_evaluate_languages_count(self, obj):
        return dict(
            map(
                lambda x: (x, obj.evaluations(language=x).count()),
                obj.available_languages(),
            )
        )

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()

    def get_authorization(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        return RepositoryAuthorizationSerializer(
            obj.get_user_authorization(request.user)
        ).data

    def get_request_authorization(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        try:
            request_authorization = RequestRepositoryAuthorization.objects.get(
                user=request.user, repository=obj
            )
            return RequestRepositoryAuthorizationSerializer(request_authorization).data
        except RequestRepositoryAuthorization.DoesNotExist:
            return None

    def get_available_request_authorization(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        authorization = obj.get_user_authorization(request.user)
        if authorization.role is not RepositoryAuthorization.ROLE_NOT_SETTED:
            return False
        if authorization.is_owner:
            return False
        try:
            RequestRepositoryAuthorization.objects.get(
                user=request.user, repository=obj
            )
            return False
        except RequestRepositoryAuthorization.DoesNotExist:
            return True


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
        many=True, style={"text_field": "text"}, required=False
    )
    translations = RepositoryTranslatedExampleSerializer(many=True, read_only=True)
    repository_version = RepositoryVersionRelatedField(
        source="repository_version_language",
        queryset=RepositoryVersion.objects,
        style={"show": False},
        required=False,
        validators=[CanContributeInRepositoryVersionValidator()],
    )

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
                intent=validated_data.get("intent"),
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
                intent=validated_data.get("intent"),
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
        validated_data.pop("language")

        instance_update = super().update(instance, validated_data)

        RepositoryExampleEntity.objects.filter(repository_example=instance.pk).delete()

        for entity_data in entities_data:
            entity_data.update({"repository_example": instance.pk})
            entity_serializer = RepositoryExampleEntitySerializer(data=entity_data)
            entity_serializer.is_valid(raise_exception=True)
            entity_serializer.save()
        return instance_update


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
        fields = ["repository", "value", "label"]
        ref_name = None

    label = serializers.SerializerMethodField()

    def get_label(self, obj):
        if not obj.label:
            return None
        return obj.label.value


class RasaUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    language = serializers.ChoiceField(LANGUAGE_CHOICES, label=_("Language"))


class ObjectRasaSerializer(serializers.Serializer):
    regex_features = serializers.ListField(required=True)
    entity_synonyms = serializers.ListField(required=True)
    common_examples = serializers.ListField(required=True)


class RasaSerializer(serializers.Serializer):
    rasa_nlu_data = ObjectRasaSerializer()
