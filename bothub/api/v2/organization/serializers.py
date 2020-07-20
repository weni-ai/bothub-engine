from rest_framework import serializers

from bothub.common.models import Organization, OrganizationAuthorization


class OrganizationSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "nickname", "description", "verificated"]
        ref_name = None

    read_only = ["id", "verificated"]

    id = serializers.PrimaryKeyRelatedField(style={"show": False}, read_only=True)
    name = serializers.CharField(max_length=40, required=True)
    nickname = serializers.SlugField(read_only=True, style={"show": False})
    verificated = serializers.BooleanField(style={"show": False}, read_only=True)

    def create(self, validated_data):
        instance = super().create(validated_data)

        OrganizationAuthorization.objects.create(
            user=self.context.get("request").user,
            organization=instance,
            role=OrganizationAuthorization.ROLE_ADMIN,
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
            "organization__nickname",
            "role",
            "level",
            "can_read",
            "can_contribute",
            "can_write",
            "can_translate",
            "is_admin",
            "created_at",
            "user__is_organization",
        ]
        read_only = [
            "user",
            "user__nickname",
            "organization",
            "organization__nickname",
            "role",
            "created_at",
        ]
        ref_name = None

    user__nickname = serializers.SlugRelatedField(
        source="user", slug_field="nickname", read_only=True
    )
    organization__nickname = serializers.SlugRelatedField(
        source="organization", slug_field="nickname", read_only=True
    )
    user__is_organization = serializers.SlugRelatedField(
        source="user", slug_field="is_organization", read_only=True
    )
