from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from bothub.api.v2.translation.serializers import RepositoryTranslatedExampleSerializer
from bothub.api.v2.translator.validators import (
    CanContributeInRepositoryExampleTranslatorValidator,
)
from bothub.common.languages import LANGUAGE_CHOICES
from bothub.common.models import RepositoryExample, RepositoryTranslatedExampleEntity


class RepositoryTranslatedExampleTranslatorSerializer(
    RepositoryTranslatedExampleSerializer
):
    original_example = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryExample.objects,
        validators=[CanContributeInRepositoryExampleTranslatorValidator()],
        help_text=_("Example's ID"),
    )
    language = serializers.ChoiceField(
        LANGUAGE_CHOICES, label=_("Language"), read_only=True
    )

    def create(self, validated_data):
        validated_data.update(
            {
                "language": self.context.get(
                    "request"
                ).auth.repository_version_language.language
            }
        )
        entities_data = validated_data.pop("entities")

        translated = self.Meta.model.objects.create(**validated_data)

        for entity_data in entities_data:
            RepositoryTranslatedExampleEntity.objects.create(
                repository_translated_example=translated, **entity_data
            )
        return translated
