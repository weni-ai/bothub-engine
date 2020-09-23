from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from bothub.api.v2.fields import EntityValueField, RepositoryVersionRelatedField
from bothub.api.v2.repository.validators import (
    EntityNotEqualGroupValidator,
    CanContributeInRepositoryVersionValidator,
)
from bothub.common.languages import LANGUAGE_CHOICES
from bothub.common.models import RepositoryExample, RepositoryVersion
from bothub.common.models import RepositoryExampleEntity


class RepositoryExampleEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryExampleEntity
        fields = [
            "id",
            "repository_example",
            "start",
            "end",
            "entity",
            "group",
            "created_at",
            "value",
        ]
        ref_name = None

    repository_example = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryExample.objects, help_text=_("Example's ID"), required=False
    )

    entity = EntityValueField()
    group = serializers.SerializerMethodField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(EntityNotEqualGroupValidator())

    def get_group(self, obj):
        if not obj.entity.group:
            return None
        return obj.entity.group.value

    def create(self, validated_data):
        repository_example = validated_data.pop("repository_example", None)
        assert repository_example
        example_entity = self.Meta.model.objects.create(
            repository_example=repository_example, **validated_data
        )
        return example_entity


class RepositoryExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryExample
        fields = [
            "id",
            "repository_version",
            "text",
            "intent",
            "language",
            "created_at",
            "entities",
            "translations",
        ]
        read_only_fields = ["translations"]
        ref_name = None

    entities = RepositoryExampleEntitySerializer(many=True, read_only=True)
    repository_version = RepositoryVersionRelatedField(
        source="repository_version_language",
        queryset=RepositoryVersion.objects,
        style={"show": False},
        required=False,
        validators=[CanContributeInRepositoryVersionValidator()],
    )
    intent = serializers.CharField(source="intent.text")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("context").get("request").method == "GET":
            self.fields["entities"] = RepositoryExampleEntitySerializer(
                many=True, read_only=True, data="GET"
            )


class RepositoriesSearchExamplesSerializer(serializers.Serializer):
    repositories = serializers.ListField(required=True)
    text = serializers.CharField(required=True)
    language = serializers.ChoiceField(LANGUAGE_CHOICES, required=True)
    exclude_intents = serializers.ListField(required=False)


class RepositoriesSearchExamplesResponseSerializer(serializers.Serializer):
    result = serializers.ListField(required=True)
