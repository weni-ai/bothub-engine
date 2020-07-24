from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import PermissionDenied

from bothub.common.models import Organization, OrganizationAuthorization


class OrganizationSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "nickname",
            "description",
            "verificated",
            "count_repositories",
            "count_members",
        ]
        ref_name = None

    read_only = ["id", "verificated"]

    id = serializers.PrimaryKeyRelatedField(style={"show": False}, read_only=True)
    name = serializers.CharField(max_length=40, required=True)
    nickname = serializers.SlugField(required=True)
    verificated = serializers.BooleanField(style={"show": False}, read_only=True)
    count_repositories = serializers.SerializerMethodField(style={"show": False})
    count_members = serializers.SerializerMethodField(style={"show": False})

    def create(self, validated_data):
        instance = super().create(validated_data)

        OrganizationAuthorization.objects.create(
            user=self.context.get("request").user,
            organization=instance,
            role=OrganizationAuthorization.ROLE_ADMIN,
        )

        return instance

    def get_count_repositories(self, obj):
        return obj.repository_owner.repositories.count()

    def get_count_members(self, obj):
        auths = OrganizationAuthorization.objects.filter(organization=obj).exclude(
            role=OrganizationAuthorization.LEVEL_NOTHING
        )
        return auths.count()


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


class OrganizationAuthorizationRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationAuthorization
        fields = ["role"]
        ref_name = None

    def validate(self, data):
        if data.get("role") == OrganizationAuthorization.LEVEL_NOTHING:
            raise PermissionDenied(_("You cannot set user role 0"))
        return data
