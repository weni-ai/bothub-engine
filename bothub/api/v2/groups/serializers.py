from rest_framework import serializers

from bothub.api.v2.repository.validators import CanContributeInRepositoryValidator
from bothub.common.models import RepositoryEntityGroup, Repository


class RepositoryEntityGroupSeralizer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryEntityGroup
        fields = ["id", "value", "created_at", "repository", "repository_version"]
        ref_name = None

        read_only = ["id", "created_at"]

    repository = serializers.PrimaryKeyRelatedField(
        queryset=Repository.objects,
        write_only=True,
        required=True,
        validators=[CanContributeInRepositoryValidator()],
    )

    def create(self, validated_data):
        validated_data.pop("repository")
        return super().create(validated_data)
