from rest_framework import serializers

from bothub.common.models import (
    Organization, OrganizationAuthorization,
)


class OrganizationSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "nickname",
            "description",
            "verificated",
        ]
        ref_name = None

        read_only = []

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=40, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        instance = super().create(validated_data)

        OrganizationAuthorization.objects.create(
            user=self.context.get("request").user,
            organization=instance,
            role=OrganizationAuthorization.ROLE_ADMIN
        )

        return instance


class OrganizationAuthorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationAuthorization
        fields = [
            "uuid",
            "user",
            "user__nickname",
            "organization",
            "role",
            "can_read",
            "can_contribute",
            "can_write",
            "can_translate",
            "is_admin",
            "created_at",
        ]
        read_only = ["user", "user__nickname", "organization", "role", "created_at"]
        ref_name = None

    user__nickname = serializers.SlugRelatedField(
        source="user", slug_field="nickname", read_only=True
    )
