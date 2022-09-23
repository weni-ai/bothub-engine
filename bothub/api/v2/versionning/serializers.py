from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from bothub.api.v2.repository.validators import CanContributeInRepositoryValidator
from bothub.api.v2.versionning.validators import (
    CanUseNameVersionValidator,
    VersionNameNotExistValidator,
)
from bothub.celery import app as celery_app
from bothub.common.models import RepositoryVersion, Repository


class RepositoryVersionSeralizer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryVersion
        fields = [
            "id",
            "repository",
            "name",
            "is_default",
            "created_at",
            "created_by",
            "last_update",
        ]
        ref_name = None

        read_only = ["is_default", "created_by", "last_update"]

    is_default = serializers.BooleanField(default=False, required=False)
    id = serializers.IntegerField()
    name = serializers.CharField(
        max_length=40, required=True, validators=[CanUseNameVersionValidator()]
    )
    repository = serializers.PrimaryKeyRelatedField(
        queryset=Repository.objects,
        validators=[CanContributeInRepositoryValidator()],
        write_only=True,
        style={"show": False},
    )
    created_by = serializers.CharField(source="created_by.name", read_only=True)
    last_update = serializers.DateTimeField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validators.append(VersionNameNotExistValidator())

    def update(self, instance, validated_data):
        validated_data.pop("repository")
        if validated_data.get("is_default"):
            validated_data["is_default"] = True
            RepositoryVersion.objects.filter(repository=instance.repository).update(
                is_default=False
            )
        return super().update(instance, validated_data)

    def create(self, validated_data):  # pragma: no cover
        id_clone = validated_data.pop("id")
        repository = validated_data.get("repository")
        name = validated_data.get("name")
        clone = get_object_or_404(RepositoryVersion, pk=id_clone, repository=repository)

        instance = self.Meta.model(
            name=name,
            last_update=clone.last_update,
            is_default=False,
            repository=clone.repository,
            created_by=self.context["request"].user,
            is_deleted=True,
        )
        instance.save()
        answer_task = celery_app.send_task(
            "clone_version", args=[repository.pk, id_clone, instance.pk]
        )
        answer_task.wait()
        return instance
