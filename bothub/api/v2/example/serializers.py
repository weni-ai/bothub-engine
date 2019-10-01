from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.fields import empty

from bothub.api.v2.fields import EntityValueField
from bothub.api.v2.fields import LabelValueField
from bothub.api.v2.repository.validators import EntityNotEqualLabelValidator
from bothub.common.models import RepositoryExample
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
            "label",
            "created_at",
            "value",
        ]
        ref_name = None

    repository_example = serializers.PrimaryKeyRelatedField(
        queryset=RepositoryExample.objects, help_text=_("Example's ID"), required=False
    )

    entity = EntityValueField()
    label = LabelValueField(allow_blank=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get("data") == "GET":
            self.fields["label"] = serializers.SerializerMethodField(required=False)
        self.validators.append(EntityNotEqualLabelValidator())

    def get_label(self, obj):
        if not obj.entity.label:
            return None
        return obj.entity.label.value

    def create(self, validated_data):
        repository_example = validated_data.pop("repository_example", None)
        assert repository_example
        label = validated_data.pop("label", empty)
        example_entity = self.Meta.model.objects.create(
            repository_example=repository_example, **validated_data
        )
        if label is not empty:
            example_entity.entity.set_label(label)
            example_entity.entity.save(update_fields=["label"])
        return example_entity


class RepositoryExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryExample
        fields = [
            "id",
            "repository_update",
            "deleted_in",
            "text",
            "intent",
            "language",
            "created_at",
            "entities",
            "translations",
        ]
        read_only_fields = ["repository_update", "deleted_in", "translations"]
        ref_name = None

    entities = RepositoryExampleEntitySerializer(many=True, read_only=True)
