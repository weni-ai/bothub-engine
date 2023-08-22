from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from bothub.api.v2.fields import EntityValueField
from bothub.api.v2.translation.validators import (
    CanContributeInRepositoryExampleValidator,
)
from bothub.api.v2.translation.validators import (
    CanContributeInRepositoryTranslatedExampleValidator,
)
from bothub.api.v2.translation.validators import TranslatedExampleLanguageValidator
from bothub.common.languages import LANGUAGE_CHOICES
from bothub.common.models import RepositoryExample
from bothub.common.models import RepositoryTranslatedExample
from bothub.common.models import RepositoryTranslatedExampleEntity


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
        required=False,
    )
    entity = serializers.SerializerMethodField(required=False)
    value = serializers.SerializerMethodField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("data") == "POST":
            self.fields["entity"] = EntityValueField()

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
            "original_example_text",
            "is_trained"
        ]
        ref_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs["context"].get("request").stream:
            self.fields["entities"] = RepositoryTranslatedExampleEntitySeralizer(
                many=True, style={"text_field": "text"}, data="POST"
            )
        self.validators.append(TranslatedExampleLanguageValidator())

    original_example = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryExample.objects,
        validators=[CanContributeInRepositoryExampleValidator()],
        help_text=_("Example's ID"),
    )
    from_language = serializers.SerializerMethodField(required=False)
    language = serializers.ChoiceField(LANGUAGE_CHOICES, label=_("Language"))
    has_valid_entities = serializers.SerializerMethodField()
    entities = RepositoryTranslatedExampleEntitySeralizer(
        many=True, style={"text_field": "text"}
    )
    original_example_text = serializers.SerializerMethodField()
    is_trained = serializers.SerializerMethodField()

    def get_from_language(self, obj):
        return obj.original_example.repository_version_language.language

    def get_has_valid_entities(self, obj):
        return obj.has_valid_entities

    def get_original_example_text(self, obj):
        return obj.original_example.text

    def get_is_trained(self, obj):
        version_language = obj.original_example.repository_version_language
        return len(version_language.training_log) > 0 or (version_language.training_end_at is not None and version_language.faield_at is None) or (version_language.training_end_at is not None and version_language.failed_at is not None and version_language.training_end_at > version_language.failed_at)

    def create(self, validated_data):
        entities_data = validated_data.pop("entities")

        translated = self.Meta.model.objects.create(**validated_data)
        for entity_data in entities_data:
            RepositoryTranslatedExampleEntity.objects.create(
                repository_translated_example=translated, **entity_data
            )
        return translated

    def update(self, instance, validated_data):
        entities_data = validated_data.pop("entities")
        instance = super().update(instance, validated_data)
        RepositoryTranslatedExampleEntity.objects.filter(
            repository_translated_example=instance.pk
        ).delete()

        for entity_data in entities_data:
            RepositoryTranslatedExampleEntity.objects.create(
                repository_translated_example=instance, **entity_data
            )
        return instance


class RepositoryTranslatedExporterSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    language = serializers.ChoiceField(
        LANGUAGE_CHOICES, label=_("Language"), required=True
    )


class RepositoryTranslatedImportSerializer(serializers.Serializer):
    of_the_language = serializers.ChoiceField(
        LANGUAGE_CHOICES, label=_("Language"), required=True
    )
    for_the_language = serializers.ChoiceField(
        LANGUAGE_CHOICES, label=_("Language"), required=True
    )
    with_translation = serializers.BooleanField(default=True)
