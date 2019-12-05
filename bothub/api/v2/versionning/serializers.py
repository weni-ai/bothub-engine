from rest_framework import serializers

from bothub.common.models import RepositoryUpdate, Repository


class RepositoryVersionSeralizer(serializers.ModelSerializer):
    class Meta:
        model = RepositoryUpdate
        fields = [
            "pk",
            "selected",
            "created_at"
        ]
        ref_name = None

        selected = serializers.BooleanField(default=True, read_only=True, required=False)

    def update(self, instance, validated_data):
        validated_data['selected'] = True
        RepositoryUpdate.objects.filter(
            repository=instance.repository,
            language=instance.language
        ).update(selected=False)
        return super().update(instance, validated_data)
