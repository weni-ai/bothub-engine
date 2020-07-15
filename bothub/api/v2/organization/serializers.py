from rest_framework import serializers

from bothub.common.models import (
    Organization,
)


class OrganizationSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "nickname",
            "description",
        ]
        ref_name = None

        read_only = []

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=40, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
