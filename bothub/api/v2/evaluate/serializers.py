import json
from decimal import Decimal, ROUND_DOWN

from django.core.paginator import Paginator
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import APIException

from bothub.api.v2.repository.validators import (
    CanContributeInRepositoryVersionValidator,
)
from bothub.common.models import Repository, RepositoryVersion
from bothub.common.models import RepositoryEvaluate
from bothub.common.models import RepositoryEvaluateEntity
from bothub.common.models import RepositoryEvaluateResult
from bothub.common.models import RepositoryEvaluateResultScore
from bothub.common.models import RepositoryEvaluateResultIntent
from bothub.common.models import RepositoryEvaluateResultEntity

from bothub.common.languages import LANGUAGE_CHOICES

from ..fields import EntityValueField, RepositoryVersionRelatedField
from .validators import ThereIsEntityValidator, ThereIsExistingSentenceValidator
from .validators import ThereIsIntentValidator


class RepositoryEvaluateEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryEvaluateEntity
        fields = ["entity", "start", "end"]
        ref_name = None

    entity = EntityValueField()


class RepositoryEvaluateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryEvaluate
        fields = [
            "id",
            "repository",
            "repository_version",
            "text",
            "language",
            "intent",
            "entities",
            "created_at",
        ]
        read_only_fields = ["created_at"]
        ref_name = None

    entities = RepositoryEvaluateEntitySerializer(many=True, required=False)

    repository = serializers.PrimaryKeyRelatedField(
        queryset=Repository.objects, write_only=True, required=True
    )

    language = serializers.ChoiceField(LANGUAGE_CHOICES, label=_("Language"))

    repository_version = RepositoryVersionRelatedField(
        source="repository_version_language",
        queryset=RepositoryVersion.objects,
        style={"show": False},
        required=True,
        validators=[CanContributeInRepositoryVersionValidator()],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(ThereIsEntityValidator())
        self.validators.append(ThereIsIntentValidator())
        self.validators.append(ThereIsExistingSentenceValidator())

    def create(self, validated_data):
        entities = validated_data.pop("entities")
        repository = validated_data.pop("repository")
        language = validated_data.pop("language")
        version_id = validated_data.get("repository_version_language")

        if version_id:
            repository_version_language = repository.get_specific_version_id(
                repository_version=version_id.pk, language=language or None
            )
            validated_data.pop("repository_version_language")
        else:
            repository_version_language = repository.current_version(language)

        validated_data.update(
            {"repository_version_language": repository_version_language}
        )
        evaluate = RepositoryEvaluate.objects.create(**validated_data)

        for entity in entities:
            RepositoryEvaluateEntity.objects.create(
                repository_evaluate=evaluate, **entity
            )

        return evaluate

    def update(self, instance, validated_data):
        repository = validated_data.pop("repository")
        language = validated_data.get("language", instance.language)
        instance.text = validated_data.get("text", instance.text)
        instance.intent = validated_data.get("intent", instance.intent)
        if not validated_data.get("repository_version_language"):  # pragma: no cover
            instance.repository_version_language = repository.current_version(language)
        instance.save()
        instance.delete_entities()

        for entity in validated_data.pop("entities"):
            RepositoryEvaluateEntity.objects.create(
                repository_evaluate=instance, **entity
            )

        return instance


class RepositoryEvaluateResultVersionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryEvaluateResult
        fields = ["id", "language", "created_at", "version"]
        ref_name = None

    language = serializers.SerializerMethodField()

    def get_language(self, obj):
        return obj.repository_version_language.language


class RepositoryEvaluateResultScore(serializers.ModelSerializer):
    class Meta:
        model = RepositoryEvaluateResultScore
        fields = ["precision", "f1_score", "accuracy", "recall", "support"]

    precision = serializers.SerializerMethodField()
    f1_score = serializers.SerializerMethodField()
    accuracy = serializers.SerializerMethodField()
    recall = serializers.SerializerMethodField()
    support = serializers.SerializerMethodField()

    def get_precision(self, obj):
        return obj.precision if obj.precision else 0

    def get_f1_score(self, obj):
        return obj.f1_score if obj.f1_score else 0

    def get_accuracy(self, obj):
        return obj.accuracy if obj.accuracy else 0

    def get_recall(self, obj):
        return obj.recall if obj.recall else 0

    def get_support(self, obj):
        return obj.support if obj.support else 0


class RepositoryEvaluateResultIntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryEvaluateResultIntent
        fields = ["intent", "score"]
        ref_name = None

    score = RepositoryEvaluateResultScore(read_only=True)


class RepositoryEvaluateResultEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryEvaluateResultEntity
        fields = ["entity", "score"]
        ref_name = None

    score = RepositoryEvaluateResultScore(read_only=True)
    entity = serializers.SerializerMethodField()

    def get_entity(self, obj):
        return obj.entity.value


class RepositoryEvaluateResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryEvaluateResult
        fields = [
            "id",
            "version",
            "repository_version",
            "created_at",
            "matrix_chart",
            "confidence_chart",
            "log",
            "intents_list",
            "entities_list",
            "intent_results",
            "entity_results",
            "cross_validation",
        ]
        ref_name = None

    log = serializers.SerializerMethodField()
    intents_list = serializers.SerializerMethodField()
    entities_list = serializers.SerializerMethodField()
    repository_version = serializers.SerializerMethodField()
    intent_results = RepositoryEvaluateResultScore(read_only=True)
    entity_results = RepositoryEvaluateResultScore(read_only=True)

    def get_intents_list(self, obj):
        return RepositoryEvaluateResultIntentSerializer(
            obj.evaluate_result_intent.all().exclude(intent__exact=""), many=True
        ).data

    def get_entities_list(self, obj):
        return RepositoryEvaluateResultEntitySerializer(
            obj.evaluate_result_entity.all(), many=True
        ).data

    def get_repository_version(self, obj):
        return {
            "id": obj.repository_version_language.repository_version.pk,
            "name": obj.repository_version_language.repository_version.name,
        }

    def get_log(self, obj):
        paginate_by = 10

        try:
            page = int(self.context.get("request").query_params.get("page_intent", 1))
        except ValueError:
            raise APIException(
                {"non_field_errors": ["page_intent requires the value to be integer"]},
                code=400,
            )
        intent = self.context.get("request").query_params.get("intent")
        min_confidence = self.context.get("request").query_params.get("min")
        max_confidence = self.context.get("request").query_params.get("max")

        def filter_intent(log, intent, min_confidence, max_confidence):
            if not intent and not min_confidence and not max_confidence:
                return log

            confidence = float(
                Decimal(log.get("intent_prediction").get("confidence")).quantize(
                    Decimal("0.00"), rounding=ROUND_DOWN
                )
            )

            has_intent = False

            if min_confidence and max_confidence:
                min_confidence = float(min_confidence) / 100
                max_confidence = float(max_confidence) / 100

                has_intent = (
                    True if min_confidence <= confidence <= max_confidence else False
                )

            if intent and log.get("intent") != intent:
                has_intent = False

            if has_intent:
                return log

        if len(obj.log) > 0:
            result_log = json.loads(obj.log)
            pagination = Paginator(tuple(result_log), paginate_by)

            results = filter(
                None,
                list(
                    map(
                        lambda log: filter_intent(
                            log, intent, min_confidence, max_confidence
                        ),
                        pagination.page(page).object_list,
                    )
                ),
            )

            return {
                "total_pages": pagination.num_pages,
                "current_page": page,
                "results": results,
            }

        return {"total_pages": 0, "current_page": 1, "results": []}
