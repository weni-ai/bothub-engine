from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from bothub.api.v2.fields import EntityValueField, RepositoryVersionRelatedField
from bothub.api.v2.fields import GroupValueField
from bothub.api.v2.repository.validators import (
    EntityNotEqualGroupValidator,
    CanContributeInRepositoryVersionValidator,
)
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
    group = GroupValueField(allow_blank=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("data") == "GET":
            self.fields["group"] = serializers.SerializerMethodField(required=False)
        self.validators.append(EntityNotEqualGroupValidator())

    def get_group(self, obj):
        if not obj.entity.group:
            return None
        return obj.entity.group.value

    def create(self, validated_data):
        # TODO: Verificar
        repository_example = validated_data.pop("repository_example", None)
        assert repository_example
        # group = validated_data.pop("group", empty)
        example_entity = self.Meta.model.objects.create(
            repository_example=repository_example, **validated_data
        )
        # if group is not empty:
        #     example_entity.entity.set_label(group)
        #     example_entity.entity.save(update_fields=["label"])
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("context").get("request").method == "GET":
            self.fields["entities"] = RepositoryExampleEntitySerializer(
                many=True, read_only=True, data="GET"
            )
