from django.utils.translation import gettext as _
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from bothub.api.v2.examples.serializers import RepositoryExampleEntitySerializer
from bothub.api.v2.fields import TextField
from bothub.api.v2.fields import EntityText
from bothub.api.v2.repository.validators import (
    CanContributeInRepositoryExampleValidator,
)
from bothub.api.v2.repository.validators import IntentAndSentenceNotExistsValidator
from bothub.api.v2.repository.validators import ExampleWithIntentOrEntityValidator
from bothub.api.v2.repository.validators import CanContributeInRepositoryValidator
from bothub.common import languages
from bothub.common.models import (
    Repository,
    UserGroupRepository,
    UserPermissionRepository,
    PermissionsCode,
)
from bothub.common.models import RepositoryVote
from bothub.common.models import RepositoryCategory
from bothub.common.models import RepositoryEntityLabel
from bothub.common.models import RepositoryAuthorization
from bothub.common.models import RequestRepositoryAuthorization
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryTranslatedExampleEntity
from bothub.common.models import RepositoryUpdate
from bothub.common.languages import LANGUAGE_CHOICES
from .validators import CanContributeInRepositoryTranslatedExampleValidator


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
        source="user", slug_field="nickname", read_only=True
    )
    approved_by__nickname = serializers.SlugRelatedField(
        source="approved_by", slug_field="nickname", read_only=True
    )
    approved_by = serializers.PrimaryKeyRelatedField(
        read_only=True, style={"show": False}
    )

    def update(self, instance, validated_data):
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
            obj.repository.other_entities
            if obj.value == "other"
            else obj.entities.all()
        )
        return map(lambda e: e.value, entities)

    def get_examples__count(self, obj):
        if obj.value == "other":
            return (
                obj.repository.examples(exclude_deleted=True)
                .filter(entities__entity__in=obj.repository.other_entities)
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
            "is_admin",
            "created_at",
        ]
        read_only = ["user", "user__nickname", "repository", "role", "created_at"]
        ref_name = None

    user__nickname = serializers.SlugRelatedField(
        source="user", slug_field="nickname", read_only=True
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
            "available_languages",
            "entities",
            "entities_list",
            "labels_list",
            "ready_for_train",
            "created_at",
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
            "requirements_to_train",
            "languages_ready_for_train",
            "request_authorization",
            "available_request_authorization",
            "languages_warnings",
            "algorithm",
            "use_language_model_featurizer",
            "use_competing_intents",
            "use_name_entities",
            "nlp_server",
        ]
        read_only = [
            "uuid",
            "available_languages",
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

    language = serializers.ChoiceField(
        LANGUAGE_CHOICES, label=Repository._meta.get_field("language").verbose_name
    )
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    owner__nickname = serializers.SlugRelatedField(
        source="owner", slug_field="nickname", read_only=True
    )
    intents = serializers.SerializerMethodField()
    intents_list = serializers.SerializerMethodField()
    categories = RepositoryCategorySerializer(many=True, read_only=True)
    categories_list = serializers.SlugRelatedField(
        source="categories", slug_field="name", many=True, read_only=True
    )
    labels = RepositoryEntityLabelSerializer(
        source="current_labels", many=True, read_only=True
    )
    other_label = serializers.SerializerMethodField()
    examples__count = serializers.SerializerMethodField()
    evaluate_languages_count = serializers.SerializerMethodField()
    absolute_url = serializers.SerializerMethodField()
    authorization = serializers.SerializerMethodField()
    request_authorization = serializers.SerializerMethodField()
    available_request_authorization = serializers.SerializerMethodField()
    entities = serializers.SerializerMethodField()
    nlp_server = serializers.SerializerMethodField()

    def get_nlp_server(self, obj):
        if obj.nlp_server:
            return obj.nlp_server
        return settings.BOTHUB_NLP_BASE_URL

    def create(self, validated_data):
        validated_data.update({"owner": self.context["request"].user})
        return super().create(validated_data)

    def get_entities(self, obj):
        return obj.current_entities.values("value", "id").distinct()

    def get_intents(self, obj):
        return IntentSerializer(
            map(
                lambda intent: {
                    "value": intent,
                    "examples__count": obj.examples(exclude_deleted=True)
                    .filter(intent=intent)
                    .count(),
                },
                obj.intents,
            ),
            many=True,
        ).data

    def get_intents_list(self, obj):
        return obj.intents

    def get_other_label(self, obj):
        return RepositoryEntityLabelSerializer(
            RepositoryEntityLabel(repository=obj, value="other")
        ).data

    def get_examples__count(self, obj):
        return obj.examples().count()

    def get_evaluate_languages_count(self, obj):
        return dict(
            map(
                lambda x: (x, obj.evaluations(language=x).count()),
                obj.available_languages,
            )
        )

    def get_absolute_url(self, obj):
        return obj.get_absolute_url()

    def get_authorization(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        return RepositoryAuthorizationSerializer(
            obj.get_user_authorization(request.user, return_group='Owner')
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
        return obj.original_example.repository_update.language

    def get_has_valid_entities(self, obj):
        return obj.has_valid_entities


class RepositoryExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryExample
        fields = [
            "id",
            "repository",
            "repository_update",
            "deleted_in",
            "text",
            "intent",
            "language",
            "created_at",
            "entities",
            "translations",
        ]
        read_only_fields = ["deleted_in"]
        ref_name = None

    id = serializers.PrimaryKeyRelatedField(read_only=True, style={"show": False})
    text = EntityText(style={"entities_field": "entities"}, required=False)
    repository = serializers.PrimaryKeyRelatedField(
        queryset=Repository.objects,
        validators=[CanContributeInRepositoryValidator()],
        write_only=True,
        style={"show": False},
    )
    repository_update = serializers.PrimaryKeyRelatedField(
        read_only=True, style={"show": False}, required=False
    )
    language = serializers.ChoiceField(
        languages.LANGUAGE_CHOICES, allow_blank=True, required=False
    )

    entities = RepositoryExampleEntitySerializer(
        many=True, style={"text_field": "text"}, required=False
    )
    translations = RepositoryTranslatedExampleSerializer(many=True, read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs["context"].get("request").stream is None:
            self.fields["entities"] = RepositoryExampleEntitySerializer(
                many=True, style={"text_field": "text"}, data="GET"
            )
        self.validators.append(ExampleWithIntentOrEntityValidator())
        self.validators.append(IntentAndSentenceNotExistsValidator())

    def create(self, validated_data):
        entities_data = validated_data.pop("entities")
        repository = validated_data.pop("repository")

        try:
            language = validated_data.pop("language")
        except KeyError:
            language = None
        repository_update = repository.current_update(language or None)
        validated_data.update({"repository_update": repository_update})
        example = self.Meta.model.objects.create(**validated_data)
        for entity_data in entities_data:
            entity_data.update({"repository_example": example.pk})
            entity_serializer = RepositoryExampleEntitySerializer(data=entity_data)
            entity_serializer.is_valid(raise_exception=True)
            entity_serializer.save()
        return example


class AnalyzeTextSerializer(serializers.Serializer):
    language = serializers.ChoiceField(LANGUAGE_CHOICES, required=True)
    text = serializers.CharField(allow_blank=False)


class EvaluateSerializer(serializers.Serializer):
    language = serializers.ChoiceField(LANGUAGE_CHOICES, required=True)


class RepositoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryUpdate
        fields = [
            "id",
            "repository",
            "language",
            "created_at",
            "by",
            "by__nickname",
            "training_started_at",
            "trained_at",
            "failed_at",
        ]
        ref_name = None

    by__nickname = serializers.SlugRelatedField(
        source="by", slug_field="nickname", read_only=True
    )


class RepositoryUpload(serializers.Serializer):
    pass
