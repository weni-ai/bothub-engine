from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from bothub.api.v2.fields import RepositoryVersionRelatedField
from bothub.api.v2.repository.validators import (
    CanContributeInRepositoryVersionValidator,
)
from bothub.api.v2.translation.serializers import RepositoryTranslatedExampleSerializer
from bothub.api.v2.translator.validators import (
    CanContributeInRepositoryExampleTranslatorValidator,
)
from bothub.common import languages
from bothub.common.languages import LANGUAGE_CHOICES
from bothub.common.models import (
    RepositoryExample,
    RepositoryTranslator,
    RepositoryVersion,
)


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
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.update(
            {
                "language": self.context.get(
                    "request"
                ).auth.repository_version_language.language
            }
        )
        return super().update(instance, validated_data)


class RepositoryTranslatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryTranslator
        fields = [
            "uuid",
            "language",
            "repository_version",
            "repository_version__name",
            "created_by",
        ]
        read_only_fields = []
        ref_name = None

    uuid = serializers.UUIDField(style={"show": False}, read_only=True)
    repository_version = RepositoryVersionRelatedField(
        source="repository_version_language",
        queryset=RepositoryVersion.objects,
        style={"show": False},
        required=True,
        validators=[CanContributeInRepositoryVersionValidator()],
    )
    repository_version__name = serializers.CharField(
        read_only=True, source="repository_version_language.repository_version.name"
    )
    language = serializers.ChoiceField(languages.LANGUAGE_CHOICES, required=True)
    created_by = serializers.PrimaryKeyRelatedField(
        read_only=True, style={"show": False}, required=False
    )

    def create(self, validated_data):
        language = validated_data.get("language")
        repository_version = validated_data.pop("repository_version_language")

        validated_data.update(
            {
                "repository_version_language": repository_version.get_version_language(
                    language=language
                )
            }
        )
        validated_data.update({"created_by": self.context["request"].user})

        return super().create(validated_data)
